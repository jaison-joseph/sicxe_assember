import global_vars as g
import tools as t
import pass_1 as p1
import pass_2 as p2

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

    def pass_1(self, location):

        self.location = location

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
            self.directiveHandler()

        #check if its a command from optable
        else:
            #extended format command
            try:
                self.instructionDetails = g.optable[self.instruction]
                self.instructionType = "INSTRUCTION"
                if self.instructionDetails[0] != 'm':
                    self.size = int(self.instructionDetails[1])
                else:
                    self.size = 3
            except KeyError:
                try:
                    if self.instruction[0] != '+':
                        raise KeyError
                    self.instructionDetails = g.optable[self.instruction[1:]]
                    if self.instructionDetails[1] != '3/4':
                        self.errors.append("Command:", self.instruction, "cannot be used in extended mode")
                        return
                    self.instructionType = "EXTENDED INSTRUCTION"
                    self.size = 4
                except KeyError:
                    self.errors.append("Instruction:", self.instruction, "is invalid")
                    return

            if self.label != -1:
                # g.symtab.append([self.label, self.location, "WORD_CONST", word_value, absolute/relative])
                g.symtab[self.label] = (self.location, "INSTRUCTION", -1, "R")

            self.arg_check()

    def pass_2(self):
        if self.instructionType == "DIRECTIVE":
            pass
        #argument check: that the number and type of argument matches
        else:
            self.getTargetAddress()
            if len(self.errors) != 0:
                return False
            self.processInstruction()
            if len(self.errors) != 0:
                return False
            self.build_instruction()
            if len(self.errors) != 0:
                return False
        return True


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
    arg_check = p1.arg_check_
    getExpressionValue = p1.getExpressionValue_
    processInstruction = p2.processInstruction_
    directiveHandler = p1.directiveHandler_
    getRelative = p2.getRelative_
    build_instruction = p2.build_instruction_
    getTargetAddress = p2.getTargetAddress_
