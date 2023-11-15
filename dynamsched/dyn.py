import math
import sys
from time import time

class Funk():
    def __init__(self) -> None:
        self.effAdd = 10
        self.fpAdd = 0
        self.fpMul = 0
        self.ints = 0
        self.reorder = 0

        self.intLat = 1
        self.addLat = 0
        self.subLat = 0
        self.multLat = 0
        self.divLat = 0


def parseConfig(file: list, funk: Funk) -> None:
    for i, line in enumerate(file):
        if "buffers" in line:
            if "eff addr" in file[i+2]:
                funk.effAdd = int(file[i+2].split(": ")[1])
            if "fp adds" in file[i+3]:
                funk.fpAdd = int(file[i+3].split(": ")[1])
            if "fp muls" in file[i+4]:
                funk.fpMul = int(file[i+4].split(": ")[1])
            if "ints" in file[i+5]:
                funk.ints = int(file[i+5].split(": ")[1])
            if "reorder" in file[i+6]:
                funk.reorder = int(file[i+6].split(": ")[1])

        if "latencies" in line:
            if "fp_add" in file[i+2]:
                funk.addLat = int(file[i+2].split(": ")[1])
            if "fp_sub" in file[i+3]:
                funk.subLat = int(file[i+3].split(": ")[1])
            if "fp_mul" in file[i+4]:
                funk.mulLat = int(file[i+4].split(": ")[1])
            if "fp_div" in file[i+5]:
                funk.divLat = int(file[i+5].split(": ")[1])


if __name__ == "__main__":
    options = []
    with open("config.txt", "r") as configFile:
        for setting in configFile:
            options.append(setting)

    funk = Funk()

    parseConfig(options, funk)

    print("Configuration")
    print("-------------")
    print("buffers:")
    print(f"{'eff addr: ':>13}{funk.effAdd}")
    print(f"{'fp adds: ':>13}{funk.fpAdd}")
    print(f"{'fp muls: ':>13}{funk.fpMul}")
    print(f"{'ints: ':>13}{funk.ints}")
    print(f"{'reorder: ':>13}{funk.reorder}")
    print("")
    print("latencies:")
    print(f"{'fp add: ':>13}{funk.addLat}")
    print(f"{'fp sub: ':>13}{funk.subLat}")
    print(f"{'fp mul: ':>13}{funk.multLat}")
    print(f"{'fp div: ':>13}{funk.divLat}")