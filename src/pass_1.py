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
            # print("details:", details)
            if details["type"] != "char" and details["type"] != "hex":
                self.errors.append("invalid argument for literal constant; must be a hex or char")
                return
            self.addressMode = "DIRECT"
            # if self.targetAddress == -1:
            #     self.errors.append("literal argument " + arg_1[1:] + " target address not set up")
            #     return
            vars.literalsToProcess = True
            if details["content"] in vars.littab.keys():
                vars.littab[details["content"]][1].append(self.location)
            else:
                print("\nadding", details["content"], "to the literal table")
                vars.littab[details["content"]] = [details, [self.location], vars.current_block]
                print("new littab")
                print(vars.littab)

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

def getExpressionValue_(self, input):
    debug = False
    ops_ = ['-', '+', '*', '/']
    operands = []
    one_operand = ''
    operators = []

    #we have a special case; and that is where the input is simply '*'
    if input == '*':
        return t.getCorrespondingNumber('*')

    for bit in input:
        if bit in ops_:
            if len(one_operand) == 0:
                return -1

            num = t.getCorrespondingNumber(one_operand) #returns [value, 'A' or 'R']
            if num == -1:
                self.errors.append("Cannot find", one_operand, "in the symtab")
                return -1
            operands.append(num)
            one_operand = ''

            if len(operators) != 0:
                while ops_.index(operators[-1]) >= ops_.index(bit):
                    op1 = operands.pop()    #because we used up 2 operands
                    op2 = operands.pop()
                    abs_or_rel = [op1[1], op2[1]]
                    op1 = op1[0]
                    op2 = op2[0]
                    single = operators.pop()
                    if single == '-':
                        if abs_or_rel != ['R', 'R']:
                            self.errors.append("Cannot find value of expression; check whether the args are absolute")
                            return
                        operands.append([op2 - op1, 'A'])
                    else:
                        if abs_or_rel != ['A', 'A']:
                            self.errors.append("Cannot find value of expression; check whether the args are absolute")
                            return
                    if single == '+':
                        operands.append([op2 + op1, 'A'])
                    elif single == '*':
                        operands.append([op2 * op1, 'A'])
                    else:
                        operands.append([op2 // op1, 'A'])
                    if len(operators) == 0:
                        break
            operators.append(bit)
        else:
            one_operand += bit
        if debug:
            print("\n\n")
            print("new bit: ", bit)
            print("operands: ", operands)
            print("operators: ", operators)

    if len(one_operand) == 0:
        return -1
    num = t.getCorrespondingNumber(one_operand)
    if num == -1:
        self.errors.append("Cannot find", one_operand, "in the symtab")
        return
    operands.append(num)

    if debug:
        print("finished main loop")
        print("\n\n")
        print("operands: ", operands)
        print("operators: ", operators)

    while (len(operands) != 1):
        op1 = operands.pop()    #because we used up 2 operands
        op2 = operands.pop()
        abs_or_rel = [op1[1], op2[1]]
        op1 = op1[0]
        op2 = op2[0]
        single = operators.pop()

        if debug:
            print("just before the first iteration")
            print("\n\n")
            print("operands: ", operands)
            print("operators: ", operators)

        if single == '-':
            if abs_or_rel != ['R', 'R']:
                self.errors.append("Cannot find value of expression; check whether the args are absolute")
                return
            operands.append([op2 - op1, 'A'])
        else:
            if abs_or_rel != ['A', 'A']:
                self.errors.append("Cannot find value of expression; check whether the args are absolute")
                return
            if single == '+':
                operands.append([op2 + op1, 'A'])
            elif single == '*':
                operands.append([op2 * op1, 'A'])
            else:
                operands.append([op2 // op1, 'A'])
        if debug:
            print("\n\n")
            print("operands: ", operands)
            print("operators: ", operators)

    return operands[0]

def directiveHandler_(self):

    details = t.info(self.args, "all")

    if self.instruction == 'START':
        if details["type"] == "int":
            g.start_address = int(details["content"], 16)
        else:
            self.errors.append("Invalid argument for the start instruction; must be a hex value")
            return
        if g.start_address > 2**20-1:
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
        vars.symtab[self.label] = (self.location, "WORD", -1, "R", vars.current_block)

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
        vars.symtab[self.label] = (self.location, "BYTE", -1, "R", vars.current_block)

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
        vars.symtab[self.label] = (self.location, "WORD_CONST", value, "R", vars.current_block)

    elif self.instruction == 'BYTE':
        #assert that the instruction args ar valid
        if details["type"] != "char" and details["type"] != "hex":
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
        vars.symtab[self.label] = (self.location, "BYTE_CONST",  value, "R", vars.current_block)

    elif self.instruction == 'USE':
        if len(vars.line_objects) != 0:
            # if we had a default control section
            if len(vars.program_block_details) == 0:
                vars.program_block_details[len(vars.program_block_details)] = (
                'default', g.start_address, g.locctr - g.start_address)
            # if we had a previous control section whose size needs to be set up
            else:
                recent = vars.program_block_details[len(vars.program_block_details)-1]
                recent[2] = g.locctr - recent[1]
                vars.program_block_details[len(vars.program_block_details)-1] = recent

        if (self.label == -1):
            self.errors.append("CSECT instruction is missing a label")
            return
        if self.label in [details[0] for details in vars.program_block_details.values()]:
            self.errors.append("label has already been used")
            return
        vars.current_block = len(vars.program_block_details)
        vars.program_block_details[len(vars.program_block_details)] = (self.label, g.locctr, 0)
        g.locctr = 0

    elif self.instruction == 'EXTDEF':
        pass

    elif self.instruction == 'EXTREF':
        pass

    elif self.instruction == 'CSECT':
        pass

    #the littab currently is in the format: {literal : [details, [self.location]]}
    #for each entry in the littab, we give it a location by icrementing locctr approproately
    #each entry also has the locations where the literal is used; we go and update the ta for the instructions
    #in each of those locations
    #
    elif self.instruction == 'LTORG':
        vars.literalsToProcess = False
        if len(vars.littab) == 0:
            self.warnings.append("LTORG was called, but no literals encountered yet")
            return
        #assign mem locations to the variables on the littab
        next_const_location = g.locctr
        for literal in vars.littab.keys():
            if len(vars.littab[literal]) == 2: #some of the literals wouls have been processed by an earlier ltorg
                continue
            locations = vars.littab[literal][1]
            details = vars.littab[literal][0]
            block_number = vars.littab[literal][2]
            # print("literal details: ", details)
            vars.littab[literal] = [next_const_location, block_number]
            if len(locations) != 0:
                self.binary = ''
            for loc in locations:
                for obj in vars.line_objects:
                    if obj.location == loc:
                        # if len(vars.program_block_details) != 0:
                        obj.targetAddress = next_const_location + vars.program_block_details[block_number][1]
                        # else:
                        #     #we need this special condition since the program_block_details is only complete at the end of pass 1
                        #     obj.targetAddress = next_const_location + g.start_address
                        break
            self.size += details["size"]
            next_const_location += details["size"]
            self.binary += details["content"]

    elif self.instruction == 'EQU':
        result = self.getExpressionValue(self.args)
        if result[0] ==  -1:
            return
        if result[0] < 0:
            self.errors.append("Cannot have a negative value. This expression results in a negative value")
            return
        exprValue = hex(result[0])[2:]
        if len(exprValue) % 2 != 0:
            exprValue = '0' + exprValue
        if len(exprValue) > 6:
            self.errors.append("expresssion value cannot exceed 0xFFF")
            return
        while len(exprValue) < 6:
            exprValue = '0' + exprValue
        self.size = 3
        if self.label == -1:
            self.errors.append("Missing label for EQU operation")
            return
        vars.symtab[self.label] = (self.location, "WORD", exprValue, result[1], vars.current_block)
