import numpy as np
import os
import time
import matplotlib.pyplot as plt
from os import listdir
from os.path import isfile, join, getmtime
from scipy.fftpack import fft, fftshift

from Modules import read_dat
from Modules import read_wav
from Modules import selectfile
from Modules import SignalData
from Modules import importfile
from Modules import fourier
from Modules import bandpass
from Modules import freqbands
from Modules import waterfall
from Modules import detect


def analysis(SignalInfo):
    filename = 'satellite_db.json'
    bands = freqbands.getbands(SignalInfo, filename)

    chunksize = int(1024 * 2 * 2 * 2 * 2 * 2 * 2 * 2)
    # waterfall.plot_waterfall(SignalInfo,chunksize,30)

    for band in bands:
        FLow = band[1]
        FHigh = band[2]

        signal_filtered = bandpass.filter_box(
            SignalInfo, FLow, FHigh, chunksize)

        n = 10 * 1000
        all_average = detect.calc_average(signal_filtered, n)
        threshold = detect.calc_threshold(signal_filtered)
        times, points = detect.find_segs(
            all_average, threshold, 50, 20, float(SignalInfo.Fsample), n, signal_filtered)

        for k in range(len(points)):
            point = points[k][0]
            new_point = detect.re_check(signal_filtered, point, threshold, n)
            points[k][0] = new_point
            times[k][0] = new_point / int(SignalInfo.Fsample)

        del signal_filtered


def singlefile():

    SignalInfo = selectfile.select()

    if SignalInfo.filetype == ".dat":
        SignalInfo.filedata = read_dat.loaddata(SignalInfo.filename)
    else:
        SignalInfo.filedata = read_wav.loaddata(SignalInfo.filename)

    analysis(SignalInfo)


def folderwatch():
    name = "/home/matrix/Desktop/aero/data"
    laststamp = -1
    while True:
        contents = os.listdir(name)
        process = []
        for content in contents:
            if(content.endswith('.dat') or content.endswith('.wav')):
                if (laststamp == -1):
                    process.append(join(name, content))
                else:
                    if(getmtime(join(name, content)) > laststamp):
                        process.append(join(name, content))

        laststamp = time.time()

        for file in process:
            SignalInfo = importfile.loadfile(file)

            if SignalInfo.filetype == ".dat":
                SignalInfo.filedata = read_dat.loaddata(SignalInfo.filename)
            else:
                SignalInfo.filedata = read_wav.loaddata(SignalInfo.filename)

            analysis(SignalInfo)


def main():
    option = "y"
    option = input("Do you want to launch single signal analysis (y/n) [y]? ")
    if option == "y" or option == "Y":
        singlefile()
    elif option == "n" or option == "N":
        folderwatch()
    else:
        pass


if __name__ == "__main__":
    main()
