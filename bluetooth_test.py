from bluepy import btle
# from bluepy.btle import Scanner, DefaultDelegate, BTLEException
import time
import sys
import bluepy.btle
import pandas as pd
import numpy as np
import pygame as pg
import os

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

for i in range(3):
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

latest_sample = ""
window = []
class ScanDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device {0}".format(dev.addr))
        elif isNewData:
            print("Received new data from {0}".format(dev.addr))


def twos_complement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value


def parseAccAndTime(accTimeString):
    accx_ts3_0 = accTimeString[0:4]
    accy_ts7_4 = accTimeString[4:8]
    accz_ts11_8 = accTimeString[8:12]

    accx = accx_ts3_0[2:4] + accx_ts3_0[0] + '0'
    accy = accy_ts7_4[2:4] + accy_ts7_4[0] + '0'
    accz = accz_ts11_8[2:4] + accz_ts11_8[0] + '0'

    ts = accz_ts11_8[1] + accy_ts7_4[1] + accx_ts3_0[1]

    accx_int = int(accx, 16)
    accy_int = int(accy, 16)
    accz_int = int(accz, 16)

    accx_signedint = twos_complement(accx, 16)
    accy_signedint = twos_complement(accy, 16)
    accz_signedint = twos_complement(accz, 16)

    return accx_signedint, accy_signedint, accz_signedint, ts


def parseMagnetometerAndTime(magTimeString):
    ts15_12_mx = magTimeString[0:4]
    ts19_16_my = magTimeString[4:8]
    ts23_20_mz = magTimeString[8:12]

    mx = ts15_12_mx[1] + ts15_12_mx[2:4]
    my = ts19_16_my[1] + ts19_16_my[2:4]
    mz = ts23_20_mz[1] + ts23_20_mz[2:4]

    ts = ts23_20_mz[0] + ts19_16_my[0] + ts15_12_mx[0]

    mx_signedint = twos_complement(mx, 12)
    my_signedint = twos_complement(my, 12)
    mz_signedint = twos_complement(mz, 12)

    return mx_signedint, my_signedint, mz_signedint, ts


def parseBluetoothData(hexString):

    accx, accy, accz, ts11_0 = parseAccAndTime(hexString[4:16])

    mx, my, mz, ts23_12 = parseMagnetometerAndTime(hexString[16:28])

    ts = int(ts23_12 + ts11_0, 16)

    return accx, accy, accz, ts


def form_sample(sample, timestamp, acc_x, acc_y, acc_z):
    sample.append(timestamp)
    for i in range(1):
        sample.append(acc_x)
        sample.append(acc_y)
        sample.append(acc_z)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, hndl):
        btle.DefaultDelegate.__init__(self)
        print("handle notification init")
        # ... initialise here
        self.hndl = hndl;
        self.timebefore = time.time()
        self.count = 0;
        self.window = []


    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        # global latest_sample
        if (cHandle == self.hndl):
            # print("handleNotification handle 0x%04X, data %s" % (cHandle, str(data)))
            # latest_sample = data.hex()
            
            acc_x, acc_y, acc_z, ts = parseBluetoothData(data.hex())
            sample = []
            form_sample(sample, ts, acc_x, acc_y, acc_z)

            self.window.append(sample)
            

            if (time.time() - timebefore) >= 10:
                print("10 secs over")
                convert_samples_to_csv(self.window)
                sys.exit(0)

            self.count += 1

        else:
            print("handleNotification handle 0x%04X unknown" % (cHandle))

        # if self.count == 500:
        #     print("time taken for 500 samples: {0}".format(time.time()-self.timebefore))
        #     sys.exit(0)
        


# Initialisation  -------
homerehab_mac_addr = "b4:99:4c:55:86:38"
service_uuid = "0000fff0-0000-1000-8000-00805f9b34fb"
char_uuid = "0000fff1-0000-1000-8000-00805f9b34fb"

scanner = btle.Scanner().withDelegate(ScanDelegate())
peripheral = btle.Peripheral()

def connectSensor(scanner, peripheral, homerehab_mac_addr):
    try:
        devices = scanner.scan(10.0, passive=True)
    except (btle.BTLEException, BrokenPipeError, AttributeError) as e:
        print(e)

    hasStartSensor = False

    for dev in devices:
        print("Device {0} ({1}), RSSI={2} dB".format(dev.addr, dev.addrType, dev.rssi))
        # for (adtype, desc, value) in dev.getScanData():
        #     print("  {0} = {1}".format(desc, value))

        if dev.addr == homerehab_mac_addr:
            hasStartSensor = True

    if hasStartSensor == True:
        try:
            peripheral.connect(homerehab_mac_addr) #Start sensor
            print("Sensor connected!")
        except (bluepy.btle.BTLEException, BrokenPipeError, AttributeError) as e:
            print(e)
    else:
        print("Sensor failed to connect")
        sys.exit(0)

    return peripheral


# start connecting to bluetooth sensor and trigger receiving of notifications
connectedPeripheral = connectSensor(scanner, peripheral, homerehab_mac_addr)
# connectedPeripheral = peripheral
# Setup to turn notifications on, e.g.
svc = connectedPeripheral.getServiceByUUID( service_uuid )
ch = svc.getCharacteristics( char_uuid )[0]
connectedPeripheral.writeCharacteristic(ch.getHandle() + 1, bytes([0x01, 0x00]))
connectedPeripheral.withDelegate(MyDelegate(ch.getHandle()))


def convert_samples_to_csv(samples):
    csv_data = pd.DataFrame()
    file_path = "/home/pi/Desktop/wearable/demo/samples.csv"

    for sample in samples:

        csv_row_np = np.array(sample)
        csv_row = csv_row_np.reshape(-1, len(csv_row_np))
        csv_data = csv_data.append(pd.DataFrame(csv_row))


    csv_data.to_csv(file_path, index=None, header=False)

timebefore = time.time()
while True:
    if connectedPeripheral.waitForNotifications(0.005):
        print("handle notification called")
        continue

    print("Waiting...")
    # Perhaps do something else here