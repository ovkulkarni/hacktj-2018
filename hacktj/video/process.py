import numpy as np
import cv2 as cv
import json

from clarifai import rest
from clarifai.rest import ClarifaiApp

app = ClarifaiApp(api_key='de12174484d04ac7ae713ce0fbf5cf56')
model = app.models.get('general-v1.3')

def search(fname):
    cap = cv.VideoCapture(fname)
    
    info = {}
    cnt = 0
    
    while(cap.isOpened()):
       ret, frame = cap.read()
       if not ret: 
          break
       cnt+=1
       if cnt%60==0:
          cv.imwrite('temp.png', frame)
          response = model.predict_by_filename(filename='temp.png')
          info[cnt] = []
          for res in response['outputs'][0]['data']['concepts']:
             if res['value']>0.93:
                info[cnt].append(res['name'])
    
       #print(json.dumps(response, indent=4, sort_keys=True))
       
    result = {}
    for time in info:
       for obj in info[time]:
          if not obj in result:
             result[obj] = []
          result[obj].append(time)
    return result

