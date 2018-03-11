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


def combine_dicts(a, b):
    if len(b) > len(a):
        a, b = b, a
    for k in b:
        if k in a: a[k].extend(b[k])
        else: a[k] = b[k]
    return a

def word_data(video, split_length=55):
    fname = flac_from_video(video)
    fname_starts = split_by_seconds(fname, split_length)
    data = {}
    for f, start in fname_starts:
        word_times = search(f, add_time=start)
        data = combine_dicts(data, word_times)
    return data

def search(a, add_time=0):
    r = sr.Recognizer()
    with sr.AudioFile(a) as source:
        audio = r.record(source)
    results = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, show_all=True)
    inner = results['results'][0]['alternatives'][0]
    word_times = {}
    for inst in inner['words']:
        time = float(inst['startTime'][:-1]) + add_time
        word = inst['word'].lower()
        if word in word_times:
            word_times[word].append(time)
        else: word_times[word] = [time]
    return word_times

if __name__ == "__main__":
    x = word_data('intro.mp4')
    pprint.pprint(x)
