import global_vars as g
import tools as t
import pprint

def pass_2_(self, ln):
    if ln.isUselessLine:
        pass
    elif ln.instructionType == "DIRECTIVE":
        pass
    #argument check: that the number and type of argument matches
    else:
        self.ln_getTargetAddress(ln)
        if len(ln.errors) != 0:
            return False
        self.ln_processInstruction(ln)
        if len(ln.errors) != 0:
            return False
        self.ln_build_instruction(ln)
        if len(ln.errors) != 0:
            return False
    return True

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

def getTargetAddress_(self, ln):

    #i saw this in the text; no args but the target address was 0
    # i just hardcoded the target address for this instruction
    if ln.instruction == 'RSUB':
        return

    if ln.instructionDetails[0] != 'm':
        return
    # the target address of IMMEDIATE CONST and LITERALS are aken care of in pass 1 itself
    if ln.targetAddress != -1:
        return

    arg_1 = ln.args[0]

    try:
        arg_details = []
        if ln.addressMode == "IMMEDIATE":
            arg_details = self.symtab[arg_1[1:]]
            ln.targetAddress = arg_details[0]
        elif ln.addressMode == "INDIRECT":
            arg_details = self.symtab[arg_1[1:]]
            ln.targetAddress = arg_details[0]
        elif ln.addressMode == "DIRECT":
            arg_details = self.symtab[arg_1]
            if ln.instruction == 'TD':
                print("arg_details:", arg_details)
            ln.targetAddress = arg_details[0]
        elif ln.addressMode == "EXTENDED":
            arg_details = self.symtab[arg_1[1:]]
            ln.targetAddress = arg_details[0]
        ln.targetAddress += self.program_block_details[arg_details[4]][1]    #adding the start location of the program block
    # except IndexError:
    #     print(len(self.program_block_details), "::", len(arg_details)
    except KeyError:
        print("error instruction details \n")
        pprint.pprint(ln.__dict__)
        ln.errors.append('target address cannot be found. check argument and addressing mode')
        return

    if ln.isIndexed:
        if g.register_x == -1:
            ln.errors.append("could not use indexed based addressing; register x has not been initialised")
            return
        ln.targetAddress -= int(g.register_x, 16)

# returns the addressing mode suitable for a given command
# it is a member function of the class
# returns:
# 1. "extended": extended
# 1. "sic": sic style addressing
# 1. "nothing": use immediate addressing flags; the argument of instruction is a literal
# 2. "pc": program-counter relative
# 3. "base": base relative
# 4. "": the target address is out of bounds
def getRelative_(self, ln):
    ta = ln.targetAddress
    pc = ln.programCounter
    disp = ta - pc
    # print(ln.instruction, " :: TA :: ", disp)
    # the case of loading a const or extended fomat
    if ln.addressMode == "IMMEDIATE CONST" and int(ln.targetAddress) <= 0xFFF:
        ln.display = hex(ta)[2:]
        return "nothing" #the behavior is the same, no pc or base relative addressing is needed
    if ln.instructionType == "EXTENDED INSTRUCTION":
        ln.display = hex(ta)[2:]
        return "extended"  #e for extended
    # prefer PC relative over base relative
    if -0xFFF//2 <= disp <= 0xFFF//2:
        ln.display = t.twocomp(disp)
        return "pc"
    if g.register_b == -1:
        # if we can avoid addresssing altogether:
        if 0 <= disp <= 2**15-1:
            return "sic"
        ln.errors.append("Cannot perform base relative addressing since base register has not been set")
        return ""
    try:
        disp = ta - int(g.register_b, 16)
    except:
        print(type(ta), "::", ta)
        print(type(g.register_b), "::", g.register_b)
        exit(0)
    if 0 <= disp <= 0xFFF:
        ln.display = t.twocomp(disp)
        return "base"

