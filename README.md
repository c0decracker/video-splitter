# Command Line Video Splitter

Simple command line Python script that splits video into multi chunks. Under the hood script uses [FFMpeg] so you will need to have that installed. No transcoding or modification of video happens, it just get's split properly.

Run `python ffmpeg-split.py -h` to see the options. Here are few samples of how it could be used:

`python ffmpeg-split.py -f big_video_file.mp4 -s 10`

This splits `big_video_file.mp4` into 10 chunks. Each chunk will be suffixed with numeric index, for example `big_video_file-0.mp4`, `big_video_file-1.mp4`, etc.


[FFMpeg]: https://www.ffmpeg.org/ 


