import global_vars as g
import re
from math import ceil


#accepts an int of base 10 and spits out a 3 digit hex number
#in 2s complement
def twocomp(x):
    l = []

    #convert to binary
    l = list(bin(x))[2:]
    if l[0] == '-': #in case of a negative number
        l = l[1:]

    # add trailing characters (padding to set size to 12)
    while len(l) < 12:
        l.insert(0,'0')

    if (x < 0):
        #flip 1 and 0
        l = ['0' if i == '1' else '1' for i in l]

        '''
        carry 1 dig 0: carry 0 dig = 1
        carry 1 dig 1: carry 1 dig = 0
        carry 0 dig 1: carry 0 dig = 1
        carry 0 dig 0: carry 0 dig = 0
        '''
        #adding 1 to result
        carry = 1
        l.reverse() #we do this since the carry has to be added starting from the least significant number
        for i,dig in enumerate(l):
            if carry == 0:
                continue
            elif carry == 1:
                if dig == "0":
                    l[i] = '1'
                    carry = 0
                else:
                    l[i] = '0'
            else:
                raise Exception("somehthing went wrong while carrying nummbers")

        l.reverse() #to get back to the original

    l = hex(int(''.join(l), 2))[2:]
    # 0 padding since the length could be lost
    while len(l) < 3:
        l = '0' + l
    return l

def put_together(opcode, address_mode, relativeness, disp, instructionType, isIndexed):
    flags = {"n":"0", "i":"0", "x":"0", "b":"0", "p":"0", "e":"0"}

    if address_mode == "DIRECT":
        flags["n"] = "1"
        flags["i"] = "1"
    elif address_mode == "IMMEDIATE" or address_mode == "IMMEDIATE CONST":
        flags["n"] = "0"
        flags["i"] = "1"
    else:   #INDIRECT
        flags["n"] = "1"
        flags["i"] = "0"

    if relativeness == "pc":
        flags["p"] = "1"
    elif relativeness == "base":
        flags["b"] = "1"
    elif relativeness == "nothing":
        disp = str(disp)
        while len(disp) < 3:    #since the width of the disp field in extended mode is 20 bits
            disp = '0'+disp
    elif relativeness == "extended":
        disp = str(disp)
        while len(disp) < 5:    #since the width of the disp field in extended mode is 20 bits
            disp = '0'+disp
    elif relativeness == "sic":
        flags["n"] = "0"
        flags["i"] = "0"
        disp = bin(disp)[2:]
        while len(disp) < 15:    #since the width of the disp field in extended mode is 20 bits
            disp = '0' + disp
        flags['b'] = disp[0]
        flags['p'] = disp[1]
        flags['e'] = disp[2]
        disp = int(disp[3:],2)
        disp = hex(disp)
        while len(disp) < 3:    #since the width of the disp field in extended mode is 20 bits
            disp = '0' + disp

    else:   #invalid ta
        return ""

    # print("\n\n details: ", [opcode, address_mode, relativeness, disp, instructionType])
    # print("flags: ", flags)

    if instructionType == "EXTENDED INSTRUCTION":
        flags["e"] = "1"
        flags["n"] = "1"
        flags["i"] = "1"

    if isIndexed:
        flags["x"] = "1"

    part_1 = hex(int(opcode,16) + int(flags['n']+flags['i'], 2))
    part_2 = hex(int(flags['x']+flags['b']+flags['p']+flags['e'],2))

    part_1 = part_1[2:]
    part_2 = part_2[2:]

    while len(part_1) < 2:
        part_1 = '0' + part_1

    return part_1 + part_2 + disp

# returns the value stored at a memory location referenced using a symbol
# returns -1 if not initialised
def get_indirect(label):
    ta_address = g.symtab[label][0]
    for key, value in g.symtab.items():
        if value[0] == ta_address:
            return value[2]
    return -1

# returns a memory address of type int
def get_immediate(label):
    return g.symtab[label][0]   #get the address of the label

def get_direct(label):
    return g.symtab[label][2]   #get the value stored at the memory location specified by the label

def info(input, what_you_want):

    type = -1
    content = -1
    size = -1

    input = str(input)

    #checking for a char or hex constant
    pattern = "^C'(\w+)'$"          #single quotes check
    pattern_2 = '^C"(\w+)"$'        #double quotes check
    result = re.search(pattern, input)
    if result is None:
        result = re.search(pattern_2, input)
        if result is None:
            pass
    if result is not None:
        size = len(result.group(1))
        type = "char"
        content = list(result.group(1))
        for i in range(len(content)):
            content[i] = hex(ord(content[i]))[2:]
            if len(content[i]) < 2:
                content[i] = '0' + content[i]
        content = ''.join(content)

    if size == -1:
        pattern = "^X'([1234567890abcdefABCDEF]+)'$"          #single quotes check
        pattern_2 = '^X"([1234567890abcdefABCDEF]+)"$'        #double quotes check
        result = re.search(pattern, input)
        if result is None:
            result = re.search(pattern_2, input)
            if result is None:
                pass
        if result is not None:
            size = ceil(len(result.group(1))/2)
            type = "hex"
            content = result.group(1)


    #maybe its a word
    if size == -1:
        try:
            word_value = int(input, 16)
            size = -1
            type = "int"
            content = str(input)
        except ValueError:
            pass

    if what_you_want == 'type':
        return type
    elif what_you_want == 'size':
        return size
    elif what_you_want == 'content':
        return content
    elif what_you_want == 'all':
        return {
            "type": type,
            "content": content,
            "size": size
        }
    else:
        return -1

def getCorrespondingNumber(input):
    try:
        result = int(input)
        return [result, "A"]
    except ValueError:
        if input == '*':
            return [g.locctr, 'R']
        if input not in g.symtab.keys():
            return -1
        return [g.symtab[input][0], g.symtab[input][-2]]

def pad(input, final_length, align = "c", bit = ' '):
    if type(input) is not str:
        input = str(input)
    pad = bit * (final_length-len(input))
    if input.count("'") and input.count('"'):   #to account for the back slash to escape the quotes while printing
        pad = bit * (final_length-len(input)-input.count("'"))
    if align == "r":
        return pad + input
    elif align == "l":
        return input + pad
    else:
        return pad[:len(pad)//2] + input + pad[len(pad)//2:]

if __name__ == "__main__":
    # foo = info('C"EOF"', 'all')
    # print([foo["type"], foo["size"], foo["content"]] )
    # print(info('X"1eee"', 'all'))
    # print(info(123, 'all'))
    # print(info('', 'all'))
    print(pad('a', 4, '0'))
