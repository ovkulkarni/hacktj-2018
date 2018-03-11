from google.oauth2 import service_account
from google.cloud import speech
import subprocess
import os

#Retrieve Google Cloud Credentials
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gcloud_apikey_path = os.path.join(BASE_DIR, 'hacktj/cloud-speech-api-key.json')
credentials = service_account.Credentials.from_service_account_file(gcloud_apikey_path)

#Initialize SpeechClient
client = speech.SpeechClient(credentials=credentials)

def flac_from_video(infile, outfile='/tmp/out.flac'):
    subprocess.run("ffmpeg -i {} -c:a flac {}".format(infile, outfile), shell=True)
    return outfile

def search(video, phrases):
    global client

    flac = flac_from_video(video)
    config = {
        'encoding': speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        'sample_rate_hertz': 44100,
        'language_code': 'en-US'
    }
    audio = {'content': open(flac, 'rb').read()}

    print('Recognizing...')
    response = client.recognize(config, audio)
    print(response)
