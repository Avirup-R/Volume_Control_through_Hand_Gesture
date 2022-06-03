import cv2
import time
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import Adv_Hand_Track as htm

wCam, hCam =640, 480



cap=cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime=0

detector=htm.handDetector(detectionCon=0.7, maxHands=1)



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange=volume.GetVolumeRange()
# print(volRange)
volume.SetMasterVolumeLevel(-20.0, None)
minVol=volRange[0]
maxVol=volRange[1]


vol=0
volBar=400
volPer=0
area=0
colorVol=(255, 0, 0)
while True:
    success, img =cap.read()

    #hand
    img=detector.findHands(img)
    lmList, bbox=detector.findPosition(img, draw=True)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        # print(bbox)
        wB, hB=bbox[2]-bbox[0], bbox[3]-bbox[1]
        area=wB*hB//100
        print(area)
        if 200<area<1000:
            # print('yea')

            #find distance b/w index and thumb
            length, img, lineinfo= detector.findDistance(4, 8, img)
            print(length)

            # Convert Volume

            volBar=np.interp(length,[30, 150], [400, 150])
            volPer = np.interp(length, [30, 150], [0, 100])
            # print(vol)
            # volume.SetMasterVolumeLevel(vol, None)

            #Reduce resolution for better accuracy
            smoothness=2
            # smothness is the value of increment
            volPer=smoothness* round(volPer/smoothness)

            # print(int(length))
            # which finger to use as accept
            fingers=detector.fingersUp()
            print(fingers)
            #check
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineinfo[4], lineinfo[5]), 15, (0, 255, 0), cv2.FILLED)
                colorVol=(0, 255, 0)
            else:
                colorVol = (255, 0, 0)

            # set volume if F-finger up


            # hand range 40 - 300
            # volume range -65(65.25) - 0
#OPTIONAL
            # for quiting the program
            if fingers[1]==0 and fingers[2]==0 and fingers[3]==0 and fingers[4]==0:
                quit(0)

            if length<30:
                cv2.circle(img, (lineinfo[4],lineinfo[5]), 15, (0, 0, 255), cv2.FILLED)

        #drawing
        cv2.rectangle(img, (50, 150), (85, 400), (8, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (8, 255, 0), cv2.FILLED)
        cv2.putText(img, f'Vol: {int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)
        cVol=int(volume.GetMasterVolumeLevelScalar( )*100)
        cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX,
                    1, colorVol, 3)
    #Frame Rate
    cTime=time.time()
    fps=1/(cTime-pTime)
    pTime=cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    cv2.imshow('Img', img)
    cv2.waitKey(1)


