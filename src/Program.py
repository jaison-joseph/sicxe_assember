import Line
import controlSection
import pprint
import global_vars as g
import tools as t
import sys
import traceback

pp = pprint.PrettyPrinter()

class Program():

    def __init__(self, inputFileName, outputFileName):

        self.inputFileName = inputFileName
        self.outputFileName = outputFileName
        self.control_sections = {}

    def run(self):
        self.pass_1()
        self.pass_2()
        self.outputSave()

    def pass_1(self):
        f = open("../tests/"+self.inputFileName)
        csect = controlSection.controlSection("")
        g.current_csect = ''
        for index, ln in enumerate(f):
            csect.addLine(ln)
            if csect.line_objects[-1].instruction != 'CSECT':
                continue
            print("\n\n ENCOUNTERED A NEW CTRL SECTION \n\n")
            csect.wrapUp()
            self.control_sections[csect.name] = csect
            # in a CSECT instruction, the label contains the name of the new CSECT
            g.current_csect = newSectName = csect.line_objects[-1].label
            if newSectName in self.control_sections.keys():
                print("control section name:", newSectName, "has been used already")
                exit(0)
            csect = controlSection.controlSection(newSectName)   #re setting the variable
            csect.startLocation = g.locctr
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


    def outputSave(self):
        debug = True
        header = 'H'
        end = 'E'

        #the header bit
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

        # the actual writing
        f = open("../tests/"+self.outputFileName, "w")
        f.write(header) #1 '|' at the end
        f.write('\n')
        for csect_name in self.control_sections.keys():
            f.write(self.control_sections[csect_name].getRecords())
        f.write(end)
        f.close()
