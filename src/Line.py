import global_vars as g
import tools as t
import pass_1 as p1
import pass_2 as p2
import controlSectionVars

import re
from math import ceil
class Line():

    #constructor; ALL non-boolean variables default as -1;
    #all boolean vars are by default False
    #except for args[], warnings[] and errors[]
    def __init__(self, input, cSectVar):

        #the only non-default thing done in this function
        self.raw = input
        self.vars = cSectVar

        #pass 1
        self.label = -1
        self.content = -1
        self.instruction = -1
        self.instructionType = -1
        self.args = ''
        self.comment = -1
        self.instructionDetails = -1  #from the optable if the given line is an instruction
        self.location = -1        #the value of locctr when its at this line
        self.programCounter = -1        #the value of locctr when its at this line
        self.size = -1   #by how much would locctr increase because of this line, bytes
        self.isDirective = False
        self.isRelative = False
        self.isUselessLine = False

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

        if len(self.content) == 0:      #the line is entirely a comment
            self.isUselessLine = True
            self.size = 0
            return

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
            try:
                #extended format command
                if self.instruction[0] == '+':
                    self.instructionDetails = g.optable[self.instruction[1:]]
                    if self.instructionDetails[0] != 'm':
                        self.errors.append("This instruction cannot be used in extended mode")
                        return
                else:
                    self.instructionDetails = g.optable[self.instruction]
            except KeyError:
                self.errors.append("Instruction:", self.instruction, "is invalid")
                return
            self.instructionType = "INSTRUCTION"
            #setting the size of the instruction based on the instruction details
            try:
                self.size = int(self.instructionDetails[1])
            # for some instructions, the size is given as '3/4' since it could be extended
            except ValueError:
                if self.instruction[0] == '+':
                    self.size = 4
                    self.instructionType = "EXTENDED INSTRUCTION"
                else:
                    self.size = 3

            if self.label != -1:
                # vars.symtab.append([self.label, self.location, "WORD_CONST", word_value, absolute/relative])
                vars.symtab[self.label] = (self.location, "INSTRUCTION", -1, "R", self.vars.current_block)

            self.arg_check()


    def pass_2(self):
        if self.isUselessLine:
            pass
        elif self.instructionType == "DIRECTIVE":
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
        if self.isUselessLine:
            return
        self.location = location
        if len(vars.symtab) != 0:
            if vars.symtab.get(self.label):
                temp = list(vars.symtab[self.label])
                temp[0] = self.location
                vars.symtab[self.label] = tuple(temp)

    def setProgramCounter(self, locctr):
        if self.isUselessLine:
            return
        self.programCounter = locctr

    def printWarnings(self):
        if self.isUselessLine:
            return
        if len(self.warnings) != 0:
            print("all the beans:", self.__dict__)
            print(self.warnings)

    def printErrors(self):
        if self.isUselessLine:
            return
        if len(self.errors) != 0:
            print("all the beans:", self.__dict__)
            print(self.errors)

    #the definitions can be found in Line_2.py
    arg_check = p1.arg_check_
    getExpressionValue = p1.getExpressionValue_
    processInstruction = p2.processInstruction_
    directiveHandler = p1.directiveHandler_
    getRelative = p2.getRelative_
    build_instruction = p2.build_instruction_
    getTargetAddress = p2.getTargetAddress_
