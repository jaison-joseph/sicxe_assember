
# this variable holds all the info pertaining to the
# ctrl section that this line is a part of
# since now the ctrl sect and line have references to the same object, of this class
# they can talk to each other via the variables

class controlSectionVars():

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
