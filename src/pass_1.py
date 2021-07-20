import global_vars as g
import tools as t

def pass_1_(self, ln):

    ln.location = self.locctr

    #split the line into <content> <comments>
    loc = ln.raw.find('.')
    if loc != -1:
        ln.comment = ln.raw[loc:]
        ln.content = ln.raw[:loc]
    else:
        ln.content = ln.raw[:-1]
        if ln.raw[-1] != '\n':
            ln.content = ln.raw

    if len(ln.content) == 0:      #the line is entirely a comment
        ln.isUselessLine = True
        ln.size = 0
        return

    #split the <content> into <label> <instruction> <args>
    slices = [x for x in ln.content.split('\t') if x != '']
    if len(slices) == 2:
        if ln.raw[0] == '\t':
            ln.instruction = slices[0]
            ln.args = slices[1]
        else:
            ln.label = slices[0]
            ln.instruction = slices[1]
    elif len(slices) == 3:
        ln.label = slices[0]
        ln.instruction = slices[1]
        ln.args = slices[2]
    else:
        ln.instruction = slices[0]

    ln.originalArgs = ln.args

    # if instruction is a directive
    if ln.instruction in g.directives:
        ln.isDirective = True
        ln.instructionType = "DIRECTIVE"
        ln.size = 0
        self.ln_directiveHandler(ln)

    #check if its a command from optable
    else:
        try:
            #extended format command
            if ln.instruction[0] == '+':
                ln.instructionDetails = g.optable[ln.instruction[1:]]
                if ln.instructionDetails[0] != 'm':
                    ln.errors.append("This instruction cannot be used in extended mode")
                    return
            else:
                ln.instructionDetails = g.optable[ln.instruction]
        except KeyError:
            ln.errors.append("Instruction:" + ln.instruction + "is invalid")
            return
        ln.instructionType = "INSTRUCTION"
        #setting the size of the instruction based on the instruction details
        try:
            ln.size = int(ln.instructionDetails[1])
        # for some instructions, the size is given as '3/4' since it could be extended
        except ValueError:
            if ln.instruction[0] == '+':
                ln.size = 4
                ln.instructionType = "EXTENDED INSTRUCTION"
            else:
                ln.size = 3

        if ln.label != -1:
            # self.symtab.append([ln.label, ln.location, "WORD_CONST", word_value, absolute/relative])
            self.symtab[ln.label] = (ln.location, "INSTRUCTION", -1, "R", self.current_block)
        self.ln_arg_check(ln)

