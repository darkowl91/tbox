#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import bme280
import smbus2

DEFAULT_ADDRESS = 0x76
DEFAULT_PORT = 1


def to_str(data):
    return "{},{},{}".format(round(data.temperature),
                             round(data.humidity),
                             round(data.pressure))


def main():
    try:
        _bus = smbus2.SMBus(DEFAULT_PORT)
        bme280.load_calibration_params(_bus, DEFAULT_ADDRESS)
        # print bme values to std out
        print(to_str(bme280.sample(_bus, DEFAULT_ADDRESS)))

    except Exception as e:
        print(e, file=sys.stderr)
        return -1
    finally:
        _bus.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
