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

        print("\n\n the littab")
        pprint.pprint(g.littab)
        print("\n\n")

        for index, line_obj in enumerate(g.line_objects):
            if index != len(g.line_objects)-1:
                g.line_objects[index].programCounter = g.line_objects[index+1].location
            if ( not line_obj.pass_2()):  #since the last instruction has nothing after it
                print("Errors found in pass 2. Printing possible warnings/errors")
                # pp.pprint(g.line_objects[i].__dict__)
                g.line_objects[index].printWarnings(index+1)
                g.line_objects[index].printErrors(index+1)
                exit(0)

    def outputSave(self, fileName):
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
        if debug:
            header = name + '|' + progStartAddress + '|' + progSize

        #the end record
        if debug:
            end += '|'
        end += progStartAddress

        '''
        text reord logic

        set thirty = 0
        set temp = ''

        1. iterate through the records
            if the new record doesnt have a binary of -1:
                a. if the current rec +size(new rec binary) > 30:
                        add the size of temp to temp
                        add temp to list or records and clear temp and thirty
                b. if thirty == 0:
                        set up the starting address for temp
                add the binary to temp
                thirty += size of binary
        2. at the end of loop, if thirty != 0
            add the size of temp to temp
            add temp to list or records and clear temp and thirty
        '''

        #the text records
        thirty = 0  #to know when we reached the length limit for a locctr
        temp_record = ''
        startAddress = -1
        for obj in g.line_objects:
            if obj.binary != -1:
                if thirty + obj.size > 30:
                    print("we hit the limit")
                    tempSize = str(thirty)
                    if len(tempSize) < 2:
                        tempSize = '0' + tempSize
                    startAddress = hex(startAddress)[2:]
                    while len(startAddress) < 6:
                        startAddress = '0' + startAddress
                    if debug:
                        temp_record = 'T' + '|' + startAddress + '|' + tempSize + '|' + temp_record
                    else:
                        temp_record = 'T' + startAddress + tempSize + temp_record
                    textRecords.append(temp_record)
                    temp_record = ''
                    thirty = 0
                if thirty == 0:
                    startAddress = obj.location
                thirty += obj.size
                temp_record += obj.binary
                if debug:
                    temp_record += '|'

        if thirty != 0:
            print ("incorporating the leftovers")
            tempSize = str(thirty)
            if len(tempSize) < 2:
                tempSize = '0' + tempSize
            startAddress = hex(startAddress)[2:]
            while len(startAddress) < 6:
                startAddress = '0' + startAddress
            if debug:
                temp_record = 'T' + '|' + startAddress + '|' + tempSize + '|' + temp_record
            else:
                temp_record = 'T' + startAddress + tempSize + temp_record
            textRecords.append(temp_record)

        # the actual writing
        f = open("../tests/"+fileName, "w")
        f.write(header) #1 '|' at the end
        f.write('\n')
        for rec in textRecords:
            f.write(rec)   #1 erroneous '|' at the end of each text record
            f.write('\n')
        f.write(end)     #1 '|' at the end
        f.close()


    def observe(self):
        print("[location, programCounter, size, label, instruction, instructionType, addressMode, ",
        "args, targetAddress, binary]")
        for obj in g.line_objects:
            pprint.pprint([obj.location, obj.programCounter, obj.size, obj.label, obj.instruction,
            obj.instructionType, obj.addressMode, obj.args, obj.targetAddress, obj.binary])
        print("\n\n the symtab")
        print('{label}: (location, type, value, type[relative/absolute])')
        pp.pprint(g.symtab)
        print("\n\n the littab")
        print("'literal' : location")
        pp.pprint(g.littab)

    def showErrors(self):
        print("\n\n Start of error list")
        for line_obj in g.line_objects:
            if len(line_obj.errors) != 0:
                print("Instruction: ", line_obj.raw, line_obj.errors)
        print("\n End of error list")
