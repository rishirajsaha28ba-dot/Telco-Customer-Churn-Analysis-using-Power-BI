# Twitch Live Clipper

A small pipeline that watches a live Twitch stream, notices when chat suddenly gets busy,
and cuts a 30-second vertical (9:16) clip from the stream around that moment.

## The steps

1. **Record the live stream**: Streamlink pipes the stream into FFmpeg, which writes 10-second segments to a rolling buffer.
2. **Count chat every 10 seconds**: joins chat anonymously (read-only, no login) and counts messages per 10-second bucket.
3. **Detect a spike**: a bucket fires when it has at least `--min-msgs` messages and at least `--factor` times the recent average. A `--cooldown` stops repeat clips.
4. **Cut the clip**: FFmpeg joins the latest segments and cuts the last 30 seconds.
5. **Caption it** (optional, `--captions`): Whisper transcribes the clip and the captions are burned in.
6. **Render vertical**: output is 1080x1920 H.264 + AAC MP4 in `clips/`.

## Setup

```bash
pip install faster-whisper          # only needed for --captions
sudo apt-get install -y ffmpeg      # needed for everything
pip install streamlink              # needed for live Twitch streams
```

## Usage

Watch a live channel and clip chat spikes:

```bash
python clipper.py live --channel SOMECHANNEL --captions
```

Clip one moment from a local video (25 s before, 5 s after):

```bash
python clipper.py cut --input stream.mp4 --at 40 --captions
```

Replay a local video as if it were live (useful for testing the loop without Twitch):

```bash
python clipper.py live --file stream.mp4 --channel test
```

Note: without chat in replay mode, no spikes fire. Test spike detection with the unit tests.

## Tests

```bash
python -m unittest -v test_clipper
```

## Notes

- Chat is read anonymously over Twitch IRC (`justinfan` login), which needs no token.
- Clip boundaries snap to the 10-second segment grid, so a clip can be off by up to about a segment.
- Respect the streamer and Twitch's terms; clips are for the channel's own highlights.
