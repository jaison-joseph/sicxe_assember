# main.py
import sys
import Program
if len(sys.argv) != 3:
    print('usage: <python> <input file name> <output file name>.\nfile must be placed'+
    'in the tests directory')
    sys.exit(0)

inputFileName = sys.argv[1]
outputFileName = sys.argv[2]

try:
    f = open("../tests/"+inputFileName)
    f.close()
except FileNotFoundError:
    print('file not found. file must be placed in the \'tests\' directory')
    exit(0)

# the constructor does the pass 1 stuff
program = Program.Program(inputFileName, outputFileName)
# exit(0)
program.run()
program.dump()
