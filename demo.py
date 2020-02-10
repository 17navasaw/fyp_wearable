#!/usr/bin/python3

from time import sleep
import time

from lsm6ds33 import LSM6DS33
from lis3mdl import LIS3MDL
from lps25h import LPS25H

import sys
import pygame as pg
import os

imu = LSM6DS33()
imu.enableLSM()

magnet = LIS3MDL()
magnet.enableLIS()

timebefore = time.time()
count = 0

# set mp3 settings
freq = 44100    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)
pg.mixer.init(freq, bitsize, channels, buffer)
user_volume = 1.0
pg.mixer.music.set_volume(user_volume)
mp3s = []
for file in os.listdir("."):
    if file.endswith(".mp3"):
        mp3s.append(file)

def play_music(music_file):
    '''
    stream music with mixer.music module in blocking manner
    this will stream the sound from disk while playing
    '''
    clock = pg.time.Clock()
    try:
        pg.mixer.music.load(music_file)
        print("Music file {} loaded!".format(music_file))
    except pygame.error:
        print("File {} not found! {}".format(music_file, pg.get_error()))
        return

    pg.mixer.music.play()
    print("After pg.mixer.music.play")
    # If you want to fade in the audio...
    # for x in range(0,100):
    #     pg.mixer.music.set_volume(float(x)/100.0)
    #     time.sleep(.0075)
    # # check if playback has finished
    while pg.mixer.music.get_busy():
        clock.tick(30)

while True:

    gyro = imu.getGyroscopeRaw()
    acc = imu.getAccelerometerRaw()
    magnetic = magnet.getMagnetometerRaw()
    #count += 1
    #if (time.time() - timebefore) >= 30:
       #print(count)
       #break
    # print("Gyro:", gyro)
    # print("Accelerometer:", acc)
    # print("Magnet:", magnetic)

    #accx = acc[0]
    #accy = acc[1]
    accz = acc[2]
    # if accz < -5000 or accz > 5000:
    #     print(accz)
    # print(accz)

    if accz > 8000:
        # Play mp3
        for x in mp3s: 
            try:
                play_music(x)
                time.sleep(.25)
            except KeyboardInterrupt:
                # if user hits Ctrl/C then exit
                # (works only in console mode)
                pg.mixer.music.fadeout(1000)
                pg.mixer.music.stop()
                raise SystemExit
        sleep(0.2)