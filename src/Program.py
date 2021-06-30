import Line
import pprint
import global_vars as g

pp = pprint.PrettyPrinter()

class Program():

    def __init__(self, fileName):

        self.line_objects = []
        self.locctr = 0
        f = open("../tests/"+fileName)
        for ln in f:
            self.line_objects.append(Line.Line(ln))


    def pass_1(self):
        for index, line_obj in enumerate (self.line_objects):
            line_obj.pass_1()
            if line_obj.size == -1:
                for i in range(index):
                    print("Errors found in pass 1. Printing possible warnings/errors")
                    pp.pprint(self.line_objects[i].__dict__)
                    self.line_objects[i].printWarnings(i+1)
                    self.line_objects[i].printWarnings(i+1)
                    exit(0)
            if index == 0:
                if line_obj.instruction == "START":
                    self.locctr = int(line_obj.args)
            line_obj.update_symtab(self.locctr)
            self.locctr += line_obj.size
            if index == len(self.line_objects)-1:
                self.line_objects[index].setProgramCounter(self.locctr)
        # print(self.line_objects[-1].raw)
        # print(self.line_objects[-1].content)

    def pass_2(self):
        for index, line_obj in enumerate(self.line_objects):
            line_obj.pass_2()  #since the last instruction has nothing after it

    def writeToFile(self, outFileName):
        debug = True
        header = 'H'
        textRecords = []
        end = 'E'

        #the header bit
        first = self.line_objects[0]
        name = ' ' * 6
        progStartAddress = '0' * 6
        if first.instruction == 'START' and first.label != -1:
                name = first.label
                while len(name) < 6:
                    name = ' ' + name
        if first.instruction == "START":
            progStartAddress = self.args
            while len(progStartAddress) < 6:
                progStartAddress = ' ' + progStartAddress

        progSize = hex(self.locctr)[2:]

        header += name
        if debug:
            header += '|'
        header += progStartAddress
        if debug:
            header += '|'
        header += progSize
        if debug:
            header += '|'

        #the text records
        counter = 0
        oneRecord = ''
        startAddresss = ''
        for line_obj in self.line_objects:
            if line_obj.binary == -1 or counter + line_obj.size > 30:
                if counter > 0:
                    counter = hex(counter)[2:]
                    while len(counter) < 2:
                        counter = '0' + counter
                    combo = 'T'
                    if debug:
                        combo += '|'
                    combo += startAddress
                    if debug:
                        combo += '|'
                    combo += counter
                    if debug:
                        combo += '|'
                    combo += oneRecord
                    if debug:
                        combo += '|'
                    textRecords.append(combo)
                counter = 0
                oneRecord = ''
            if counter == 0 and line_obj.binary != -1:
                startAddress = str(line_obj.location)
                while len(startAddress) < 6:
                    startAddress = '0' + startAddress
            if line_obj.binary != -1:
                oneRecord += line_obj.binary
                if debug:
                    oneRecord += '|'
            if counter == 0 and line_obj.binary != -1:
                counter += line_obj.size

        if counter > 0:
            counter = hex(counter)[2:]
            while len(counter) < 2:
                counter = '0' + counter
            combo = 'T'
            if debug:
                combo += '|'
            combo += startAddress
            if debug:
                combo += '|'
            combo += counter
            if debug:
                combo += '|'
            combo += oneRecord
            if debug:
                combo += '|'
            textRecords.append(combo)

        #the end record
        if debug:
            end += '|'
        end += progStartAddress

        # the actual writing
        f = open("../tests/"+outFileName, "w")
        f.write(header)
        f.write('\n')
        for rec in textRecords:
            f.write(rec)
        f.write('\n')
        f.write(end)
        f.close()

        if debug:
            pprint.pprint(textRecords)

    def observe(self):
        for line_obj in self.line_objects:
            pprint.pprint([line_obj.location, line_obj.size, line_obj.label, line_obj.instruction, line_obj.args, line_obj.programCounter,
            line_obj.targetAddress, line_obj.binary])
        print(g.symtab)

    def spillTheBeans(self):
        for line_obj in self.line_objects:
            pprint.pprint(line_obj.__dict__)
            print("\n\n ---------------------------------------- ")
