import Line
import pprint
import global_vars as g

pp = pprint.PrettyPrinter()

class Program():

    def __init__(self, fileName):

        self.line_objects = []
        self.locctr = 0
        f = open("../tests/"+fileName)
        for ln in f:
            self.line_objects.append(Line.Line(ln))


    def pass_1(self):
        for index, line_obj in enumerate (self.line_objects):
            line_obj.pass_1()
            if line_obj.size == -1:
                for i in range(index):
                    print("Errors found in pass 1. Printing possible warnings/errors")
                    pp.pprint(self.line_objects[i].__dict__)
                    self.line_objects[i].printWarnings(i+1)
                    self.line_objects[i].printWarnings(i+1)
                    exit(0)
            line_obj.update_symtab(self.locctr)
            self.locctr += line_obj.size
            if index != 0:
                self.line_objects[index-1].setProgramCounter(self.locctr)
        # print(self.line_objects[-1].raw)
        # print(self.line_objects[-1].content)

    def pass_2(self):
        for index, line_obj in enumerate(self.line_objects):
            line_obj.pass_2()  #since the last instruction has nothing after it

    def observe(self):
        for line_obj in self.line_objects:
            print([line_obj.location, line_obj.size, line_obj.label, line_obj.instruction, line_obj.args, line_obj.binary])
        print(g.symtab)
