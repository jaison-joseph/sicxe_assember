import global_vars as g
import tools as t

#checks the number and type of arguments
#also gets the target address, if needed
def arg_check_(self):
    #to check that the number of arguments match
    self.args = self.args.split(",")
    arg_type = self.instructionDetails[0]
    # for a type match
    arg_1 = ''
    arg_2 = ''

    #number of args check
    if self.args == [''] and arg_type == '0':
        pass
    else:
        if ',' in arg_type:
            if len(self.args) == 2:
                arg_1 = self.args[0]
                arg_2 = self.args[1]
            else:
                self.errors.append("Instruction does not have the correct number of arguments. "+
                "Expected 2; got:",len(self.args))
                return
        else:
            arg_1 = self.args[0]
            if len(self.args) == 2:
                if self.args[1] == 'X':
                    arg_2 = self.args[1]
                    self.isIndexed = True
                else:
                    self.errors.append("Instruction does not have the correct number of arguments. "+
                    "Expected 1; got:"+str(len(self.args)))
                    return

    # print("instruction:", self.instruction)
    # print("arg_type:", arg_type)
    # print("arg_1:", arg_1)
    # print("arg_2:", arg_2)

    #check the type match
    if arg_type == 'm':

        #get addressing mode; change TA accordingly
        #if immediate, need to get the value of the operand
        if arg_1[0] == '#':
            try:
                num = int(arg_1[1:])
                if num < 0:
                    self.errors.append("const argument", arg_1, " must be >= 0")
                    return
                self.targetAddress = num
                self.addressMode = "IMMEDIATE CONST"
            except ValueError:

                self.addressMode = "IMMEDIATE"

        # indirect addressing
        elif arg_1[0] == '@':
            self.addressMode = "INDIRECT"

        # literal pool
        elif arg_1[0] == '=':
            details = t.info(arg_1[1:], "all")
            print("details:", details)
            if details["type"] != "char" and details["type"] != "hex":
                self.errors.append("invalid argument for literal constant; must be a hex or char")
                return
            self.addressMode = "DIRECT"
            # if self.targetAddress == -1:
            #     self.errors.append("literal argument " + arg_1[1:] + " target address not set up")
            #     return
            if details["content"] in g.littab.keys():
                g.littab[details["content"]][1].append(self.location)
            else:
                g.littab[details["content"]] = [details, [self.location]]

        #direct addressing mode
        else:
            self.addressMode = "DIRECT"


    #this is just the SVC instruction

    elif arg_type == 'n':
        try:
            self.targetAddress = int(arg_1)
        except ValueError:
            #so it is not a number; check if it is a valid
            self.errors.append("Argument:", arg_1, " must be an integer for the given instruction")
            return

    elif arg_type == 'r1,n':
        #check that the register is a valid one
        if arg_1 not in g.registers.keys():
            self.errors.append("Argument:", arg_1, " must be a register name")
            return
        try:
            num = int(arg_2)
            if 0x1 < num < 0x10 == False:
                self.errors.append("Argument:", arg_2, " must be a in [1,16]")
                return
        except ValueError:
            self.errors.append("Argument:", arg_2, " must be an integer in [1,16]")
            return

    elif arg_type == 'r1,r2':
        if arg_1 not in g.registers.keys():
            self.errors.append("Argument:", arg_1, " must be a register name")
            return
        if arg_2 not in g.registers.keys():
            self.errors.append("Argument:", arg_2, " must be a register name")
            return

    elif arg_type == "r1":
        if arg_1 not in g.registers.keys():
            self.errors.append("Argument:", arg_1, " must be a register name")
            return

    elif arg_type == '0':
        pass

    if self.isIndexed:
        if arg_type != 'm':
            self.errors.append("Instruction", self.instruction, " does not support indexed addressing")
            return
        if self.addressMode != "DIRECT":
            self.errors.append("Instruction", self.instruction, "'s addressing mode cannot use indexed addressing")
            return
        pass

def directiveHandler_(self):

    details = t.info(self.args, "all")

    if self.instruction == 'START':
        if details["type"] == "int":
            g.start_address = int(details["content"], 16)
        else:
            self.errors.append("Invalid argument for the start instruction; must be a hex value")
            return
        if start_address > 2**20-1:
            self.errors.append("SICXE compouters only have 1 mb of memory; given start location exceeds 1 mb limit")
            return

    elif self.instruction == 'END':
        pass

    elif self.instruction == 'RESW':
        if details["type"] != "int":
            self.errors.append("Invalid argument for instruction")
            return
        try:
            self.size = int(details["content"]) * 3
        except ValueError:
            self.errors.append(" invalid argument for RESW; must be an integer (not a hex)")
            return
        if (self.label == -1):
            self.warnings.append("RESW instruction has no label for it")
            return
        g.symtab[self.label] = (self.location, "WORD", -1)

    elif self.instruction == 'RESB':
        if details["type"] != "int":
            self.errors.append("Invalid argument for instruction")
            return
        try:
            self.size = int(details["content"])
        except ValueError:
            self.errors.append(" invalid argument for RESB; must be an integer (not a hex)")
            return
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
        #asserting that the word value is within bounds
        if (word_value < 0 or word_value > 2**24-1):      #a word is 3 bytes long; hence the upper bound
            self.errors.append("value for word is out of bounds")
            return
        self.size = 3
        #if the label is absent, we cant add it to the symtab
        if (self.label == -1):
            self.warnings.append("WORD instruction has no label for it")
            return
        value = details["content"]
        while 2*len(value) < self.size:
            value = '0'+ value
        self.binary = value
        g.symtab[self.label] = (self.location, "WORD_CONST", value)

    elif self.instruction == 'BYTE':
        #assert that the instruction args ar valid
        if details["type"] != "char" or details["type"] != "hex":
            self.errors.append("value for BYTE must be a char/hex const")
            return
        self.size = details["size"]
        if (self.label == -1):
            self.warnings.append("BYTE instruction has no label for it")
            return
        value = details["content"]
        if (details['type'] == 'hex'):
            while len(value) < 2*self.size:
                value = '0'+ value
        else:
            while len(value) < self.size:
                value = '0' + value
        self.binary = value
        g.symtab[self.label] = (self.location, "BYTE_CONST",  value)

    elif self.instruction == 'EXTDEF':
        pass

    elif self.instruction == 'EXTREF':
        pass

    elif self.instruction == 'LTORG':
        print("littab", g.littab)
        if len(g.littab) == 0:
            self.warnings.append("LTORG was called, but no literals encountered yet")
            return
        #assign mem locations to the variables on the littab
        for literal in g.littab.keys():
            locations = g.littab[literal][1]
            details = g.littab[literal][0]
            print("literal details: ", details)
            g.littab[literal] = g.locctr
            if len(locations) != 0:
                self.binary = ''
            for loc in locations:
                for obj in g.line_objects:
                    if obj.location == loc:
                        obj.targetAddress = g.locctr
                        break
            self.size += details["size"]
            self.binary += details["content"]
    elif self.instruction == 'EQU':
        pass

    elif self.instruction == 'CSECT':
        pass
