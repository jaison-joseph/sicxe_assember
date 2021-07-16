import global_vars as g
import tools as t
import Line
import pass_1 as p1
import pass_2 as p2
import sys
import traceback
import pprint as pp

class controlSection():

    def __init__(self, input):
        self.name = input
        self.littab = {}
        self.symtab = {}
        self.program_block_details = {}
        self.line_objects = []
        self.current_block = 0
        self.startLocation = 0
        self.errorCount = 0
        self.warningCount = 0
        self.literalsToProcess = False

    def getErrorCount(self):
        return sum([len(obj.errors) for obj in self.line_objects])

    def getWarningCount(self):
        return sum([len(obj.warnings) for obj in self.line_objects])

    def addLine(self, input):
        try:
            line_obj = Line.Line(input)
            self.ln_pass_1(g.locctr, line_obj)
        except:
            print("error:", sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2])
            print("\n\n instruction details:", line_obj.__dict__)
            self.dump()
            exit(0)
        if len(line_obj.errors) != 0:
            print("Errors found in pass 1. Printing possible warnings/errors")
            pp.pprint(line_obj.__dict__)
            for i in range(index-1, -1, -1):
                if len(self.line_objects[i].warnings) != 0:
                    self.ln_printWarnings(i+1, self.line_objects[i])
                if len(self.line_objects[i].errors) != 0:
                    self.ln_printErrors(i+1, self.line_objects[i])
            exit(0)
        self.line_objects.append(line_obj)
        if len(self.line_objects) == 1:
            if line_obj.instruction == "START":
                g.locctr = g.start_address
                line_obj.location = g.start_address
            if line_obj.instruction != 'USE':
                self.program_block_details[0] = ["default",g.locctr,0]
        g.locctr += line_obj.size

    # to be called at the end of pass 1
    def wrapUp(self):
        if (self.literalsToProcess):
            self.cleanUpLittab()
        self.cleanUpProgramBlock()

    # this takes care of literals that still have to be processed by an LTORG
    # if any literals are unprocessed, we just place an LTORG instruction at the end of the current ctrl section
    def cleanUpLittab(self):
        try:
            imaginary_instruction = Line.Line("LTORG")
            self.ln_pass_1(g.locctr, imaginary_instruction)
            self.line_objects.append(imaginary_instruction)
        except:
            print("error happened during cleanUpLittab")
            print("\n\n the littab")
            pp.pprint(self.littab)
            exit(0)

    # this method is to set the length of the last program block
    def cleanUpProgramBlock(self):
        last = self.program_block_details[len(self.program_block_details)-1]
        last[2] = g.locctr - last[1]#setting the length of the program block
        self.program_block_details[len(self.program_block_details)-1] = last

    def pass_2(self):
        for index, line_obj in enumerate(self.line_objects):
            if index != len(self.line_objects)-1:   #since the last instruction has nothing after it
                self.line_objects[index].programCounter = self.line_objects[index+1].location
            try:
                if (not self.ln_pass_2(line_obj)):
                    print("Errors found in pass 2. Printing possible warnings/errors")
                    # pp.pprint(self.line_objects[i].__dict__)
                    self.ln_printWarnings(index+1, self.line_objects[index])
                    self.ln_printErrors(index+1, self.line_objects[index])
                    exit(0)
            except:
                print("error:", sys.exc_info()[:2])
                traceback.print_tb(sys.exc_info()[2])
                print("\n\n instruction details:", line_obj.__dict__)
                print("\n\n dumping all the control section info: \n")
                self.dump()
                exit(0)

        pp.pprint(self.symtab)

    def dump(self):

        line_obj_pad = [4, 6, 4, 12, 4, 18, 10]
        line_obj_desc = ['loc', 'label' , 'pc', 'instruction',
        'TA', 'args', 'binary']
        print("\n\n the line objects")
        for i in range(len(line_obj_desc)):
            line_obj_desc[i] = t.pad(line_obj_desc[i], line_obj_pad[i])
        print(line_obj_desc)
        for obj in self.line_objects:
            temp = [hex(obj.location)[2:], obj.label, hex(obj.programCounter)[2:],
            obj.instruction, hex(obj.targetAddress)[2:], obj.args, obj.binary]
            # temp = [obj.location, obj.label, obj.programCounter,
            # obj.instruction, obj.targetAddress, obj.args, obj.binary]
            for i in range(len(temp)):
                temp[i] = t.pad(temp[i], line_obj_pad[i])
            print(temp)

        symtab_pad = [10, 4, 12, 6, 20, 8]
        symtab_desc = ["label", "loc", "type", "value", "[relative/absolute]", "block no"]
        print("\n\n the symtab")
        for i in range(len(symtab_desc)):
            symtab_desc[i] = t.pad(symtab_desc[i], symtab_pad[i])
        print(symtab_desc)
        for k in self.symtab.keys():
            temp = [k] + list(self.symtab[k])
            for i in range(len(temp)):
                temp[i] = t.pad(temp[i], symtab_pad[i])
            print(temp)
        print("\n\n the littab")
        print("'literal' : [location, block number]")
        pp.pprint(self.littab)

        print("\n\n the program block details")
        print("'number' : [name, start address length]")
        pp.pprint(self.program_block_details)

    def showErrors(self):
        print("\n\n Start of error list")
        for line_obj in self.line_objects:
            if len(line_obj.errors) != 0:
                print("Instruction: ", line_obj.raw, line_obj.errors)
        print("\n End of error list")

    # returns all the records that go into the output file
    def getRecords(self):
        debug = True
        textRecords = []
        modRecords = []

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
        for obj in self.line_objects:
            if obj.isUselessLine:
                continue
            if obj.instructionType == "EXTENDED INSTRUCTION" and obj.addressMode == "DIRECT":
                newRec = 'M'
                relativeLoc = hex(obj.location - g.start_address + 1)[2:]
                relativeLoc = t.pad(relativeLoc, 6, "r", '0')
                length = t.pad(5, 2, "r", '0')  #5 hex long address space
                if debug:
                    newRec += '|' + relativeLoc + '|' + length
                else:
                    newRec += relativeLoc + length
                modRecords.append(newRec)
            if ((obj.binary == -1 and obj.size != 0) or thirty + obj.size > 30) and thirty != 0:
                try:
                    startAddress = t.pad(hex(startAddress)[2:], 6, 'r', '0')
                except TypeError:
                    print("\n the types are: ", startAddress)
                    print("\n the types are: ", type(startAddress))
                    exit(0)
                tempSize = t.pad(hex(thirty)[2:], 2, 'r', '0')
                if debug:
                    temp_record = 'T' + '|' + startAddress + '|' + tempSize + '|' + temp_record
                else:
                    temp_record = 'T' + startAddress + tempSize + temp_record
                textRecords.append(temp_record)
                temp_record = ''
                thirty = 0
            if obj.binary != -1:
                if thirty == 0:
                    startAddress = obj.location
                    print("ooolala:", type(startAddress))
                thirty += obj.size
                temp_record += obj.binary
                if debug:
                    temp_record += '|'

        if thirty != 0:
            print ("incorporating the leftovers")
            tempSize = t.pad(hex(thirty)[2:], 2, "r", '0')
            startAddress = t.pad(hex(startAddress)[2:], 6, "r", '0')
            if debug:
                temp_record = 'T' + '|' + startAddress + '|' + tempSize + '|' + temp_record
            else:
                temp_record = 'T' + startAddress + tempSize + temp_record
            textRecords.append(temp_record)

        result = ''

        for rec in textRecords:
            result += rec
            result += '\n'
        for rec in modRecords:
            result += rec
            result += '\n'

        return result

    #the definitions can be found in Line_2
    ln_pass_1 = p1.pass_1_
    ln_arg_check = p1.arg_check_
    ln_getExpressionValue = p1.getExpressionValue_
    ln_processInstruction = p2.processInstruction_
    ln_directiveHandler = p1.directiveHandler_
    ln_getCorrespondingNumber = p1.getCorrespondingNumber_

    ln_pass_2 = p2.pass_2_
    ln_getRelative = p2.getRelative_
    ln_build_instruction = p2.build_instruction_
    ln_getTargetAddress = p2.getTargetAddress_
    ln_printWarnings = p2.printWarnings_
    ln_printErrors = p2.printErrors_
    ln_get_immediate = p2.get_immediate_
    ln_get_direct_ = p2.get_direct_
    ln_get_indirect = p2.get_indirect_
