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
        self.mulLat = 0
        self.divLat = 0

        self.reorderBuff = []
        self.fpAddBuff = []
        self.fpMulBuff = []
        self.intsBuff = []
        self.cycle = 0

        self.reorderDelays = 0

        self.que = []

    def lat(self, inst: str) -> int:
        if inst == "fadd.s":
            return self.addLat
        elif inst == "fsub.s":
            return self.subLat
        elif inst == "fmul.s":
            return self.mulLat
        elif inst == "fdiv.s":
            return self.divLat
        else:
            return self.intLat

    def first(self, instruction: str) -> int:
        issueCycle = funk.cycle +1
        line = instruction.split(" ")
        readCycle = ''
        executeCycle = issueCycle + self.lat(line[0])
        if 'lw' in line[0]:
            readCycle = executeCycle+1
        if 'be' not in line[0] and 'sw' not in line[0]:
            if readCycle != '':
                writeCycle = readCycle +1
            else:
                writeCycle = executeCycle +1

        if writeCycle != '':
            commitCycle = writeCycle +1
        elif readCycle != '':
            commitCycle = readCycle +1
        else:
            commitCycle = executeCycle +1
        

        executeCycles = f"{issueCycle+1:>3} -{executeCycle:>3}"
        printLine = f"{instruction.strip():<21} {funk.cycle+1:>6} {executeCycles:>8} {readCycle:>6} {writeCycle:>6} {commitCycle:>7}"

        funk.reorderBuff.append((instruction, issueCycle, executeCycle, readCycle, writeCycle, commitCycle))

        funk.cycle +=1

        return printLine

    def issue(self, line: list, cycle: int) -> int:
        if len(self.reorderBuff) >= self.reorder:
            issCycle = self.reorderBuff[0][5]
            funk.cycle = issCycle
            self.reorderDelays += issCycle - cycle
            return issCycle
        return cycle +1
    
    def execute(self, line: list, cycle: int) -> int:
        latency = funk.lat(line[0])
        return cycle + latency
    
    def read(self, line: list, cycle: int) -> int:
        return cycle + 1
    
    def write(self, line: list, cycle: int) -> int:
        return cycle + 1
    
    def commit(self, line: list, cycle: int) -> int:

        comCycle = cycle + 1
        if comCycle <= self.reorderBuff[-1][5]:
            return self.reorderBuff[-1][5] + 1
        return cycle + 1

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

            if (funk.fpAdd + funk.fpMul + funk.effAdd) > 10:
                print("too many reservation stations")
                exit(2)
            if funk.reorder > 10:
                print("too many entries for the reorder buffer")
                exit(2)

        if "latencies" in line:
            if "fp_add" in file[i+2]:
                funk.addLat = int(file[i+2].split(": ")[1])
            if "fp_sub" in file[i+3]:
                funk.subLat = int(file[i+3].split(": ")[1])
            if "fp_mul" in file[i+4]:
                funk.mulLat = int(file[i+4].split(": ")[1])
            if "fp_div" in file[i+5]:
                funk.divLat = int(file[i+5].split(": ")[1])



def cycle(funk: Funk, instruction: str) -> str:
    line = instruction.split(' ')

    if funk.reorderBuff[0][5] <= funk.cycle:
        funk.reorderBuff.pop(0)

    
    readCycle = ''
    writeCycle = ''

    issueCycle = funk.issue(line, funk.cycle)
    executeCycle = funk.execute(line, issueCycle)
    if 'lw' in line[0]:
        readCycle = funk.read(line, executeCycle)
    if 'be' not in line[0] and 'sw' not in line[0]:
        if readCycle != '':
            writeCycle = funk.write(line, readCycle)
        else:
            writeCycle = funk.write(line, executeCycle)
    
    if writeCycle != '':
        commitCycle = funk.commit(line, writeCycle)
    elif readCycle != '':
        commitCycle = funk.commit(line, readCycle)
    else:
        commitCycle = funk.commit(line, executeCycle)

    funk.reorderBuff.append((instruction, issueCycle, executeCycle, readCycle, writeCycle, commitCycle))

    executeCycles = f"{issueCycle+1:>3} -{executeCycle:>3}"

    printLine = f"{instruction.strip():<21} {issueCycle:>6} {executeCycles:>8} {readCycle:>6} {writeCycle:>6} {commitCycle:>7}"

    funk.cycle +=1

    return printLine


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
    print(f"{'fp mul: ':>13}{funk.mulLat}")
    print(f"{'fp div: ':>13}{funk.divLat}")
    print("")
    print("")
    print(f"{'Pipeline Simulation':^59}")
    print("-" * 59)

    print(f"{'':^38}{'Memory Writes'}")
    print(f"{'Instruction':^21} {'Issues':^} {'Executes':^} {'Read':^6} {'Result':^6} {'Commits':^7}")
    print(f"{'-'*21} {'-'*6} {'-'*8} {'-'*6} {'-'*6} {'-'*7}")


    instruction = next(sys.stdin)
    line = funk.first(instruction)
    print(line)

    for instruction in sys.stdin:

        line = cycle(funk, instruction)

        print(line)

    print("")
    print("")
    print("Delays")
    print("------")
    print(f"reorder buffer delays: {funk.reorderDelays}")