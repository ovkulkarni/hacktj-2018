import speech_recognition as sr
import os
import subprocess
import io
import json
import pprint
from .split import split_by_seconds

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOOGLE_CLOUD_SPEECH_CREDENTIALS = open(os.path.join(BASE_DIR, 'hacktj', 'cloud-speech-api-key.json')).read()


def flac_from_video(infile, outfile='/tmp/out.flac'):
    subprocess.run("ffmpeg -y -loglevel panic -i {} -c:a flac {}".format(infile, outfile), shell=True)
    return outfile


def combine_dicts(a, b):
    if len(b) > len(a):
        a, b = b, a
    for k in b:
        if k in a:
            a[k].extend(b[k])
        else:
            a[k] = b[k]
    return a


def word_data(video, split_length=55):
    fname = flac_from_video(video)
    fname_starts = split_by_seconds(fname, split_length)
    trans = []
    order = {}
    cur_word = 0
    for f, start in fname_starts:
        order, trans, cur_word = search(f, order, trans, add_time=start, cur_word=cur_word)
    return order, trans

def find_matches(data, phrase):
    order, trans = data
    words = phrase.lower().split()
    for word in words:
        if word not in order: return None
    if len(words) == 1:
        return [t for t, p in order[words[0]]]
    times = []
    for time, pos in order[words[0]]:
        for e, word in enumerate(words[1:], start=1):
            if trans[pos+e] != word: break
        else: times.append(time)
    return sorted(times)

def search(a, word_order, trans, add_time=0, cur_word=0):
    r = sr.Recognizer()
    with sr.AudioFile(a) as source:
        audio = r.record(source)
    results = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, show_all=True)

    if 'results' in results:
        for section in results['results']:
            best_alt = section['alternatives'][0]
            for inst in best_alt['words']:
                time = float(inst['startTime'][:-1]) + add_time
                word = inst['word'].lower()
                if word in word_order:
                    word_order[word].append((time, cur_word))
                else:
                    word_order[word] = [(time, cur_word)]
                trans.append(word)
                cur_word += 1
    return word_order, trans, cur_word

if __name__ == "__main__":
    x = word_data('trump.mp4')
    pprint.pprint(x)
