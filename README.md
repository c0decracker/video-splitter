# Command Line Video Splitter

Simple command line Python script that splits video into multi chunks. Under the hood script uses [FFMpeg] so you will need to have that installed. No transcoding or modification of video happens, it just get's split properly.

Run `python ffmpeg-split.py -h` to see the options. Here are few samples of how it could be used:

## Spliting video into equal chunks

`python ffmpeg-split.py -f big_video_file.mp4 -s 10`

This splits `big_video_file.mp4` into 10 chunks. Each chunk will be suffixed with numeric index, for example `big_video_file-0.mp4`, `big_video_file-1.mp4`, etc.

## Splitting videos into unequal chunks

In order to create unequal chunks of a video, you'll need to create ***manifest.json***.


***manifest.json***

```json

[
    {
        "start_time": 0,
        "length": 34,
        "rename_to": "video1"
    },
    {
        "start_time": 35,
        "length": 22,
        "rename_to": "video2.mp4"
    }
]

```

Afterwards run:

`python ffmpeg-split.py -f big_video_file.mp4 -m manifest.json`

This splits `big_video_file.mp4` into 2 video files, video1.mp4 and video2.mp4. The video1.mp4 is a 34 seconds
clip, starting from 0:00 to 0:34 of the `big_video_file.mp4`.


Alternatively, you can use a ***manifest.csv*** file to accomplish the task above.

***manifest.csv***:

```CSV

start_time,length,rename_to
0,34,video1
35,22,video2

```


#### Manifest Options

* start_time      - number of seconds into the video or start time
* length          - length of the video in seconds. The end time of the video is calculated by the start_time plus the length of the video.
* rename_to       - name of the video clip to be saved
* end_time        - end time of the video




[FFMpeg]: https://www.ffmpeg.org/


