import sys
import ffmpeg
import os

work_directory = sys.argv[1]
local_file = sys.argv[2]
uid = sys.argv[3]

www_directory = "/var/www/mab502.com/public/dev/absurdibot_data/"

size_a = [640, 480]

size = f"{str(size_a[0])}x{str(size_a[1])}"

output = ffmpeg.input(local_file)
audio = ffmpeg.input(local_file)
output = ffmpeg.filter(output, "showwaves", s=size, mode="cline", rate=25, colors="White|White")
spectrum = ffmpeg.filter(audio, "showspectrum", size=size, stop=10000, slide="scroll")
output = ffmpeg.filter([output, spectrum], "blend", all_mode="overlay")

out = f"{www_directory}/{uid}.mp4"

output = ffmpeg.overwrite_output(ffmpeg.output(output, audio, out, acodec="copy"))
ffmpeg.run(output)
