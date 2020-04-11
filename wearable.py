#!/usr/bin/python

from time import sleep
import time

from lsm6ds33 import LSM6DS33
# from lis3mdl import LIS3MDL
# from lps25h import LPS25H

from constants import *
import utils
from joblib import load
from sklearn.metrics import classification_report

import numpy as np

import pygame as pg
import sys
import os

imu = LSM6DS33()
imu.enableLSM()

# magnet = LIS3MDL()
# magnet.enableLIS()

count = 0

window = []
clf = load('rf_all.joblib')

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

def form_sample(sample, timestamp, acc_x, acc_y, acc_z):
   sample.append(timestamp)
   for i in range(1):
      sample.append(acc_x)
      sample.append(acc_y)
      sample.append(acc_z)


def feature_extract(test_window):
    
   features_test_window = np.empty(shape=(1, 3))

   window = test_window
   features_window = []

   left_accz_rms = utils.extract_rms(window, LEFT_ACCZ_INDEX)
   # right_accz_rms = utils.extract_rms_np(window, RIGHT_ACCZ_INDEX)
   # avg_accz_rms = (left_accz_rms + right_accz_rms) / 2.0
   # features_window.append(avg_accz_rms)
   features_window.append(left_accz_rms)

   # timebefore = time.time()
   left_accz_std = utils.extract_std(window, LEFT_ACCZ_INDEX)
   # time_std = time.time() - timebefore
   # timebefore_std_welford = time.time()
   # right_accz_std = utils.extract_std_welford(window, RIGHT_ACCZ_INDEX)
   # time_std_welford = time.time() - timebefore_std_welford
   # avg_accz_std = (left_accz_std + right_accz_std) / 2.0
   # features_window.append(avg_accz_std)
   features_window.append(left_accz_std)

   features_window.append(
      utils.extract_fi_one_side(window, LEFT_ACCX_INDEX, LB_LOW, LB_HIGH, FB_LOW, FB_HIGH))

   features_test_window[0] = np.array(features_window)

   return features_test_window

def simulate_sensor(clf, window_size, file_name):
   left_ind = 0
   right_ind = left_ind + window_size

   # test_samples = form_test_samples(test_windows, window_size)
   test_samples = utils.read_csv(file_name, load_header=True, delimiter=",")
   print(len(test_samples))

   predicted_labels = []
   actual_labels = []
   num_windows = 0
   # form window
   while right_ind <= len(test_samples):
      window = test_samples[left_ind:right_ind]
      sample = np.empty(shape=(1, 3))

      # actual_labels.append(int(float(window[window_size-1][FOG_INDEX])))
      actual_labels.append(1)

      features_window = feature_extract(window)

      # predict with 1 sample
      sample[0] = np.array(features_window)
      predicted_label = clf.predict(sample)
      predicted_labels.append(predicted_label[0])

      left_ind += 1
      right_ind += 1
      num_windows += 1

   # print("Feature extraction time is {0:.5f} across {1} windows".format(feature_extract_time, num_windows))
   # print("Time std: {0:6f} Time std with welford: {1:6f} across {2} windows".format(std_extract_time, std_welford_extract_time, num_windows))
   target_names = ['non-FOG', 'FOG']
   print(classification_report(actual_labels, predicted_labels, labels=[0, 1], target_names=target_names))

simulate_sensor(clf, 100, 'samples.csv')
sys.exit(0)

timebefore = time.time()

while True:

   # gyro = imu.getGyroscopeRaw()
   # gyro_x = gyro[0]
   # gyro_y = gyro[1]
   # gyro_z = gyro[2]

   acc = imu.getAccelerometerRaw()
   acc_x = acc[0]
   acc_y = acc[1]
   acc_z = acc[2]

   timestamp = time.time() - timebefore

   sample = []
   form_sample(sample, timestamp, acc_x, acc_y, acc_z)

   # print(sample)

   window.append(sample)

   if len(window) >= WIN_SIZE:
      print(time.time() - timebefore)
      print("window size 100!")
      features_window = feature_extract(window)
      predicted_label = clf.predict(features_window)[0]
      print("Predicted label: {}".format(predicted_label))

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

      window = window[1:]
      # sys.exit(0)
   
   sleep(0.01)