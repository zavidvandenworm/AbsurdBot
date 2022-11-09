import ffmpeg
import sys

author_id = sys.argv[1]
video_dl = sys.argv[2]
audio_dl = sys.argv[3]
bitrate = sys.argv[4]
kwargs = sys.argv[5]
imgtest = bool(sys.argv[6])
video_out = sys.argv[7]
audio_length = ffmpeg.probe(audio_dl)['format']['duration']
audio_ff = ffmpeg.input(audio_dl)

if "extend" in kwargs:
    video_ff = ffmpeg.input(video_dl, t=audio_length, stream_loop=-1)
elif imgtest:
    video_ff = ffmpeg.input(video_dl, t=audio_length, stream_loop=-1, r=1)
else:
    video_ff = ffmpeg.input(video_dl)
    video_length = ffmpeg.probe(video_dl)['format']['duration']
    audio_ff = audio_ff.filter_('atrim', start=0, end=video_length)
    audio_ff = audio_ff.filter_('asetpts', 'PTS-STARTPTS')

concat = ffmpeg.concat(video_ff, audio_ff, v=1, a=1)
out = ffmpeg.output(concat, video_out, bitrate=bitrate)
out.run(overwrite_output=True)