#checks the number and type of arguments
#also gets the target address, if needed
def arg_check_(self, ln):
    #to check that the number of arguments match
    ln.args = ln.args.split(",")
    arg_type = ln.instructionDetails[0]
    # for a type match
    arg_1 = ''
    arg_2 = ''

    #number of args check
    if ln.args == [''] and arg_type == '0':
        pass
    else:
        if ',' in arg_type:
            if len(ln.args) == 2:
                arg_1 = ln.args[0]
                arg_2 = ln.args[1]
            else:
                ln.errors.append("Instruction does not have the correct number of arguments. "+
                "Expected 2; got:",len(ln.args))
                return
        else:
            arg_1 = ln.args[0]
            if len(ln.args) == 2:
                if ln.args[1] == 'X':
                    arg_2 = ln.args[1]
                    ln.isIndexed = True
                else:
                    ln.errors.append("Instruction does not have the correct number of arguments. "+
                    "Expected 1; got:"+str(len(ln.args)))
                    return

    # print("instruction:", ln.instruction)
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
                    ln.errors.append("const argument", arg_1, " must be >= 0")
                    return
                ln.targetAddress = num
                ln.addressMode = "IMMEDIATE CONST"
            except ValueError:

                ln.addressMode = "IMMEDIATE"

        # indirect addressing
        elif arg_1[0] == '@':
            ln.addressMode = "INDIRECT"

        # literal pool
        elif arg_1[0] == '=':
            details = t.info(arg_1[1:], "all")
            # print("details:", details)
            if details["type"] != "char" and details["type"] != "hex":
                ln.errors.append("invalid argument for literal constant; must be a hex or char")
                return
            ln.addressMode = "DIRECT"
            # if ln.targetAddress == -1:
            #     ln.errors.append("literal argument " + arg_1[1:] + " target address not set up")
            #     return
            self.literalsToProcess = True
            if details["content"] in self.littab.keys():
                self.littab[details["content"]][1].append(ln.location)
            else:
                print("\nadding", details["content"], "to the literal table")
                self.littab[details["content"]] = [details, [ln.location], self.current_block]
                print("new littab")
                print(self.littab)

        #direct addressing mode
        else:
            ln.addressMode = "DIRECT"


    #this is just the SVC instruction

    elif arg_type == 'n':
        try:
            ln.targetAddress = int(arg_1)
        except ValueError:
            #so it is not a number; check if it is a valid
            ln.errors.append("Argument:", arg_1, " must be an integer for the given instruction")
            return

    elif arg_type == 'r1,n':
        #check that the register is a valid one
        if arg_1 not in g.registers.keys():
            ln.errors.append("Argument:", arg_1, " must be a register name")
            return
        try:
            num = int(arg_2)
            if 0x1 < num < 0x10 == False:
                ln.errors.append("Argument:", arg_2, " must be a in [1,16]")
                return
        except ValueError:
            ln.errors.append("Argument:", arg_2, " must be an integer in [1,16]")
            return

    elif arg_type == 'r1,r2':
        if arg_1 not in g.registers.keys():
            ln.errors.append("Argument:", arg_1, " must be a register name")
            return
        if arg_2 not in g.registers.keys():
            ln.errors.append("Argument:", arg_2, " must be a register name")
            return

    elif arg_type == "r1":
        if arg_1 not in g.registers.keys():
            ln.errors.append("Argument:", arg_1, " must be a register name")
            return

    elif arg_type == '0':
        pass

    if ln.isIndexed:
        if arg_type != 'm':
            ln.errors.append("Instruction", ln.instruction, " does not support indexed addressing")
            return
        if ln.addressMode != "DIRECT":
            ln.errors.append("Instruction", ln.instruction, "'s addressing mode cannot use indexed addressing")
            return
        pass

def getExpressionValue_(self, ln):
    debug = False
    # ops_ = ['-', '+', '*', '/']
    ops_ = ['-', '+']
    operands = []
    one_operand = ''
    operators = []

    input = ln.args

    #we have a special case; and that is where the input is simply '*'
    if input == '*':
        return self.ln_getCorrespondingNumber('*')

    for bit in input:
        if bit in ops_:
            if len(one_operand) == 0:
                return -1
            num = self.ln_getCorrespondingNumber(one_operand) #returns [value, 'A' or 'R']
            if num == -1:
                ln.errors.append("Cannot find" + one_operand + "in the symtab")
                return -1
            if one_operand in self.referRecords:
                ln.usesExtRef = True
            operands.append(num)
            one_operand = ''

            try:
                while ops_.index(operators[-1]) >= ops_.index(bit):
                    op1 = operands.pop()    #because we used up 2 operands
                    op2 = operands.pop()
                    abs_or_rel = [op1[1], op2[1]]
                    op1 = op1[0]
                    op2 = op2[0]
                    single = operators.pop()
                    if single == '-':
                        if abs_or_rel != ['R', 'R']:
                            ln.errors.append("Cannot find value of expression; check whether the args are absolute")
                            return -1
                        operands.append([op2 - op1, 'A'])
                    else:
                        if abs_or_rel != ['A', 'A']:
                            ln.errors.append("Cannot find value of expression; check whether the args are absolute")
                            return -1
                    if single == '+':
                        operands.append([op2 + op1, 'A'])
                    # elif single == '*':
                    #     operands.append([op2 * op1, 'A'])
                    # else:
                    #     operands.append([op2 // op1, 'A'])
                    if len(operators) == 0:
                        break
            except IndexError:
                if len(operators) != 0 or len(operands) != 1:
                    ln.errors.append("Expression is invalid")
                    return -1
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
    num = self.ln_getCorrespondingNumber(one_operand)
    if num == -1:
        ln.errors.append("Cannot find", one_operand, "in the symtab")
        return -1
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
                ln.errors.append("Cannot find value of expression; check whether the args are absolute")
                return -1
            operands.append([op2 - op1, 'A'])
        else:
            if abs_or_rel != ['A', 'A']:
                ln.errors.append("Cannot find value of expression; check whether the args are absolute")
                return -1
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

