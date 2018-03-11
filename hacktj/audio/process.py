import speech_recognition as sr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gcloud_apikey_path = os.path.join(BASE_DIR, 'hacktj/cloud-speech-api-key.json')

def flac_from_video(infile, outfile='/tmp/out.flac'):
    subprocess.run("ffmpeg -y -loglevel PANIC -i {} -c:a flac {}".format(infile, outfile), shell=True)
    return outfile

def search(video, phrases):
    global client

    ffile = flac_from_video(video)

    r = sr.Recognizer()

    with sr.AudioFile(ffile) as source:
        audio = r.record(source)

    GOOGLE_CLOUD_SPEECH_CREDENTIALS = open(gcloud_apikey_path).read()
    try:
        print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
    except sr.UnknownValueError:
        print("Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Cloud Speech service; {0}".format(e))

if __name__ == "__main__":
    search('test.mp4', [])
