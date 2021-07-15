import global_vars as g
import tools as t

class controlSection():

    def __init__(self, input):
        self.name = input
        self.littab = {}
        self.symtab = {}
        self.program_block_details = {}
        self.line_objects = []
        self.current_block = 0
        self.errorCount = 0
        self.warningCount = 0
        self.literalsToProcess = False

    def addLine(self, input):
        try:
            line_ = Line.Line(input)
            return line_.pass_1(g.locctr)
        except:
            print("error:", sys.exc_info()[1])
            traceback.print_tb(sys.exc_info()[2])
            print("\n\n instruction details:", line_obj.__dict__)
            exit(0)
        if len(line_.errors) != 0:
            print("Errors found in pass 1. Printing possible warnings/errors")
            pp.pprint(line_.__dict__)
            for i in range(index-1, -1, -1):
                if len(self.line_objects[i].warnings) != 0:
                    self.line_objects[i].printWarnings(i+1)
                if len(self.line_objects[i].errors) != 0:
                    self.line_objects[i].printErrors(i+1)
            exit(0)
        self.line_objects.append(line_)
        g.locctr += line_.size
        if index == 0:
            if line_.instruction == "START":
                g.locctr += g.start_address
                line_.location = g.start_address
            if line_.instruction != 'CSECT':
                self.program_block_details[0] = ["default",g.locctr,0]

    # to be called at the end of pass 1
    def wrapUp(self):
        if (self.literalsToProcess):
            self.cleanUpLittab()
        self.cleanUpProgramBlock()

    # this takes care of literals that still have to be processed by an LTORG
    # if any literals are unprocessed, we just place an LTORG instruction at the end of the current ctrl section
    def cleanUpLittab(self):
        try:
            imaginary_instruction = Line.Line("LTORG")
            imaginary_instruction.pass_1(g.locctr)
            self.line_objects.append(imaginary_instruction)
        except:
            print("error happened during cleanUpLittab")
            print("\n\n the littab")
            pprint.pprint(g.littab)
            exit(0)

    # this method is to set the length of the last program block
    def cleanUpProgramBlock(self):
        last = self.program_block_details[len(self.program_block_details)-1]
        last[2] = g.locctr - last[1]#setting the length of the program block
        self.program_block_details[len(self.program_block_details)-1] = last

    def pass_2(self):

        for index, line_obj in enumerate(g.line_objects):
            if index != len(g.line_objects)-1:   #since the last instruction has nothing after it
                g.line_objects[index].programCounter = g.line_objects[index+1].location
            try:
                if (not line_obj.pass_2()):
                    print("Errors found in pass 2. Printing possible warnings/errors")
                    # pp.pprint(g.line_objects[i].__dict__)
                    g.line_objects[index].printWarnings(index+1)
                    g.line_objects[index].printErrors(index+1)
                    exit(0)
            except:
                print("error:", sys.exc_info()[:2])
                traceback.print_tb(sys.exc_info()[2])
                print("\n\n instruction details:", line_obj.__dict__)
                exit(0)

    # returns all the records that go into the output file
    def getOutput(self):
        pass
