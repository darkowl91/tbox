#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time

import Adafruit_PCA9685

PWM = Adafruit_PCA9685.PCA9685()
PWM.set_pwm_freq(50)


def main():
    try:
        channel = int(sys.argv[1])  # chanels: 0,1
        pulse = int(float(sys.argv[2]))  # min:100, max:500
        print("channel {} receive pulse {}".format(channel, pulse))

        PWM.set_pwm(channel, 0, pulse)
        time.sleep(0.5)
        PWM.set_pwm(channel, 0, 0)  # off
    except Exception as e:
        print(e, file=sys.stderr)
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
