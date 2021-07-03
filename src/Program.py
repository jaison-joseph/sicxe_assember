import Line
import pprint
import global_vars as g

pp = pprint.PrettyPrinter()

class Program():

    def __init__(self, fileName):

        f = open("../tests/"+fileName)
        for index, ln in enumerate(f):
            line_obj = Line.Line(ln)
            line_obj.pass_1(g.locctr)
            if len(line_obj.errors) != 0:
                print("Errors found in pass 1. Printing possible warnings/errors")
                pp.pprint(g.line_objects[i].__dict__)
                for i in range(index, -1, -1):
                    if len(g.line_objects[i].warnings != 0):
                        g.line_objects[i].printWarnings(i+1)
                    if len(g.line_objects[i].errors != 0):
                        g.line_objects[i].printErrors(i+1)

            g.line_objects.append(line_obj)
            if index == 0 and line_obj.instruction == "START":
                g.locctr += g.start_address
                line_obj.location = g.start_address
            print("locctr: ", g.locctr, " :: size: ", line_obj.size)
            g.locctr += line_obj.size

    #
    #
    # def pass_1(self):
    #     for index, line_obj in enumerate (g.line_objects):
    #         line_obj.pass_1(g.locctr)
    #             # if line_obj.instruction == "START":
    #             #     g.locctr = int(line_obj.args)
    #             #     line_obj.location = g.locctr
    #         # line_obj.update_symtab(g.locctr)
    #     # print(self.line_objects[-1].raw)
    #     # print(self.line_objects[-1].content)

    def pass_2(self):
        for index, line_obj in enumerate(g.line_objects):
            if index != len(g.line_objects)-1:
                g.line_objects[index].programCounter = g.line_objects[index+1].location
            if ( not line_obj.pass_2()):  #since the last instruction has nothing after it
                print("Errors found in pass 2. Printing possible warnings/errors")
                # pp.pprint(g.line_objects[i].__dict__)
                g.line_objects[index].printWarnings(index+1)
                g.line_objects[index].printErrors(index+1)
                exit(0)

    def writeToFile(self, outFileName):
        debug = True
        header = 'H'
        textRecords = []
        end = 'E'

        if debug:
            header += '|'

        #the header bit
        first = g.line_objects[0]
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

        progSize = hex(g.locctr)[2:]

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
        lengthForRecord = 0
        oneRecord = ''
        startAddresss = ''
        for line_obj in g.line_objects:
            if line_obj.binary == -1 or counter + line_obj.size > 30 or line_obj.instruction in ["RESW", "RESB"]:
                if counter > 0 and line_obj.instruction not in ["RESW", "RESB"]:
                    lengthForRecord = hex(counter)[2:]
                    while len(lengthForRecord) < 2:
                        lengthForRecord = '0' + lengthForRecord
                    combo = 'T'
                    if debug:
                        combo += '|'
                    combo += startAddress
                    if debug:
                        combo += '|'
                    combo += lengthForRecord
                    if debug:
                        combo += '|'
                    combo += oneRecord
                    if debug:
                        combo += '|'
                    combo += '\n'
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
            # if counter == 0 and line_obj.binary != -1:
            counter += line_obj.size
            print("counter: ", counter)

        if counter > 0:
            lengthForRecord = hex(counter)[2:]
            while len(lengthForRecord) < 2:
                lengthForRecord = '0' + lengthForRecord
            combo = 'T'
            if debug:
                combo += '|'
            combo += startAddress
            if debug:
                combo += '|'
            combo += lengthForRecord
            if debug:
                combo += '|'
            combo += oneRecord
            if debug:
                combo += '|'
            combo += '\n'
            textRecords.append(combo)

        #the end record
        if debug:
            end += '|'
        end += progStartAddress

        # the actual writing
        f = open("../tests/"+outFileName, "w")
        f.write(header[:-1]) #1 '|' at the end
        f.write('\n')
        for rec in textRecords[:-1]:
            f.write(rec[:-3])   #since there are 2 erroneous '|' at the end of each text record
        f.write('\n')
        f.write(end[:-1])     #1 '|' at the end
        f.close()

        if debug:
            pprint.pprint(textRecords)

    def outputSave(self):
        debug = True
        header = 'H'
        textRecords = []
        end = 'E'

        #the header bit
        first = g.line_objects[0]
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
        progSize = hex(g.locctr)[2:]
        header = name + progStartAddress + progSize

        #the end record
        end += progStartAddress

        #the text records
        ctr = 0
        thirty = 0
        temp_record = ''
        size = len(self.line_objects)-1
        for index, obj in self.line_objects:
            increase = obj.size 
            if ctr != obj.location:
                if ctr in g.littab.keys():
                    increase = g.littab[]
            if obj.binary == -1 or ctr != obj.location:
                if ctr != obj.location:
                    if ctr in g.littab.keys():

                textRecords.append(temp_record)
                thirty = 0
                temp_record = ''

            thirty += obj.size
            ctr += obj.size

        # the actual writing
        f = open("../tests/"+outFileName, "w")
        f.write(header[:-1]) #1 '|' at the end
        f.write('\n')
        for rec in textRecords[:-1]:
            f.write(rec[:-3])   #since there are 2 erroneous '|' at the end of each text record
        f.write('\n')
        f.write(end[:-1])     #1 '|' at the end
        f.close()


    def observe(self):
        print("[location, programCounter, size, label, instruction, instructionType, ",
        "args, targetAddress, binary]")
        for obj in g.line_objects:
            pprint.pprint([obj.location, obj.programCounter, obj.size, obj.label, obj.instruction,
            obj.instructionType, obj.args, obj.targetAddress, obj.binary])
        print(g.symtab)

    def showErrors(self):
        print("\n\n Start of error list")
        for line_obj in g.line_objects:
            if len(line_obj.errors) != 0:
                print("Instruction: ", line_obj.raw, line_obj.errors)
        print("\n End of error list")