def directiveHandler_(self, ln):

    details = t.info(ln.args, "all")

    if ln.instruction == 'START':
        details = t.info(ln.args, "all")
        if len(self.line_objects) == 1:
            self.locctr = g.start_address
            line_obj.location = g.start_address
        if details["type"] == "int":
            g.start_address = int(details["content"], 16)
        else:
            ln.errors.append("Invalid argument for the start instruction; must be a hex value")
            return
        if g.start_address > 2**20-1:
            ln.errors.append("SICXE compouters only have 1 mb of memory; given start location exceeds 1 mb limit")
            return


    elif ln.instruction == 'END':
        pass

    elif ln.instruction == 'RESW':
        details = t.info(ln.args, "all")
        if details["type"] != "int":
            ln.errors.append("Invalid argument for instruction")
            return
        try:
            ln.size = int(details["content"]) * 3
        except ValueError:
            ln.errors.append(" invalid argument for RESW; must be an integer (not a hex)")
            return
        if (ln.label == -1):
            ln.warnings.append("RESW instruction has no label for it")
            return
        self.symtab[ln.label] = (ln.location, "WORD", -1, "R", self.current_block)

    elif ln.instruction == 'RESB':
        details = t.info(ln.args, "all")
        if details["type"] != "int":
            ln.errors.append("Invalid argument for instruction")
            return
        try:
            ln.size = int(details["content"])
        except ValueError:
            ln.errors.append(" invalid argument for RESB; must be an integer (not a hex)")
            return
        # ln.instructionType = "BYTE"
        if (ln.label == -1):
            ln.warnings.append("RESB instruction has no label for it")
            return
        self.symtab[ln.label] = (ln.location, "BYTE", -1, "R", self.current_block)

    elif ln.instruction == 'WORD':
        #assert that the instruction args ar valid
        result = self.ln_getExpressionValue(ln)
        value = result[0]
        print("\n\n result: ", result)
        if value == -1:
            ln.errors.append("value for WORD must be an int")
            return
        if result[1] != 'A':
            ln.errors.append("the expression value is relative; absolute needed here")
            return
        #asserting that the word value is within bounds
        if (value < 0 or value > 2**24-1):      #a word is 3 bytes long; hence the upper bound
            ln.errors.append("value for word is out of bounds")
            return
        ln.size = 3
        #if the label is absent, we cant add it to the symtab
        if (ln.label == -1):
            ln.warnings.append("WORD instruction has no label for it")
            return
        value = hex(value)[2:]
        while len(value) < 6:
            value = '0'+ value
        ln.binary = value
        self.symtab[ln.label] = (ln.location, "WORD_CONST", value, "R", self.current_block)

    elif ln.instruction == 'BYTE':
        details = t.info(ln.args, "all")
        #assert that the instruction args ar valid
        if details["type"] != "char" and details["type"] != "hex":
            ln.errors.append("value for BYTE must be a char/hex const")
            return
        ln.size = details["size"]
        if (ln.label == -1):
            ln.warnings.append("BYTE instruction has no label for it")
            return
        value = details["content"]
        if (details['type'] == 'hex'):
            while len(value) < 2*ln.size:
                value = '0'+ value
        else:
            while len(value) < ln.size:
                value = '0' + value
        ln.binary = value
        self.symtab[ln.label] = (ln.location, "BYTE_CONST",  value, "R", self.current_block)

    elif ln.instruction == 'USE':
        if len(self.line_objects) != 0:
            # if we had a default control section
            if len(self.program_block_details) == 0:
                self.program_block_details[len(self.program_block_details)] = (
                'default', g.start_address, self.locctr - g.start_address)
            # if we had a previous control section whose size needs to be set up
            else:
                recent = self.program_block_details[len(self.program_block_details)-1]
                recent[2] = self.locctr - recent[1]
                self.program_block_details[len(self.program_block_details)-1] = recent

        if (ln.label == -1):
            ln.errors.append("CSECT instruction is missing a label")
            return
        if ln.label in [details[0] for details in self.program_block_details.values()]:
            ln.errors.append("label has already been used")
            return
        self.current_block = len(self.program_block_details)
        self.program_block_details[len(self.program_block_details)] = (ln.label, self.locctr, 0)
        self.locctr = 0

    elif ln.instruction == 'EXTDEF':
        if self.name in g.extVars.keys():
            self.warnings.append('multiple use of EXTDEF instruction')
        else:
            g.extVars[self.name] = []
        g.extVars[self.name] = g.extVars[self.name] + ln.args.split(',')
        for var in ln.args.split(','):
            self.defineRecords.append(var)

    elif ln.instruction == 'EXTREF':
        ln.args = ln.args.split(',')
        if len(self.referRecords) != 0:
            self.warnings.append('multiple use of EXTREF instruction')
        for arg in ln.args:
            self.symtab[arg] = (0, "WORD", -1, "R", self.current_block)
            self.referRecords.append(arg)

    elif ln.instruction == 'CSECT':
        pass

    #the littab currently is in the format: {literal : [details, [ln.location]]}
    #for each entry in the littab, we give it a location by icrementing locctr approproately
    #each entry also has the locations where the literal is used; we go and update the ta for the instructions
    #in each of those locations
    #
    elif ln.instruction == 'LTORG':
        self.literalsToProcess = False
        if len(self.littab) == 0:
            ln.warnings.append("LTORG was called, but no literals encountered yet")
            return
        #assign mem locations to the variables on the littab
        next_const_location = self.locctr
        for literal in self.littab.keys():
            if len(self.littab[literal]) == 2: #some of the literals wouls have been processed by an earlier ltorg
                continue
            locations = self.littab[literal][1]
            details = self.littab[literal][0]
            block_number = self.littab[literal][2]
            # print("literal details: ", details)
            self.littab[literal] = [next_const_location, block_number]
            if len(locations) != 0:
                ln.binary = ''
            for loc in locations:
                for obj in self.line_objects:
                    if obj.location == loc:
                        # if len(self.program_block_details) != 0:
                        obj.targetAddress = next_const_location + self.program_block_details[block_number][1]
                        # else:
                        #     #we need this special condition since the program_block_details is only complete at the end of pass 1
                        #     obj.targetAddress = next_const_location + g.start_address
                        break
            ln.size += details["size"]
            next_const_location += details["size"]
            ln.binary += details["content"]

    elif ln.instruction == 'EQU':
        result = self.ln_getExpressionValue(ln)
        print("\n the result of the equ expression is:", result)
        if result[0] ==  -1:
            return
        if result[0] < 0:
            ln.errors.append("Cannot have a negative value. This expression results in a negative value")
            return
        exprValue = hex(result[0])[2:]
        if len(exprValue) % 2 != 0:
            exprValue = '0' + exprValue
        if len(exprValue) > 6:
            ln.errors.append("expresssion value cannot exceed 0xFFF")
            return
        while len(exprValue) < 6:
            exprValue = '0' + exprValue
        # ln.size = 3           # i'm not sure about this; does the EQU not require to be wrotten into memory?
        if ln.label == -1:
            ln.errors.append("Missing label for EQU operation")
            return
        self.symtab[ln.label] = (ln.location, "WORD", exprValue, result[1], self.current_block)


#           BELOW are the helper methods for pass 1                #

def getCorrespondingNumber_(self, input):
    try:
        result = int(input)
        return [result, "A"]
    except ValueError:
        if input == '*':
            return [self.locctr, 'R']
        if input not in self.symtab.keys():
            return -1
        return [self.symtab[input][0], self.symtab[input][-2]]
