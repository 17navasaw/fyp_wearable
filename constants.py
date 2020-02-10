#!/usr/bin/python

### Python module to control several aspects of Pololu's AltIMU-10v5 ###
#
# This file contains several constants used by the various module
# classes.
#
# The Python code is developed and maintained by
# Torsten Kurbad <github@tk-webart.de>
#
########################################################################

## Global constants

# I2C device addresses
LIS3MDL_ADDR    = 0x1e      # Magnetometer
LPS25H_ADDR     = 0x5d      # Barometric pressure sensor
LSM6DS33_ADDR   = 0x6b      # Gyrometer / accelerometer

C_FILTER_CONST  = 0.60      # Complementary filter constant

# Used by the Kalman filter
K_Q_ANGLE       = 0.01
K_Q_GYRO        = 0.0003
K_R_ANGLE       = 0.01

# Gyroscope dps/LSB for 1000 dps full scale
GYRO_GAIN       = 0.035

# Indices in window
LEFT_ACCX_INDEX = 1
LEFT_ACCY_INDEX = 2
LEFT_ACCZ_INDEX = 3
RIGHT_ACCX_INDEX = 4
RIGHT_ACCY_INDEX = 5
RIGHT_ACCZ_INDEX = 6

# Thresholds for Freezing Index in Hz
LB_LOW = 0.5 # Lower bound of locomotion band index
LB_HIGH = 3 # Upper bound of locomotion band index
FB_LOW = 3 # Lower bound of freeze band index
FB_HIGH = 8 # Upper bound of freeze band index

WIN_SIZE = 100