import speech_recognition as sr
import os
import subprocess
import io
import json
import pprint
from split import split_by_seconds

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_CLOUD_SPEECH_CREDENTIALS = open(os.path.join(BASE_DIR, 'hacktj', 'cloud-speech-api-key.json')).read()


def flac_from_video(infile, outfile='/tmp/out.flac'):
    subprocess.run("ffmpeg -y -loglevel panic -i {} -c:a flac {}".format(infile, outfile), shell=True)
    return outfile


def run_splits(video, words):
    fname = flac_from_video(video)
    fnames = split_by_seconds(fname, 55)
    print(fnames)
    data = []
    for f in fnames:
        data.append(search(f, words))
    return data


def search(a, words):
    r = sr.Recognizer()
    with sr.AudioFile(a) as source:
        audio = r.record(source)
    return r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, show_all=True)


if __name__ == "__main__":
    x = run_splits('intro.mp4', [])
    pprint.pprint(x)
