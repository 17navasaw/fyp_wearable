#!/usr/bin/python

from time import sleep
import time

from lsm6ds33 import LSM6DS33
# from lis3mdl import LIS3MDL
# from lps25h import LPS25H

from constants import *
import utils
from joblib import load

imu = LSM6DS33()
imu.enableLSM()

# magnet = LIS3MDL()
# magnet.enableLIS()

timebefore = time.time()
count = 0

window = []
clf = load('lda.joblib')


def form_sample(sample, timestamp, acc_x, acc_y, acc_z):
   sample.append(timestamp)
   for i in range(2):
      sample.append(acc_x)
      sample.append(acc_y)
      sample.append(acc_z)


def feature_extract(test_window):
    
   features_test_window = np.empty(shape=(1, 3))

   window = test_window
   features_window = []

   left_accz_rms = utils.extract_rms(window, LEFT_ACCZ_INDEX)
   right_accz_rms = utils.extract_rms(window, RIGHT_ACCZ_INDEX)
   avg_accz_rms = (left_accz_rms + right_accz_rms) / 2.0
   features_window.append(avg_accz_rms)

   left_accz_std = utils.extract_std(window, LEFT_ACCZ_INDEX)
   right_accz_std = utils.extract_std(window, RIGHT_ACCZ_INDEX)
   avg_accz_std = (left_accz_std + right_accz_std) / 2.0
   features_window.append(avg_accz_std)

   features_window.append(
      utils.extract_fi(window, LEFT_ACCX_INDEX, RIGHT_ACCX_INDEX, LB_LOW, LB_HIGH, FB_LOW, FB_HIGH))

   # features_test_windows.append(features_window)
   features_test_window[0] = np.array(features_window)

   return features_test_window

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
      window = []
   
   sleep(0.01)