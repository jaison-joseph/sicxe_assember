import global_vars as g
import tools as t
import Line_2 as extension

import re
from math import ceil
class Line():

    #constructor; ALL non-boolean variables default as -1;
    #all boolean vars are by default False
    #except for args[], warnings[] and errors[]
    def __init__(self, input):

        #the only non-default thing done in this function
        self.raw = input

        #pass 1
        self.label = -1
        self.content = -1
        self.instruction = -1
        self.instructionType = -1
        self.args = []
        self.comment = -1
        self.instructionDetails = -1  #from the optable if the given line is an instruction
        self.location = -1        #the value of locctr when its at this line
        self.programCounter = -1        #the value of locctr when its at this line
        self.size = -1   #by how much would locctr increase because of this line, bytes
        self.isDirective = False
        self.isRelative = False

        #pass 2
        self.targetAddress = -1
        self.display = -1
        self.addressMode = -1
        self.isIndexed = False
        self.binary = -1    #the final string that gets added to the outout executable

        #pass 1 AND pass 2
        self.warnings = []
        self.errors = []

    def pass_1(self):
        #split the line into <content> <comments>
        loc = self.raw.find('.')
        if loc != -1:
            self.comment = self.raw[loc:]
            self.content = self.raw[:loc]
        else:
            self.content = self.raw[:-1]
            if self.raw[-1] != '\n':
                self.content = self.raw

        #split the <content> into <label> <instruction> <args>
        slices = [x for x in self.content.split('\t') if x != '']
        if len(slices) == 2:
            self.instruction = slices[0]
            self.args = slices[1]
        elif len(slices) == 3:
            self.label = slices[0]
            self.instruction = slices[1]
            self.args = slices[2]
        else:
            self.instruction = slices[0]

        #get size of instruction

        # if instruction is a directive
        if self.instruction in g.directives:
            self.isDirective = True
            self.instructionType = "DIRECTIVE"
            self.size = 0

            details = t.info(self.args, "all")
            #some directives allocate memory; we check if that is the case
            #and proceed to correct the size demanded by the line

            if self.instruction == 'RESW':
                if details["type"] != "int":
                    self.errors.append("Invalid argument for instruction")
                    return
                self.size = int(details["content"]) * 3
                if (self.label == -1):
                    self.warnings.append("RESW instruction has no label for it")
                    return
                g.symtab[self.label] = (self.location, "WORD", -1)

            elif self.instruction == 'RESB':
                if details["type"] != "int":
                    self.errors.append("Invalid argument for instruction")
                    return
                self.size = int(details["content"])
                # self.instructionType = "BYTE"
                if (self.label == -1):
                    self.warnings.append("RESB instruction has no label for it")
                    return
                g.symtab[self.label] = (self.location, "BYTE", -1)

            elif self.instruction == 'WORD':
                #assert that the instruction args ar valid
                if details["type"] != "int":
                    self.errors.append("value for WORD must be an int")
                    return
                word_value = int(details["content"], 16)
                if (word_value < 0 or word_value > 2**24-1):      #a wword is 3 bytes long; hence the upper bound
                    self.errors.append("value for word is out of bounds")
                    return
                self.size = 3
                if (self.label == -1):
                    self.warnings.append("WORD instruction has no label for it")
                    return
                g.symtab[self.label] = (self.location, "WORD_CONST", word_value)

            elif self.instruction == 'BYTE':
                #assert that the instruction args ar valid
                if details["type"] != "int":
                    self.errors.append("value for BYTE must be an int")
                    return
                self.size = details["size"]
                if (self.label == -1):
                    self.warnings.append("BYTE instruction has no label for it")
                    return
                g.symtab[self.label] = (self.location, "BYTE_CONST",  details["content"])


        #check if its a command from optable
        else:
            extended = False
            #extended format command
            try:
                if self.instruction[0] == '+':
                    extended = True
                # only commands of sicxe (size 3) can be extended
                if extended:
                    if self.instructionDetails[1] == '3/4':
                        self.instructionDetails = g.optable[self.instruction[1:]]
                        self.instructionType = "EXTENDED INSTRUCTION"
                        self.size = 4
                    else:
                        self.errors.append("Command:", self.instruction, "cannot be used in extended mode")
                        return
                else:
                    self.instructionDetails = g.optable[self.instruction]
                    self.instructionType = "INSTRUCTION"
                    self.size = 3
            except KeyError:    #invalid instructions land here
                self.errors.append("Instruction:", self.instruction, "is invalid")
                return

            if self.label != -1:
                # g.symtab.append([self.label, self.location, "WORD_CONST", word_value])
                g.symtab[self.label] = (self.location, "INSTRUCTION", -1)

    def update_symtab(self, location):
        self.location = location
        if len(g.symtab) != 0:
            if g.symtab.get(self.label):
                temp = list(g.symtab[self.label])
                temp[0] = self.location
                g.symtab[self.label] = tuple(temp)

    def setProgramCounter(self, locctr):
        self.programCounter = locctr

    def printWarnings(self, num):
        if len(self.warnings) != 0:
            print("Line",num,":",self.warnings)

    def printErrors(self, num):
        if len(self.errors) != 0:
            print("Line",num,":",self.errors)

    #the definitions can be found in Line_2.py
    arg_check = extension.arg_check_
    processInstruction = extension.processInstruction_
    directiveHandler = extension.directiveHandler_
    getRelative = extension.getRelative_
    build_instruction = extension.build_instruction_
    directiveHandler = extension.directiveHandler_
    pass_2 = extension.pass_2_

# print("__name__ from line.py is: ", __name__)

"""
try:
    #extended format command
    if self.instruction[0] == '+':
        index = g.instruction_names.index(self.instruction[1:])
        self.instructionDetails = g.optable[index]
        # only commands of sicxe (size 3) can be extended
        if self.instructionDetails[2] == '3/4':
            self.size = 4
        else:
            self.errors.append("Command:", self.instruction, "cannot be used in extended mode")
            return

    else:
        index = g.instruction_names.index(self.instruction)
        self.instructionDetails = g.optable[index]
        if self.instructionDetails[2] == '3/4':
            self.size = 3
        else:
            self.size = int(self.instructionDetails[2])

    if self.label != -1:
        # g.symtab.append([self.label, self.location, "WORD_CONST", word_value])
        g.symtab.append([self.label, self.location, "INSTRUCTION", -1])
except ValueError:
    self.errors.append("Invalid instruction; neither directive nor command from optable")
    return
"""
