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

        self.fileName = fileName
        self.control_sections = {}

    def run(self):
        self.pass_1()
        self.pass_2()

    def pass_1(self):
        f = open("../tests/"+self.fileName)
        csect = controlSection.controlSection("")
        for index, ln in enumerate(f):
            csect.addLine(ln)
            if csect.line_objects[-1].instruction == 'CSECT':
                if index != 0:
                    csect.wrapUp()
                    self.control_sections[csect.name] = csect
                    # in a CSECT instruction, the label contains the name of the new CSECT
                    newSectName = csect.v.line_objects[-1].label
                    if newSectName in self.control_sections.keys():
                        print("control section name:", newSectName, "has been used already")
                        exit(0)
                    csect = controlSection(newSectName)   #re setting the variable
                    csect.startLocation = g.locctr
                else:
                    # there is only one line in the current ctrl sect, so -1 still works
                    csect.name = csect.v.line_objects[-1].label
        csect.wrapUp()
        self.control_sections[csect.name] = csect
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

        for csect_name in self.control_sections.keys():
            csect = self.control_sections[csect_name].pass_2()


    def dump(self):
        for csect_name in self.control_sections.keys():
            print("\n\n printing the control section details of:", csect_name, "\n")
            self.control_sections[csect_name].dump()
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
