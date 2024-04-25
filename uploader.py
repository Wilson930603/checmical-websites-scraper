import boto3
from glob import glob
import os
import time
import json

s3 = boto3.client(
    's3',
    aws_access_key_id='xxxxxx',
    aws_secret_access_key='xxxxxx'
)
count = 0
while True:
    print('Start while loop')
    historyDict = []
    try:
        historyFile = open("historySize.txt","r")
        historyDict = json.loads(historyFile.read())
    except Exception as e:print(e)

    test = glob("./outputs/*.json", recursive = True)
    print(test)
    for te in test:
        head, tail = os.path.split(te)

        fileOpen = open(te,"r")
        fileLen = len(fileOpen.readlines())
        fileOpen.close()

        found = False
        sizeOk = False
        for hist in historyDict:
            if(hist['file']==te):
                # hist['size']=fileLen
                found = True
                if(int(fileLen)-int(hist['size'])>2000):
                    sizeOk = True
                    hist['size'] = fileLen

        if(not found):
            historyDict.append({'file':te,'size':fileLen})
            s3.upload_file(Filename=te,Bucket='data-scrapes',Key=tail)
            print("NewFile >> " + te)

        if(found and sizeOk):
            s3.upload_file(Filename=te,Bucket='data-scrapes',Key=tail)
            print("Uploading.. >> " + te)

    fileWrite = open("historySize.txt","w")
    fileWrite.write(json.dumps(historyDict))
    fileWrite.close()
    time.sleep(1800)
    count+=1
    print(count)
