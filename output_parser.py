from os import chdir
from os import listdir
from os.path import isfile, join
import os

fileLoc = os.getcwd() + '/'
for filename in os.listdir(fileLoc):
    if filename.endswith(".txt"):
	    outputfile = open(filename[:-4] + '_parsed.txt','w')
	    outputfile.write('disp,force\n')
	    f= open(filename[:-4]+".txt","r")
	    oline=f.readlines()

	    for line in oline:

	    	tmpline = ''
	    	if (('  1.' in line) or ('  2.' in line)):
	    		displacement = round((float(line[16:25]) -1)*5,10)
	    		if ' 1. ' in line:
	    			tmpline = str(displacement) + ',' + '0\n'
	    		else:
	    			tmpline = str(displacement) + ',' + line[30:]
	    		tmpline = tmpline.replace('-','')
	    		outputfile.write(tmpline)



