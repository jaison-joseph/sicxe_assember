import global_vars as g
import tools as t
import pprint
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

def getTargetAddress_(self):

    #i saw this in the text; no args but the target address was 0
    if self.instruction == 'RSUB':
        self.targetAddress = 0
        return

    if self.instructionDetails[0] != 'm':
        return
    # the target address of IMMEDIATE CONST and LITERALS are aken care of in pass 1 itself
    if self.targetAddress != -1:
        return

    arg_1 = self.args[0]

    try:
        arg_details = []
        if self.addressMode == "IMMEDIATE":
            arg_details = g.symtab[arg_1[1:]]
            self.targetAddress = arg_details[0]
        elif self.addressMode == "INDIRECT":
            arg_details = g.symtab[arg_1[1:]]
            self.targetAddress = arg_details[0]
        elif self.addressMode == "DIRECT":
            arg_details = g.symtab[arg_1]
            if self.instruction == 'TD':
                print("arg_details:", arg_details)
            self.targetAddress = arg_details[0]
        elif self.addressMode == "EXTENDED":
            arg_details = g.symtab[arg_1[1:]]
            self.targetAddress = arg_details[0]
        self.targetAddress += g.program_block_details[arg_details[4]][1]    #adding the start location of the program block
    except KeyError:
        print("error instruction details \n")
        pprint.pprint(self.__dict__)
        self.errors.append('target address cannot be found. check argument and addressing mode')
        return

    if self.isIndexed:
        if g.register_x == -1:
            self.errors.append("could not use indexed based addressing; register x has not been initialised")
            return
        self.targetAddress -= int(g.register_x, 16)

# returns the addressing mode suitable for a given command
# it is a member function of the class
# returns:
# 1. "extended": extended
# 1. "sic": sic style addressing
# 1. "nothing": use immediate addressing flags; the argument of instruction is a literal
# 2. "pc": program-counter relative
# 3. "base": base relative
# 4. "": the target address is out of bounds
def getRelative_(self):
    ta = self.targetAddress
    pc = self.programCounter
    disp = ta - pc
    # print(self.instruction, " :: TA :: ", disp)
    # the case of loading a const or extended fomat
    if self.addressMode == "IMMEDIATE CONST" and int(self.targetAddress) <= 0xFFF:
        self.display = hex(ta)[2:]
        return "nothing" #the behavior is the same, no pc or base relative addressing is needed
    if self.instructionType == "EXTENDED INSTRUCTION":
        self.display = hex(ta)[2:]
        return "extended"  #e for extended
    # prefer PC relative over base relative
    if -0xFFF//2 <= disp <= 0xFFF//2:
        self.display = t.twocomp(disp)
        return "pc"
    if g.register_b == -1:
        # if we can avoid addresssing altogether:
        if 0 <= disp <= 2**15-1:
            return "sic"
        self.errors.append("Cannot perform base relative addressing since base register has not been set")
        return ""
    try:
        disp = ta - int(g.register_b, 16)
    except:
        print(type(ta), "::", ta)
        print(type(g.register_b), "::", g.register_b)
        exit(0)
    if 0 <= disp <= 0xFFF:
        self.display = t.twocomp(disp)
        return "base"

# for the LDB/LDX instructions, we need to get the actaul values into the registers
# in case we need to do base or index based addressing
def processInstruction_(self):
    if self.instruction == 'CLEAR':
        print("start of clear")
        if self.args[0] == 'B':
            g.register_b = '0'*6
        elif self.args[0] == 'X':
            print("hit the CLEAR X instruction")
            g.register_x = '0'*6

    elif self.instruction == 'LDB':
        if self.addressMode == "DIRECT":
            foo = g.symtab[self.args[0]]
            if foo[2] == -1:
                self.errors.append("variable", self.args[0], "has not been initialised")
                return
            g.register_b == foo[2]
            while len(g.register_b) < 6:
                g.register_b = '0' + g.register_b
            # remember that one can only use indexed addressing along with direct addressing
            if self.isIndexed:
                if g.register_x == -1:
                    print("the instruction with error: ", self.__dict__)
                    self.errors.append("could not use indexed based addressing; register x has not been initialised")
                    return
                g.register_b += g.register_x
            g.register_b == hex(str(foo[2]))[2:]
            while len(g.register_b) < 6:
                g.register_b = '0' + g.register_b

        elif self.addressMode == "IMMEDIATE":
            g.register_b = hex(t.get_immediate(self.args[0][1:]))[2:]
            while len(g.register_b) < 6:
                g.register_b = '0' + g.register_b
        elif self.addressMode == "INDIRECT":
            # self.warnings.append("are you sure you want to use indirect addressing for an LDB instruction?")
            # value = t.get_indirect_value(g.args[0][1:])
            # if value == -1:
            #     self.errors.append("could not deduce value stored by:", )
            self.errors.append("cannot use indirect addressing here")
            return

    elif self.instruction == 'LDX':
        if self.addressMode == "DIRECT":
            foo = g.symtab[self.args[0]]
            if foo[2] == -1:
                self.errors.append("variable has not been initialised")
                return
            else:
                g.register_x == [2]
                while len(g.register_x) < 6:
                    g.register_x = '0' + g.register_x
                # remember that one can only use indexed addressing along with direct addressing
                if self.isIndexed:
                    self.errors.append("Cannot use indexxed based addressing here")
                    return
                g.register_x == hex(str(foo[2]))[2:]
                while len(g.register_x) < 6:
                    g.register_x = '0' + g.register_x

        elif self.addressMode == "IMMEDIATE":
            g.register_x = hex(t.get_immediate(self.args[0][1:]))[2:]
            while len(g.register_x) < 6:
                g.register_x = '0' + g.register_x

        elif self.addressMode == "IMMEDIATE CONST":
            g.register_x = hex(self.targetAddress)[2:]
            while len(g.register_x) < 6:
                g.register_x = '0' + g.register_x

        elif self.addressMode == "INDIRECT":
            self.errors.append("cannot use indirect addressing on an LDX instruction")
            return

def build_instruction_(self):
    arg_type = self.instructionDetails[0]
    opcode = self.instructionDetails[2]
    if arg_type == 'm':
        self.binary = t.put_together(opcode, self.addressMode, self.getRelative(),
                                     self.display, self.instructionType, self.isIndexed)
    elif arg_type == 'r1,r2':
        self.binary = opcode + g.registers[self.args[0]][0] + g.registers[self.args[1]][0]
    elif arg_type == 'r1,n':
        self.binary = opcode + g.registers[self.args[0]][0] + hex(int(self.args[1])-1)[2:]
    elif arg_type == 'r1':
        self.binary = opcode + g.registers[self.args[0]][0] + '0'
    elif arg_type == 'n':
        self.binary = opcode + hex(self.args[0])[2:] + '0'
    elif arg_type == '0':
        self.binary = opcode
