# arg_types = ['', 'r1,r2', 'r1,n', 'n', 'm', 'r1']
'''
r1, n :: SHIFTL and SHIFTR                :: no indexed
<opcode><r1><n-1> - 2bytes - <2hex><1hex><1hex> => 0x0<n-1<0xF => 1<n<16

r1,r2 :: ADDR/SUBR/MULR/DIVR/ COMPR/ RMO  :: all registers; no cool method of addressing
<OPCODE><r1><r2>  - 2bytes - <2hex><1hex><1hex>

m     :: LOAD, STO, ADD/MUL/SUB/DIV, JUMPS:: ALL TYPES OF ADDRESSING
got this!! - 3 or 4

n     :: SVC instruction just this one    :: its actually r1 type ; r1 is n
is it <opcode><n><whatever 1/2 byte> - 2 bytes - <2hex opcode><1hex register><0x0> - 0x0<n<0xF

r1    :: CLEAR and TIXR                   :: register, same comments as r1,r2
TIXR T --> B850   (register 5 is T)
<OPCODE><r1><whatever 1/2 byte> - 2 bytes - <2hex opcode><1hex register><0x0>

no argument: FIX, FLOAT, HIO, NORM, RSUB, SIO, TIO  (ALL EXCEPT RSUB(3/4 size) are of size 1)
'''

def pass_2_(self, pc):
    #argument check: that the number and type of argument matches
    arg_check()
    build_instruction_definition(pc)
    #get TA; add error if any
    #modify TA based on adddressing mode
    #write opcode?

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
            if len(self.args) == 1:
                arg_1 = self.args[0]
            else:
                self.errors.append("Instruction does not have the correct number of arguments. "+
                "Expected 1; got:",len(self.args))
                return

    #check the type match
    if arg_type == 'm':
        #get addressing mode; change TA accordingly
        #if immediate, need to get the value of the operand
        if arg_1[0] == '#':
            try:
                num = int(arg_1[1:])
            except ValueError:
                #so it is not a number; check if it is a valid
                try:
                    arg_details = g.symtab[arg_1[1:]]
                    self.targetAddress = arg_details[0]
                    self.addressMode = "IMMEDIATE"
                except KeyError:
                    self.errors.append("Argument:", arg_1, " is not defined")
                    return
        # indirect addressing
        elif arg_1[0] == '@':
            try:
                arg_details = g.symtab[arg_1[1:]]
                if arg_details[1] is not "WORD_CONST":      #is this necessary tho?
                self.errors.append("Argument:", arg_1[1:], " is of type", arg_details[1]
                , " that cannot be used for immediate addressing")
                return
                self.targetAddress = arg_details[0]
                self.addressMode = "INDIRECT"
            except KeyError:
                self.errors.append("Argument:", arg_1, " is not defined")
                return
        #direct addressing mode
        else:
            try:
                arg_details = g.symtab[arg_1]
                self.targetAddress == arg_details[0]
                self.addressMode = "DIRECT"
            except KeyError:
                self.errors.append("Argument:", arg_1, " is not defined")
                return
            pass

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
            self.errors.append("Argument:", arg_1, " must be a regsiter name")
            return
        try:
            num = int(arg_2)
            if 0x1 < num < 0x10 is False:
                self.errors.append("Argument:", arg_2, " must be a in [1,16]")
                return
        except ValueError:
            self.errors.append("Argument:", arg_2, " must be an integer in [1,16]")
            return

    elif arg_type == 'r1,r2':
        if arg_1 not in g.registers.keys():
            self.errors.append("Argument:", arg_1, " must be a regsiter name")
            return
        if arg_2 not in g.registers.keys():
            self.errors.append("Argument:", arg_2, " must be a regsiter name")
            return

    elif arg_type == "r1":
        if arg_1 not in g.registers.keys():
            self.errors.append("Argument:", arg_1, " must be a regsiter name")
            return

    elif arg_type == '0':
        pass

def build_instruction_(self, pc):
    arg_type = self.instructionDetails[0]
    opcode = self.instructionDetails[2]
    if arg_type == 'm':
        if self.addressMode = "DIRECT":
            pass
        elif self.addressMode = "IMMEDIATE":    #'#'
            pass
        else:   #INDIRECT; '@'
            pass

    elif arg_type == 'n':
        self.binary = opcode + hex(self.args[0])[2:] + '0'

    elif arg_type == 'r1,n':
        self.binary = opcode + g.registers[self.args[0]][0]
        + str(int(self.args[1])-1)

    elif arg_type == 'r1,r2':
        self.binary = opcode + g.registers[self.args[0]][0]
        + g.registers[self.args[1]][0]

    elif arg_type == "r1":
        self.binary = opcode + g.registers[self.args[0]][0] + '0'

    elif arg_type == '0':
        self.bianry = opcode
