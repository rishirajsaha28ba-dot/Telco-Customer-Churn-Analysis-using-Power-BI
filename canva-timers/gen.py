import subprocess, sys, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
W,H,FPS=960,236,24
BG=(8,13,16); WHITE=(255,255,255); RED=(255,43,58); DIM=(70,22,26)
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
fl=ImageFont.truetype(BOLD,34); fd=ImageFont.truetype(MONO,120); fu=ImageFont.truetype(BOLD,92)
def spaced(d,y,txt,font,fill,sp=10):
    w=sum(d.textlength(c,font=font) for c in txt)+sp*(len(txt)-1); x=(W-w)/2
    for c in txt: d.text((x,y),c,font=font,fill=fill); x+=d.textlength(c,font=font)+sp
def frame(t,T):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    rem=T-t
    if rem>0:
        import math; s=math.ceil(rem-1e-9); col=RED if s<=10 else WHITE
        spaced(d,14,'TIME',fl,WHITE)
        txt=f'{s//60:02d}:{s%60:02d}'; w=d.textlength(txt,font=fd)
        d.text(((W-w)/2,52),txt,font=fd,fill=col)
        d.rectangle((60,206,W-60,212),fill=DIM)
        d.rectangle((60,206,60+(W-120)*rem/T,212),fill=RED)
    else:
        on=int((t-T)*2)%2==0
        txt="TIME'S UP"; w=d.textlength(txt,font=fu)
        d.text(((W-w)/2,(H-110)/2),txt,font=fu,fill=RED if on else DIM)
    return im
for T in map(int,sys.argv[1:]):
    out=f'timer_{T//60:02d}m{T%60:02d}s.mp4'; n=(T+4)*FPS
    p=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
       '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-movflags','+faststart',out],stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(frame(i/FPS,T).tobytes())
    p.stdin.close(); p.wait(); print(out)
    frame(0,T).save(out.replace('.mp4','_start.png'))
frame(37,40).save('preview_last10.png'); frame(41,40).save('preview_up.png')
