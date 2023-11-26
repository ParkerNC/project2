import sys

class Funk():
    def __init__(self) -> None:
        self.effAdd = 0
        self.fpAdd = 0
        self.fpMul = 0
        self.ints = 0
        self.reorder = 0

        self.intLat = 1
        self.addLat = 0
        self.subLat = 0
        self.mulLat = 0
        self.divLat = 0

        self.cycle = 0

        self.reorderDelays = 0
        self.reservationDelays = 0
        self.memoryDelays = 0
        self.dependenceDelays = 0

        self.reorderBuff = []

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
        
    def functionalUnits(self, inst: str) -> int:
        if inst == "fadd.s":
            return self.fpAdd
        elif inst == "fsub.s":
            return self.fpAdd
        elif inst == "fmul.s":
            return self.fpMul
        elif inst == "fdiv.s":
            return self.fpMul
        elif inst == "add":
            return self.ints
        elif inst == "sub":
            return self.ints
        elif inst == "beq":
            return self.ints
        elif inst == "bne": 
            return self.ints
        else:
            return self.effAdd

    def first(self, instruction: str) -> int:
        issueCycle = funk.cycle +1
        line = instruction.split(" ")
        readCycle = ''
        writeCycle = ''
        executeCycle = issueCycle + self.lat(line[0])
        if 'lw' in line[0]:
            readCycle = executeCycle+1
        if 'beq' not in line[0] and 'sw' not in line[0] and "bne" not in line[0]:
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

        self.reorderBuff.append((instruction, issueCycle, (issueCycle+1, executeCycle), readCycle, writeCycle, commitCycle))

        self.cycle +=1

        return printLine

    def buffConflict(self, cycle: int, stage: int) -> int:
        newCycle = cycle
        for line in self.reorderBuff:
            if newCycle == line[stage]:
                newCycle = self.buffConflict(newCycle+1, stage)

        return newCycle
    
    def fuConflict(self, type: str, start: int, end: int):
        pairs = []
        if type in ["fadd.s", "fsub.s"]:
            pairs = ["fadd.s", "fsub.s"]
        elif type in ["fmul.s", "fdiv.s"]:
            pairs = ["fmul.s", "fdiv.s"]
        elif type in ["add", "sub", "bne", "beq"]:
            pairs = ["add", "sub", "bne", "beq"]
        elif type in ["lw", "sw", "flw", "fsw"]:
            pairs = ["lw", "sw", "flw", "fsw"]

        matches = []
        for line in self.reorderBuff:
            if line[0].split(" ")[0] in pairs and start <= line[2][1]:
                if line[0].split(" ")[0] in ["lw", "flw"]:
                    matches.append(line[3])
                    continue 
                matches.append(line[2][1])
            if line[0].split(" ")[0] in pairs and line[0].split(" ")[0] in ["lw", "flw"] and start <= line[3]:
                matches.append(line[3])

        """
        for line in self.reorderBuff:
            if line[0].split(" ")[0] in pairs:
                if line[0].split(" ")[0] in ["lw", "flw"]:
                    if start < line[3]:
                        matches.append(line[3])
                        continue
                if start <= line[2][1]:
                    matches.append(line[2][1])

                if line[0].split(" ")[0] not in ["lw", "flw"]:
                    if line[4] != '':
                        if start > line[2][1] and start < line[4]:
                            matches.append(line[4])

        """


        if len(matches) >= self.functionalUnits(type):
            return min(matches)
            
        return start
    
    def rawCheck(self, readLine: list, writeLine: tuple) -> tuple:
        writeInstruction = writeLine[0]
        writeInstruction = writeInstruction.split(" ")
        if writeInstruction[0] not in ["beq", "bne", "sw", "fsw"]:
            readRegisters = readLine[-1].strip()
            readRegisters = readRegisters.split(',')
            if readLine[0] in ["flw", "lw", "sw", "fsw"]:
                tmp = readRegisters[-1].split("(")[1]
                tmp = tmp.split(")")[0]
                readRegisters[-1] = tmp

            writeRegister = writeInstruction[-1].strip()
            writeRegister = writeRegister.split(',')[0]
            if readLine[0] in ["beq", "bne"]:
                if writeRegister in readRegisters:

                    return (writeLine[4], writeRegister)
            else:
                if writeRegister in readRegisters[1:]:
                    return (writeLine[4], writeRegister)
                
        return (0, "0")

    def dataDependence(self, line: list, cycle: int) -> int:
        #if line[0] not in ["sw", "fsw"]:
        deps = {}
        for prevLine in self.reorderBuff:
            if prevLine[4] == '':
                continue
            
            dep = funk.rawCheck(line, prevLine)
            if dep[0] != 0:
                deps[dep[1]] = dep[0]

        
        if len(deps) > 0:
            big = 0
            for dep in deps:
                if big < deps[dep]:
                    big = deps[dep]

            if big >= cycle:
                return big
        
        return cycle

    def memoryConflict(self, line: list, cycle: int) -> int:
        readingLocation = line[-1].split(":")[-1]
        for prevLine in self.reorderBuff:
            if prevLine[0].split(" ")[0] in ["sw", "fsw"]:
                writtenLoction = prevLine[0].split(" ")[-1].split(":")[-1]
                if readingLocation == writtenLoction and cycle <= prevLine[5]:
                    return prevLine[5]+1
                
        return cycle
    
    def memoryBuffConflict(self, cycle: int) -> int:
        newCycle = cycle
        for line in self.reorderBuff:
            if line[0].split(" ")[0] in ["sw", "fsw"] and newCycle == line[5]:
                newCycle +=1

        return newCycle


    def issue(self, line: list, cycle: int) -> int:
        issCycle = cycle
        latency = funk.lat(line[0])
        issCycle = funk.fuConflict(line[0], issCycle, latency)

        if issCycle != cycle:
            self.reservationDelays+=1

        if len(self.reorderBuff) >= self.reorder:
            if issCycle < self.reorderBuff[0][5]:
                self.reorderDelays +=1
                issCycle = self.reorderBuff[0][5] -1
        
        funk.cycle = issCycle

        return issCycle+1
    
    def execute(self, line: list, cycle: int) -> int:
        
        latency = funk.lat(line[0])
        executeCycle = funk.dataDependence(line, cycle)
        if executeCycle != cycle:
            self.dependenceDelays +=1
        
        return executeCycle+1, executeCycle+latency
    
    def read(self, line: list, cycle: int) -> int:
        readCycle = self.memoryConflict(line, cycle+1)
        if readCycle != cycle:
            self.memoryDelays +=1
        readCycle = self.buffConflict(readCycle, 3)
        readCycle = self.memoryBuffConflict(readCycle)
        readCycle = self.buffConflict(readCycle, 3)
        
        return readCycle
    
    def write(self, line: list, cycle: int) -> int:
        writeCycle = self.buffConflict(cycle+1, 4)
        return writeCycle
    
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
    executeCycleStart, executeCycleEnd = funk.execute(line, issueCycle)
    if 'lw' in line[0]:
        readCycle = funk.read(line, executeCycleEnd)
    if 'beq' not in line[0] and 'sw' not in line[0] and "bne" not in line[0]:
        if readCycle != '':
            writeCycle = funk.write(line, readCycle)
        else:
            writeCycle = funk.write(line, executeCycleEnd)
    
    if writeCycle != '':
        commitCycle = funk.commit(line, writeCycle)
    elif readCycle != '':
        commitCycle = funk.commit(line, readCycle)
    else:
        commitCycle = funk.commit(line, executeCycleEnd)

    funk.reorderBuff.append((instruction, issueCycle, (executeCycleStart, executeCycleEnd), readCycle, writeCycle, commitCycle))

    executeCycles = f"{executeCycleStart:>3} -{executeCycleEnd:>3}"

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
    print(f"{'fp add: ':>11}{funk.addLat}")
    print(f"{'fp sub: ':>11}{funk.subLat}")
    print(f"{'fp mul: ':>11}{funk.mulLat}")
    print(f"{'fp div: ':>11}{funk.divLat}")
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
    print(f"reservation station delays: {funk.reservationDelays}")
    print(f"data memory conflict delays: {funk.memoryDelays}")
    print(f"true dependence delays: {funk.dependenceDelays}")