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
