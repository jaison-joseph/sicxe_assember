# main.py
import sys
import Program
if len(sys.argv) != 2:
    print('usage: <python> <name of the file>.\nfile must be placed'+
    'in the tests directory')
    sys.exit(0)

fileName = sys.argv[1]

try:
    f = open("../tests/"+fileName)
    f.close()
except FileNotFoundError:
    print('file not found. file must be placed in the \'tests\' directory')
    exit(0)

program_obj = Program.Program(fileName)
program_obj.pass_1()
