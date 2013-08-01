encodey
=======

A python script for reencoding video files (mkv) to depreciated formats (avi and mp4). Supports (some) subtitles.

Requires:
Python (2.7.3),
Ubuntu? (12.04),
FFMPEG (built with x264, libass, libmp3lame, and libfdk_aac support),
mencoder,
mkvtoolnix (specifically mkvextract),
mediainfo,

Better description:
Reencodes formats from mkv to avi by default. Takes arguments to change input and output types, resolutions, bitrates, stuff.
Supports .ass, .ssa, .srt subtitles.
Currently only outputs mp4 or avi files.

Frontend:
For the webs! so you don't have to cli your way through stuff.
