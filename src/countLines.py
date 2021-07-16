# usage: python countLines.py [list of fileNames to be omitted]
# if any of the file names are not found, it will be ignored

from os import listdir, getcwd
from os.path import isfile, join
import sys

mypath = getcwd()
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# note: sys.argv[0] is the name of 'this' file 
for i in range(0,len(sys.argv)):
    fname = sys.argv[i]
    if fname in onlyfiles:
        onlyfiles.remove(fname)
number = 0
for fileName in onlyfiles:
    number += sum(1 for ln in open(fileName))
print("\n the number of lines in this directory is:", number, "lines")
