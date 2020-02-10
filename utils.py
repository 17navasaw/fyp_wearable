import math
import numpy as np

def extract_rms(window, index):
    sum_of_squares = 0

    for i in range(len(window)):
        sum_of_squares += math.pow(float(window[i][index]), 2.0)

    return math.sqrt(sum_of_squares)


def extract_std(window, index):
    li = []
    for i in range(len(window)):
        li.append(float(window[i][index]))

    return np.std(li, ddof=1)


def extract_fi(window, left_acc_ind_first, right_acc_ind_first, lb_low_hz, lb_high_hz, fb_low_hz, fb_high_hz):
    left_accx = []
    left_accy = []
    left_accz = []
    right_accx = []
    right_accy = []
    right_accz = []

    for x in range(len(window)):
        sample = window[x]

        left_accx.append(float(sample[left_acc_ind_first]))
        left_accy.append(float(sample[left_acc_ind_first+1]))
        left_accz.append(float(sample[left_acc_ind_first+2]))
        right_accx.append(float(sample[right_acc_ind_first]))
        right_accy.append(float(sample[right_acc_ind_first+1]))
        right_accz.append(float(sample[right_acc_ind_first+2]))

    left_accx_fft = list(map(abs, np.fft.fft(left_accx)))
    left_accy_fft = list(map(abs, np.fft.fft(left_accy)))
    left_accz_fft = list(map(abs, np.fft.fft(left_accz)))
    right_accx_fft = list(map(abs, np.fft.fft(right_accx)))
    right_accy_fft = list(map(abs, np.fft.fft(right_accy)))
    right_accz_fft = list(map(abs, np.fft.fft(right_accz)))

    left_accx_power = list(map(lambda y: pow(y, 2.0), left_accx_fft))
    left_accy_power = list(map(lambda y: pow(y, 2.0), left_accy_fft))
    left_accz_power = list(map(lambda y: pow(y, 2.0), left_accz_fft))
    right_accx_power = list(map(lambda y: pow(y, 2.0), right_accx_fft))
    right_accy_power = list(map(lambda y: pow(y, 2.0), right_accy_fft))
    right_accz_power = list(map(lambda y: pow(y, 2.0), right_accz_fft))

    left_window = []
    right_window = []

    for x in range(len(window)):
        left_window.append(left_accx_power[x] + left_accy_power[x] + left_accz_power[x])
        right_window.append(right_accx_power[x] + right_accy_power[x] + right_accz_power[x])

    bin_width = 50.0 / len(window)
    lb_low = int(lb_low_hz / bin_width)
    lb_high = int(lb_high_hz / bin_width)
    fb_low = int(fb_low_hz / bin_width)
    fb_high = int(fb_high_hz / bin_width)

    lb_power_left = 0
    fb_power_left = 0
    lb_power_right = 0
    fb_power_right = 0
    for x in range(lb_low, lb_high+1):
        lb_power_left += left_window[x]
        lb_power_right += right_window[x]
    for x in range(fb_low, fb_high+1):
        fb_power_left += left_window[x]
        fb_power_right += right_window[x]

    return ((fb_power_right / lb_power_right) + (fb_power_left / lb_power_left)) / 2.0