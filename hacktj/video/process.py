import numpy as np
import cv2 as cv
import json

from clarifai import rest
from clarifai.rest import ClarifaiApp

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet

def word_data(filename):
   app = ClarifaiApp(api_key='de12174484d04ac7ae713ce0fbf5cf56')
   model = app.models.get('general-v1.3')
   cap = cv.VideoCapture(filename)
   fps = int(cap.get(cv.CAP_PROP_FPS));
   info = {}
   while(cap.isOpened()):
      ret, frame = cap.read()
      if not ret:
         break
      cnt+=1
      print(cnt)
      if cnt%(2*fps)==0:
         cv.imwrite('/tmp/temp.png', frame)
         response = model.predict_by_filename(filename='/tmp/temp.png')
         time = cnt/fps
         info[time] = []
         for res in response['outputs'][0]['data']['concepts']:
            if res['value']>0.93:
               info[time].append(res['name'])
   result = {}
   for time in info:
      for obj in info[time]:
         if not obj in result:
            result[obj] = []
         if not result[obj] or result[obj] and time-result[obj][-1]>8:
            result[obj].append(time)

   return result

def noun_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        if syn.name().split('.')[1] != 'n': continue
        for l in syn.lemmas():
            synonyms.add(l.name())
    return synonyms

def find_matches(dct, orig):
    lm = WordNetLemmatizer()
    word = lm.lemmatize(orig)
    times = set()
    for term in noun_synonyms(word):
        if term not in dct: continue
        times.update(dct[term])
    return sorted(times)

table = word_data('/Users/mmreed/Downloads/Rick Astley - Never Gonna Give You Up.mp4')
print(table)