# for the LDB/LDX instructions, we need to get the actaul values into the registers
# in case we need to do base or index based addressing
def processInstruction_(self, ln):
    if ln.instruction == 'CLEAR':
        print("start of clear")
        if ln.args[0] == 'B':
            g.register_b = '0'*6
        elif ln.args[0] == 'X':
            print("hit the CLEAR X instruction")
            g.register_x = '0'*6

    elif ln.instruction == 'LDB':
        if ln.addressMode == "DIRECT":
            foo = self.symtab[ln.args[0]]
            if foo[2] == -1:
                ln.errors.append("variable", ln.args[0], "has not been initialised")
                return
            g.register_b == foo[2]
            while len(g.register_b) < 6:
                g.register_b = '0' + g.register_b
            # remember that one can only use indexed addressing along with direct addressing
            if ln.isIndexed:
                if g.register_x == -1:
                    print("the instruction with error: ", ln.__dict__)
                    ln.errors.append("could not use indexed based addressing; register x has not been initialised")
                    return
                g.register_b += g.register_x
            g.register_b == hex(str(foo[2]))[2:]
            while len(g.register_b) < 6:
                g.register_b = '0' + g.register_b

        elif ln.addressMode == "IMMEDIATE":
            g.register_b = hex(self.ln_get_immediate(ln.args[0][1:]))[2:]
            while len(g.register_b) < 6:
                g.register_b = '0' + g.register_b
        elif ln.addressMode == "INDIRECT":
            # ln.warnings.append("are you sure you want to use indirect addressing for an LDB instruction?")
            # value = t.get_indirect_value(g.args[0][1:])
            # if value == -1:
            #     ln.errors.append("could not deduce value stored by:", )
            ln.errors.append("cannot use indirect addressing for this instruction")
            return

    elif ln.instruction == 'LDX':
        if ln.addressMode == "DIRECT":
            foo = self.symtab[ln.args[0]]
            if foo[2] == -1:
                ln.errors.append("variable has not been initialised")
                return
            else:
                g.register_x == [2]
                while len(g.register_x) < 6:
                    g.register_x = '0' + g.register_x
                # remember that one can only use indexed addressing along with direct addressing
                if ln.isIndexed:
                    ln.errors.append("Cannot use indexxed based addressing here")
                    return
                g.register_x == hex(str(foo[2]))[2:]
                while len(g.register_x) < 6:
                    g.register_x = '0' + g.register_x

        elif ln.addressMode == "IMMEDIATE":
            g.register_x = hex(t.get_immediate(ln.args[0][1:]))[2:]
            while len(g.register_x) < 6:
                g.register_x = '0' + g.register_x

        elif ln.addressMode == "IMMEDIATE CONST":
            g.register_x = hex(ln.targetAddress)[2:]
            while len(g.register_x) < 6:
                g.register_x = '0' + g.register_x

        elif ln.addressMode == "INDIRECT":
            ln.errors.append("cannot use indirect addressing on an LDX instruction")
            return

def build_instruction_(self, ln):
    arg_type = ln.instructionDetails[0]
    opcode = ln.instructionDetails[2]
    if arg_type == 'm':
        ln.binary = t.put_together(opcode, ln.addressMode, self.ln_getRelative(ln),
                                     ln.display, ln.instructionType, ln.isIndexed)
    elif arg_type == 'r1,r2':
        ln.binary = opcode + g.registers[ln.args[0]][0] + g.registers[ln.args[1]][0]
    elif arg_type == 'r1,n':
        ln.binary = opcode + g.registers[ln.args[0]][0] + hex(int(ln.args[1])-1)[2:]
    elif arg_type == 'r1':
        ln.binary = opcode + g.registers[ln.args[0]][0] + '0'
    elif arg_type == 'n':
        ln.binary = opcode + hex(ln.args[0])[2:] + '0'
    elif arg_type == '0':
        if ln.instruction == "RSUB":
            ln.binary = '4F0000'
        else:
            while len(opcode) < 2:
                opcode = '0' + opcode
            ln.binary = opcode

# returns the value stored at a memory location referenced using a symbol
# returns -1 if not initialised
def get_indirect_(self, label):
    ta_address = self.symtab[label][0]
    for key, value in self.symtab.items():
        if value[0] == ta_address:
            return value[2]
    return -1

# returns a memory address of type int
def get_immediate_(self, label):
    return self.symtab[label][0]   #get the address of the label

def get_direct_(self, label):
    return self.symtab[label][2]   #get the value stored at the memory location specified by the label

def printWarnings_(self, ln):
    if ln.isUselessLine:
        return
    if len(ln.warnings) != 0:
        print("all the beans:", ln.__dict__)
        print(ln.warnings)

def printErrors_(self, ln):
    if ln.isUselessLine:
        return
    if len(ln.errors) != 0:
        print("all the beans:", ln.__dict__)
        print(ln.errors)
