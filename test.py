#!/usr/bin/python

from time import sleep
import time

from lsm6ds33 import LSM6DS33
from lis3mdl import LIS3MDL
from lps25h import LPS25H

imu = LSM6DS33()
imu.enableLSM()

magnet = LIS3MDL()
magnet.enableLIS()

timebefore = time.time()
count = 0

while True:

    print("Gyro:", imu.getGyroscopeRaw())
    #imu.getGyroscopeRaw()
    #imu.getAccelerometerRaw()
    #magnet.getMagnetometerRaw()
    #count += 1
    #if (time.time() - timebefore) >= 30:
       #print(count)
       #break
    print("Accelerometer:", imu.getAccelerometerRaw())
    print("Magnet:", magnet.getMagnetometerRaw())
    sleep(0.2)
    #print("LSM6DS33 Temperature:", imu.getLSMTemperatureCelsius())
    #print("LIS3MDL Temperature:", magnet.getLISTemperatureCelsius())
    #sleep(0.1)
