import Line
import controlSection
import pprint
import global_vars as g
import tools as t
import sys
import traceback

pp = pprint.PrettyPrinter()

class Program():

    def __init__(self, fileName):

        self.control_sections = {}
        self.csect_ = controlSection("")

    def run(self):
        f = open("../tests/"+fileName)
        for index, ln in enumerate(f):
            csect_.addLine(ln)


            if csect_.line_objects[-1].instruction == 'CSECT':
                if index != 0:
                    csect_.wrapUp()
                    self.control_sections[self.name] = csect_
                    # in a CSECT instruction, the label contains the name of the new CSECT
                    newSectName = csect_.line_objects[-1].label
                    if newSectName in self.control_sections.keys():
                        print("control section name:", newSectName, "has been used already")
                        exit(0)
                    csect_ = controlSection(newSectName)
                else:
                    # there is only one line in the current ctrl sect, so -1 still works
                    csect_.name = csect_.line_objects[-1].label

            if len(line_obj.errors) != 0:
                print("Errors found in pass 1. Printing possible warnings/errors")
                pp.pprint(line_obj.__dict__)
                for i in range(index-1, -1, -1):
                    if len(g.line_objects[i].warnings) != 0:
                        g.line_objects[i].printWarnings(i+1)
                    if len(g.line_objects[i].errors) != 0:
                        g.line_objects[i].printErrors(i+1)
                exit(0)
            g.line_objects.append(line_obj)
            g.locctr += line_obj.size
            if index == 0:
                if line_obj.instruction == "START":
                    g.locctr += g.start_address
                    line_obj.location = g.start_address
                if line_obj.instruction != 'CSECT':
                    print("hit the set up for program block!")
                    g.program_block_details[0] = ["default",g.locctr,0]
        self.cleanUpProgramBlock()
        self.cleanUpLittab()

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

    def cleanUpLittab(self):
        try:
            if (g.literalsToProcess):
                imaginary_instruction = Line.Line("LTORG")
                imaginary_instruction.pass_1(g.locctr)
                g.line_objects.append(imaginary_instruction)
        except:
            print("\n\n the littab")
            pprint.pprint(g.littab)
            exit(0)


    def cleanUpProgramBlock(self):
        last = g.program_block_details[len(g.program_block_details)-1]
        last[2] = g.locctr - last[1]#setting the length of the program block
        g.program_block_details[len(g.program_block_details)-1] = last

    def pass_2(self):

        print("\n\n the littab")
        pprint.pprint(g.littab)
        print("\n\n")

        for index, line_obj in enumerate(g.line_objects):
            if index != len(g.line_objects)-1:
                g.line_objects[index].programCounter = g.line_objects[index+1].location
            try:
                if (not line_obj.pass_2()):  #since the last instruction has nothing after it
                    print("Errors found in pass 2. Printing possible warnings/errors")
                    # pp.pprint(g.line_objects[i].__dict__)
                    g.line_objects[index].printWarnings(index+1)
                    g.line_objects[index].printErrors(index+1)
                    exit(0)
            except:
                print("error:", sys.exc_info()[:2])
                traceback.print_tb(sys.exc_info()[2])
                print("\n\n instruction details:", line_obj.__dict__)
                exit(0)

    def outputSave(self, fileName):
        debug = True
        header = 'H'
        textRecords = []
        modRecords = []
        end = 'E'

        #the header bit
        first = g.line_objects[0]
        name = ' ' * 6
        progStartAddress = t.pad(hex(g.start_address)[2:], 6, "r", '0')
        # if first.instruction == 'START' and first.label != -1:
        #     name = first.label
        #     while len(name) < 6:
        #         name = ' ' + name
        # if first.instruction == "START":
        #     progStartAddress = first.args
        progSize = hex(g.locctr)[2:]
        if debug:
            header += '|' + name + '|' + progStartAddress + '|' + progSize
        else:
            header += name + progStartAddress + progSize

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

        # the actual writing
        f = open("../tests/"+fileName, "w")
        f.write(header) #1 '|' at the end
        f.write('\n')
        for rec in textRecords:
            f.write(rec)   #1 erroneous '|' at the end of each text record
            f.write('\n')
        for rec in modRecords:
            f.write(rec)   #1 erroneous '|' at the end of each text record
            f.write('\n')
        f.write(end)     #1 '|' at the end
        f.close()


    def observe(self):

        line_obj_pad = [4, 8, 12, 4, 20, 10]
        line_obj_desc = ['loc', 'label' ,'instruction', 'TA',
        'args', 'binary']
        print("\n\n the line objects")
        for i in range(len(line_obj_desc)):
            line_obj_desc[i] = t.pad(line_obj_desc[i], line_obj_pad[i])
        print(line_obj_desc)
        for obj in g.line_objects:
            temp = [hex(obj.location)[2:], obj.label, obj.instruction,
            obj.targetAddress, obj.args, obj.binary]
            for i in range(len(temp)):
                temp[i] = t.pad(temp[i], line_obj_pad[i])
            print(temp)

        symtab_pad = [10, 4, 12, 6, 20, 8]
        symtab_desc = ["label", "loc", "type", "value", "[relative/absolute]", "block no"]
        print("\n\n the symtab")
        for i in range(len(symtab_desc)):
            symtab_desc[i] = t.pad(symtab_desc[i], symtab_pad[i])
        print(symtab_desc)
        for k in g.symtab.keys():
            temp = [k] + list(g.symtab[k])
            for i in range(len(temp)):
                temp[i] = t.pad(temp[i], symtab_pad[i])
            print(temp)
        print("\n\n the littab")
        print("'literal' : [location, block number]")
        pp.pprint(g.littab)

    def showErrors(self):
        print("\n\n Start of error list")
        for line_obj in g.line_objects:
            if len(line_obj.errors) != 0:
                print("Instruction: ", line_obj.raw, line_obj.errors)
        print("\n End of error list")
