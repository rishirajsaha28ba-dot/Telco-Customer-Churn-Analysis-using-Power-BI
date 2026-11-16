#!/usr/bin/env python3
"""Live Twitch clipper.

Follows the steps from the reel:
  1. Record the live stream            (Streamlink -> FFmpeg 10 s segments)
  2. Count Twitch chat every 10 s      (anonymous, read-only IRC)
  3. Detect a chat spike               (current 10 s bucket vs. rolling baseline)
  4. Cut the last clip from the buffer (FFmpeg)
  5. Caption it with Whisper           (optional, --captions)
  6. Save a 9:16 vertical clip         (1080x1920 MP4)

Usage:
  python clipper.py live --channel SOMECHANNEL [--captions]
  python clipper.py live --file local_stream.mp4 --channel test   # replay a local file as "live"
  python clipper.py cut  --input video.mp4 --at 25 [--captions]   # clip one moment from a file
"""
import argparse
import collections
import glob
import os
import random
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime

BUCKET_SECONDS = 10      # chat is counted in 10 s buckets (as in the reel)
SEGMENT_SECONDS = 10     # recorder writes 10 s .ts segments
BUFFER_SEGMENTS = 60     # keep ~10 minutes of video on disk
CLIP_SECONDS = 30        # clip length (as in the reel)
OUT_DIR = "clips"


# ---------- Step 3: spike detection -------------------------------------------------
class SpikeDetector:
    """Fires when a 10 s bucket is much busier than the recent average."""

    def __init__(self, window=12, factor=3.0, min_msgs=15, cooldown=60):
        self.history = collections.deque(maxlen=window)
        self.factor = factor
        self.min_msgs = min_msgs
        self.cooldown = cooldown
        self.last_fire = None

    def add_bucket(self, count, t):
        """Feed one bucket (message count, timestamp in seconds). Returns True on a spike."""
        baseline = sum(self.history) / len(self.history) if self.history else 0
        self.history.append(count)
        if count < self.min_msgs or count < self.factor * max(baseline, 1):
            return False
        if self.last_fire is not None and t - self.last_fire < self.cooldown:
            return False
        self.last_fire = t
        return True


# ---------- Step 2: read-only Twitch chat -------------------------------------------
def read_chat(channel, on_message, stop):
    """Joins chat anonymously (justinfan login, read-only) and calls on_message per chat line."""
    nick = f"justinfan{random.randint(10000, 99999)}"
    sock = socket.create_connection(("irc.chat.twitch.tv", 6667), timeout=30)
    sock.sendall(f"NICK {nick}\r\nJOIN #{channel.lower()}\r\n".encode())
    buf = b""
    while not stop.is_set():
        try:
            data = sock.recv(4096)
        except socket.timeout:
            continue
        if not data:
            break
        buf += data
        while b"\r\n" in buf:
            line, buf = buf.split(b"\r\n", 1)
            text = line.decode("utf-8", "replace")
            if text.startswith("PING"):
                sock.sendall(b"PONG :tmi.twitch.tv\r\n")
            elif " PRIVMSG " in text:
                on_message()
    sock.close()


# ---------- Step 1: record the stream into a rolling buffer --------------------------
def start_recorder(buf_dir, channel=None, file=None):
    """Streamlink (or a local file, played in real time) -> FFmpeg segmenter."""
    if file:
        src = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-re", "-i", file, "-c", "copy", "-f", "mpegts", "pipe:1"],
            stdout=subprocess.PIPE)
    else:
        src = subprocess.Popen(
            ["streamlink", "--stdout", "--twitch-disable-ads",
             f"https://twitch.tv/{channel}", "best"],
            stdout=subprocess.PIPE)
    seg = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-i", "pipe:0", "-c", "copy",
         "-f", "segment", "-segment_time", str(SEGMENT_SECONDS),
         "-reset_timestamps", "1", "-segment_format", "mpegts",
         os.path.join(buf_dir, "seg_%05d.ts")],
        stdin=src.stdout)
    src.stdout.close()
    return src, seg


def finished_segments(buf_dir):
    """All segments except the newest, which FFmpeg may still be writing."""
    files = sorted(glob.glob(os.path.join(buf_dir, "seg_*.ts")))
    return files[:-1]


def prune(buf_dir):
    files = sorted(glob.glob(os.path.join(buf_dir, "seg_*.ts")))
    for old in files[:-BUFFER_SEGMENTS]:
        try:
            os.remove(old)
        except OSError:
            pass


# ---------- Steps 4-6: cut, caption, and render vertical ----------------------------
def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def transcribe_to_srt(wav_path, srt_path):
    """Step 5: Whisper captions. Imported lazily so the clipper runs without it."""
    from faster_whisper import WhisperModel  # pip install faster-whisper
    model = WhisperModel("base", compute_type="int8")
    segments, _ = model.transcribe(wav_path, vad_filter=True)

    def stamp(s):
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{sec:06.3f}".replace(".", ",")

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{stamp(seg.start)} --> {stamp(seg.end)}\n{seg.text.strip()}\n\n")


