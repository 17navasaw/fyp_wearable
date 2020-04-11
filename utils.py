import math
import numpy as np
import csv

def read_csv(path, load_header=False, delimiter=","):
    content = []
    # try:
    with open(path, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        if load_header:
            for row in csv_reader:
                content.append(row)
            # [content.append(row) for row in csv_reader]
        else:
            [content.append(row) for i, row in enumerate(csv_reader) if i > 0]
    # except Exception as e:
    #     print(e)
    return content


def write_csv(content, header, path, delimiter=","):
    path = ensure_path(path)
    with open(path, 'w', encoding="utf-8", newline='') as f:
        csv_writer = csv.writer(f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        if header is not None:
            csv_writer.writerow(header)

        for row in content:
            csv_writer.writerow(row)


def extract_rms(window, index):
    sum_of_squares = 0

    for i in range(len(window)):
        sum_of_squares += math.pow(float(window[i][index]), 2.0)

    return math.sqrt(sum_of_squares)

def extract_rms_np(window, index):
    li = []
    for i in range(len(window)):
        li.append(float(window[i][index]))

    return np.sqrt(np.mean(np.array(li)**2))

def extract_std(window, index):
    li = []
    for i in range(len(window)):
        li.append(float(window[i][index]))

    return np.std(li, ddof=1)

def extract_std_welford(window, index):
    mean = 0
    sum = 0

    for i in range(len(window)):
        x = float(window[i][index])
        old_mean = mean
        mean = mean + (x-mean)/(i+1)
        sum = sum + (x-mean)*(x-old_mean)

    return math.sqrt(sum/(len(window) - 1))

def extract_fi_one_side(window, left_acc_ind_first, lb_low_hz, lb_high_hz, fb_low_hz, fb_high_hz):
    left_accx = []
    left_accy = []
    left_accz = []

    for x in range(len(window)):
        sample = window[x]

        left_accx.append(float(sample[left_acc_ind_first]))
        left_accy.append(float(sample[left_acc_ind_first+1]))
        left_accz.append(float(sample[left_acc_ind_first+2]))

    left_accx_fft = list(map(abs, np.fft.fft(left_accx)))
    left_accy_fft = list(map(abs, np.fft.fft(left_accy)))
    left_accz_fft = list(map(abs, np.fft.fft(left_accz)))

    left_accx_power = list(map(lambda y: pow(y, 2.0), left_accx_fft))
    left_accy_power = list(map(lambda y: pow(y, 2.0), left_accy_fft))
    left_accz_power = list(map(lambda y: pow(y, 2.0), left_accz_fft))

    left_window = []

    for x in range(len(window)):
        left_window.append(left_accx_power[x] + left_accy_power[x] + left_accz_power[x])

    bin_width = 50.0 / len(window)
    lb_low = int(lb_low_hz / bin_width)
    lb_high = int(lb_high_hz / bin_width)
    fb_low = int(fb_low_hz / bin_width)
    fb_high = int(fb_high_hz / bin_width)

    lb_power_left = 0
    fb_power_left = 0

    for x in range(lb_low, lb_high+1):
        lb_power_left += left_window[x]
    for x in range(fb_low, fb_high+1):
        fb_power_left += left_window[x]

    return fb_power_left / lb_power_left