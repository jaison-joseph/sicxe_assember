import global_vars as g
import tools as t

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


def pass_2_(self):
    if self.instructionType == "DIRECTIVE":
        self.directiveHandler()
    #argument check: that the number and type of argument matches
    else:
        self.arg_check()
        self.processInstruction()
        self.build_instruction()
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
            elif len(self.args) == 2 and self.args[1] == 'X':
                arg_1 = self.args[0]
                arg_2 = self.args[1]
                self.isIndexed = True
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
                # if arg_details[1] is not "WORD_CONST":      #is this necessary tho?
                #     self.errors.append("Argument:", arg_1[1:], " is of type", arg_details[1]
                #     , " that cannot be used for immediate addressing")
                #     return
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

            # not sure if control flow will reach here, but just in case
            if self.addressMode == -1:
                self.arguments.append("COuld not deduce the addressing mode for this instruction")
                return
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
            if 0x1 < num < 0x10 == False:
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

def build_instruction_(self):
    arg_type = self.instructionDetails[0]
    opcode = self.instructionDetails[2]
    if arg_type == 'm':
        self.binary = t.put_together(opcode, self.addressMode, self.getRelative(), self.display, self.instructionType)
    elif arg_type == 'r1,r2':
        self.binary = opcode + g.registers[self.args[0]][0] + g.registers[self.args[1]][0]
    elif arg_type == 'r1,n':
        self.binary = opcode + g.registers[self.args[0]][0] + hex(int(self.args[1])-1)[2:]
    elif arg_type == 'r1':
        self.binary = opcode + g.registers[self.args[0]][0] + g.registers[self.args[1]][0]
    elif arg_type == 'n':
        self.binary = opcode + hex(self.args[0])[2:] + '0'
    elif arg_type == '0':
        self.binary = opcode



def directiveHandler_(self):
    if self.instruction == 'START':
        pass
    elif self.instruction == 'END':
        pass
    elif self.instruction == 'RESW':
        pass
    elif self.instruction == 'RESB':
        pass
    elif self.instruction == 'WORD':
        pass
    elif self.instruction == 'BYTE':
        pass
    elif self.instruction == 'EXTDEF':
        pass
    elif self.instruction == 'EXTREF':
        pass
    elif self.instruction == 'LTORG':
        pass
    elif self.instruction == 'EQU':
        pass
    elif self.instruction == 'CSECT':
        pass


# returns the addressing mode suitable for a given command
# it is a member function of the class
# returns:
# 1. "e": extended
# 2. "pc": program-counter relative
# 3. "base": base relative
# 4. "": the target address is out of bounds
def getRelative_(self):
    ta = self.targetAddress
    pc = self.programCounter
    disp = ta - pc
    if self.instructionType == "EXTENDED INSTRUCTION":
        self.display == ta
        return "extended"  #e for extended
    # prefer PC relative over base relative
    if -0xFFF//2 <= disp <= 0xFFF//2:
        self.display = t.twocomp(disp)
        return "pc"
    else:
        if g.register_b == -1:
            self.errors.append("Cannot perform base relative addressing since base register has not been set")
            return ""
        disp = ta - g.register_b
        if 0 <= disp <= 0xFFF:
            self.display = twocomp(disp)
            return "base"

# for the LDB/LDX instructions, we need to get the actaul values into the registers
# in case we need to do base or index based addressing
def processInstruction_(self):
        if self.instruction == 'CLEAR':
            if self.args[0] == 'B':
                g.register_b == 0x000000
            elif self.args[0] == 'X':
                g.register_x == 0x000000

        elif self.instruction == 'LDB':
            if self.addressMode == "DIRECT":
                foo = g.symtab[self.args[0]]
                if foo[2] == -1:
                    self.errors.append("variable has not been initialised")
                    return
                else:
                    g.register_b == int(foo[2], 16)
                    # remember that one can only use indexed addressing along with direct addressing
                    if self.isIndexed:
                        if g.register_x == -1:
                            self.errors.append("could not use indexed based addressing; register x has not been initialised")
                            return
                        g.register_b += g.register_x
                    g.register_b == hex(str(foo[2]))[2:]
                    while len(g.register_b) < 6:
                        g.register_b = '0' + g.register_b

            elif self.addressMode == "IMMEDIATE":
                g.register_b = hex(t.get_immediate(g.args[0][1:]))[2:]
                while len(g.register_b) < 6:
                    g.register_b = '0' + g.regsiter_b
            elif self.addressMode == "INDIRECT":
                # self.warnings.append("are you sure you want to use indirect addressing for an LDB instruction?")
                # value = t.get_indirect_value(g.args[0][1:])
                # if value == -1:
                #     self.errors.append("could not deduce value stored by:", )
                self.errors.append("cannot use indirect addressing on an LDB instruction")
                return

        elif self.instruction == 'LDX':
            if self.addressMode == "DIRECT":
                foo = g.symtab[self.args[0]]
                if foo[2] == -1:
                    self.errors.append("variable has not been initialised")
                    return
                else:
                    g.register_x == int(foo[2], 16)
                    # remember that one can only use indexed addressing along with direct addressing
                    if self.isIndexed:
                        self.errors.append("Cannot use indexxed based addressing on an LDX instruction")
                        return
                    g.register_x == hex(str(foo[2]))[2:]
                    while len(g.register_x) < 6:
                        g.register_x = '0' + g.register_x

            elif self.addressMode == "IMMEDIATE":
                g.register_x = hex(t.get_immediate(g.args[0][1:]))[2:]
                while len(g.register_x) < 6:
                    g.register_x = '0' + g.regsiter_b
            elif self.addressMode == "INDIRECT":
                self.errors.append("cannot use indirect addressing on an LDX instruction")
                return