def render_clip(source, start, length, out_path, captions=False):
    """Cut [start, start+length] from source and render 1080x1920 MP4 (optionally captioned)."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    vertical = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
    with tempfile.TemporaryDirectory() as tmp:
        if captions:
            wav = os.path.join(tmp, "audio.wav")
            run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(length),
                 "-i", source, "-vn", "-ac", "1", "-ar", "16000", wav])
            srt = os.path.join(tmp, "captions.srt")  # relative name used by the subtitles filter
            transcribe_to_srt(wav, srt)
            vf = (f"{vertical},subtitles=captions.srt:force_style="
                  "'Alignment=2,FontSize=16,Bold=1,Outline=2,MarginV=260'")
            run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(length),
                 "-i", os.path.abspath(source), "-vf", vf,
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                 os.path.abspath(out_path)], cwd=tmp)
        else:
            run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(length),
                 "-i", source, "-vf", vertical,
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out_path])
    print(f"[clip] saved {out_path}", flush=True)
    return out_path


def clip_from_buffer(buf_dir, captions):
    """Concat the most recent finished segments and cut the last CLIP_SECONDS."""
    segs = finished_segments(buf_dir)
    needed = -(-CLIP_SECONDS // SEGMENT_SECONDS)  # ceil
    if len(segs) < needed:
        print("[clip] not enough buffered video yet", flush=True)
        return None
    segs = segs[-needed:]
    with tempfile.TemporaryDirectory() as tmp:
        listing = os.path.join(tmp, "list.txt")
        with open(listing, "w") as f:
            for s in segs:
                f.write(f"file '{os.path.abspath(s)}'\n")
        joined = os.path.join(tmp, "joined.ts")
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
             "-i", listing, "-c", "copy", joined])
        total = len(segs) * SEGMENT_SECONDS
        start = max(0, total - CLIP_SECONDS)
        out = os.path.join(OUT_DIR, datetime.now().strftime("clip_%Y%m%d_%H%M%S.mp4"))
        return render_clip(joined, start, CLIP_SECONDS, out, captions)


def live(args):
    if not args.file and not args.channel:
        sys.exit("live: pass --channel or --file")
    buf_dir = tempfile.mkdtemp(prefix="clipper_buf_")
    stop = threading.Event()
    counter = {"n": 0}
    lock = threading.Lock()

    def on_message():
        with lock:
            counter["n"] += 1

    chat_channel = args.channel or "test"
    if not args.file:
        threading.Thread(target=read_chat, args=(chat_channel, on_message, stop),
                         daemon=True).start()
    src, seg = start_recorder(buf_dir, channel=args.channel, file=args.file)
    detector = SpikeDetector(factor=args.factor, min_msgs=args.min_msgs, cooldown=args.cooldown)
    print(f"[live] recording {'file ' + args.file if args.file else args.channel}; watching chat",
          flush=True)
    started = time.time()
    try:
        while seg.poll() is None:
            time.sleep(BUCKET_SECONDS)
            with lock:
                count, counter["n"] = counter["n"], 0
            t = time.time() - started
            prune(buf_dir)
            print(f"[chat] {count} msgs / {BUCKET_SECONDS}s", flush=True)
            if detector.add_bucket(count, t):
                print(f"[spike] {count} msgs at t={t:.0f}s -> clipping", flush=True)
                clip_from_buffer(buf_dir, args.captions)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        seg.terminate()
        src.terminate()


def cut(args):
    start = max(0.0, args.at - args.before)
    out = os.path.join(OUT_DIR, datetime.now().strftime("clip_%Y%m%d_%H%M%S.mp4"))
    render_clip(args.input, start, args.before + args.after, out, args.captions)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    lp = sub.add_parser("live", help="watch a live stream and clip chat spikes")
    lp.add_argument("--channel", help="Twitch channel name")
    lp.add_argument("--file", help="local video to replay as the live stream (testing)")
    lp.add_argument("--captions", action="store_true", help="add Whisper captions")
    lp.add_argument("--factor", type=float, default=3.0, help="spike must be N x baseline")
    lp.add_argument("--min-msgs", type=int, default=15, help="min messages in a 10 s bucket")
    lp.add_argument("--cooldown", type=int, default=60, help="seconds between clips")
    lp.set_defaults(func=live)

    cp = sub.add_parser("cut", help="clip one moment from a local video")
    cp.add_argument("--input", required=True)
    cp.add_argument("--at", type=float, required=True, help="moment of interest (seconds)")
    cp.add_argument("--before", type=float, default=25.0)
    cp.add_argument("--after", type=float, default=5.0)
    cp.add_argument("--captions", action="store_true")
    cp.set_defaults(func=cut)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
