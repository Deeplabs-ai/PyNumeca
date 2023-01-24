import math


def convert_rotational_speed(value, to_rpm=True):
    if to_rpm:
        return value * 30 / math.pi
    else:
        return value * math.pi / 30
