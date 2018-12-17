#-*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *


fileLoc = os.getcwd() + '/'
for filename in os.listdir(fileLoc):
    if filename.endswith(".odb"):

        odb = session.openOdb(
                name=filename)
        odb = session.odbs[filename]
        session.viewports['Viewport: 1'].setValues(displayedObject=odb)
        session.xyDataListFromField(
        odb=odb, outputPosition=NODAL, variable=(
                ('RF', NODAL, ((COMPONENT, 'RF3'), )), ), nodeSets=(
                    'RF_POINT', ))
        x0 = 0
        #x0 = session.xyDataObjects['RF:RF3 PI: PLATEN-1 N: 1']
        lastone = len(session.xyDataObjects.items())
        x0 = session.xyDataObjects[session.xyDataObjects.items()[lastone - 1][0]]
        session.writeXYReport(fileName=filename[:-4]+'.txt',xyData=(x0,))
        odb.close()
        f= open(filename[:-4]+".txt","r")
        oline=f.readlines()
#Here, we prepend the string we want to on first line
        oline.insert(0,filename[:-4])
        f.close()


#We again open the file in WRITE mode
        src=open(filename[:-4]+".txt","w")
        src.writelines(oline)
        src.close()

