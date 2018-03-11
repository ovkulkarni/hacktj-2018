import subprocess
import re
import math
import os


length_regexp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_length = re.compile(length_regexp)


def split_by_seconds(filename, split_length, vcodec="copy", acodec="copy", extra="", **kwargs):
    if split_length and split_length <= 0:
        return [filename]
    output = subprocess.Popen("ffmpeg -y -i '" + filename + "' 2>&1 | grep 'Duration'",
                              shell=True,
                              stdout=subprocess.PIPE
                              ).stdout.read()
    matches = re_length.search(output.decode())
    if matches:
        video_length = int(matches.group(1)) * 3600 + \
            int(matches.group(2)) * 60 + \
            int(matches.group(3))
    else:
        print("Can't determine video length.")
        raise SystemExit
    split_count = int(math.ceil(video_length / float(split_length)))
    split_cmd = "ffmpeg -y -loglevel panic -i '{}' -vcodec {} -acodec {} {}" .format(filename, vcodec, acodec, extra)
    filebase = ".".join(filename.split(".")[:-1])
    fileext = filename.split(".")[-1]
    fname_starts = []
    for n in range(0, split_count):
        split_str = ""
        if n == 0:
            split_start = 0
        else:
            split_start = split_length * n

        split_str += " -ss " + str(split_start) + " -t " + str(split_length) + " '" + filebase + "-" + str(n) + "." + fileext + "'"
        output = subprocess.Popen(split_cmd + split_str, shell=True, stdout=subprocess.PIPE).stdout.read()
        fname_starts.append((filebase + "-" + str(n) + "." + fileext, split_start))
    return fname_starts
