#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_imu_v2.py ui/imu_v2.ui")
system("pyuic4 -o ui_calibration.py ui/calibration.ui")
