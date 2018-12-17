# -*- coding: mbcs -*-
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

pfits = [0.005,0.01,0.015,0.02,0.025,0.03]
a = ['0_005','0_01','0_015','0_02','0_025','0_03']
count = 0

fileLoc = os.getcwd() + '/'
for i in pfits:
    depth = 10
    displacement = -5
    host_sizeA = -50
    host_sizeB = 50
    graft_size = 8.5
    pressfit_size_bone = i
    pressfit_size_cart = i
    coeff_frict_cart = 0.2
    coeff_frict_bone = 0.5
    name = 'CF_0_5_P_0_05_M_80_'+a[count]
    count = count+1

    model = mdb.models['Model-1']
    #host
    model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    model.sketches['__profile__'].rectangle(point1=(host_sizeA, host_sizeB),
        point2=(host_sizeB, host_sizeA))
    model.Part(dimensionality=THREE_D, name='host', type=
        DEFORMABLE_BODY)
    model.parts['host'].BaseSolidExtrude(depth=depth, sketch=
        model.sketches['__profile__'])

    #cyl
    model.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    model.sketches['__profile__'].CircleByCenterPerimeter(center=(
        0.0, 0.0), point1=(graft_size, 0.0))
    model.Part(dimensionality=THREE_D, name='cyl', type=
        DEFORMABLE_BODY)
    model.parts['cyl'].BaseSolidExtrude(depth=depth, sketch=
        model.sketches['__profile__'])

    model.rootAssembly.DatumCsysByDefault(CARTESIAN)

    model.rootAssembly.Instance(dependent=ON, name='cyl-1', part=
        model.parts['cyl'])


    model.Part(name='host-Cart', objectToCopy=
        model.parts['host'])
    model.Part(name='cyl-cart', objectToCopy=
        model.parts['cyl'])
    model.parts['host-Cart'].features['Solid extrude-1'].setValues(
        depth=1.0)
    model.parts['host-Cart'].regenerate()
    model.parts['cyl-cart'].features['Solid extrude-1'].setValues(
        depth=1.0)
    model.parts['cyl-cart'].regenerate()


    model.rootAssembly.Instance(dependent=ON, name='cyl-1', part=
        model.parts['cyl'])
    model.rootAssembly.Instance(dependent=ON, name='cyl-cart-1',
        part=model.parts['cyl-cart'])
    model.rootAssembly.Instance(dependent=ON, name='host-1', part=
        model.parts['host'])
    model.rootAssembly.Instance(dependent=ON, name='host-Cart-1',
        part=model.parts['host-Cart'])
    model.rootAssembly.translate(instanceList=('host-Cart-1',
        'cyl-cart-1'), vector=(0.0, 0.0, 15.0))


    #cuts ie boolean
    model.rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
        model.rootAssembly.instances['cyl-1'], ), instanceToBeCut=
        model.rootAssembly.instances['host-1'], name='host_cut',
        originalInstances=SUPPRESS)
    model.rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
        model.rootAssembly.instances['cyl-cart-1'], ),
        instanceToBeCut=model.rootAssembly.instances['host-Cart-1']
        , name='host_cart_cut', originalInstances=SUPPRESS)
    model.rootAssembly.features['cyl-cart-1'].resume()
    model.rootAssembly.features['cyl-1'].resume()



    model.Tie(adjust=ON, master=Region(
        side1Faces=model.rootAssembly.instances['cyl-1'].faces.getSequenceFromMask(
        mask=('[#2 ]', ), )), name='Constraint-1', positionToleranceMethod=COMPUTED
        , slave=Region(
        side1Faces=model.rootAssembly.instances['cyl-cart-1'].faces.getSequenceFromMask(
        mask=('[#4 ]', ), )), thickness=ON, tieRotations=ON)
    model.Tie(adjust=ON, master=Region(
        side1Faces=model.rootAssembly.instances['host_cut-1'].faces.getSequenceFromMask(
        mask=('[#20 ]', ), )), name='Constraint-2', positionToleranceMethod=
        COMPUTED, slave=Region(
        side1Faces=model.rootAssembly.instances['host_cart_cut-1'].faces.getSequenceFromMask(
        mask=('[#40 ]', ), )), thickness=ON, tieRotations=ON)



    model.ConstrainedSketch(name='__edit__', objectToCopy=
        model.parts['cyl'].features['Solid extrude-1'].sketch)
    model.parts['cyl'].projectReferencesOntoSketch(filter=
        COPLANAR_EDGES, sketch=model.sketches['__edit__'],
        upToFeature=model.parts['cyl'].features['Solid extrude-1'])
    model.sketches['__edit__'].autoDimension(objectList=(
        model.sketches['__edit__'].geometry[2], ))

    model.sketches['__edit__'].dimensions[0].setValues(value=10+pressfit_size_bone)
    model.parts['cyl'].features['Solid extrude-1'].setValues(
        sketch=model.sketches['__edit__'])
    del model.sketches['__edit__']
    model.parts['cyl'].regenerate()

    model.ConstrainedSketch(name='__edit__', objectToCopy=
        model.parts['cyl-cart'].features['Solid extrude-1'].sketch)
    model.parts['cyl-cart'].projectReferencesOntoSketch(filter=
        COPLANAR_EDGES, sketch=model.sketches['__edit__'],
        upToFeature=
        model.parts['cyl-cart'].features['Solid extrude-1'])
    model.sketches['__edit__'].autoDimension(objectList=(
        model.sketches['__edit__'].geometry[2], ))
    model.sketches['__edit__'].dimensions[0].setValues(value=10+pressfit_size_cart)
    model.parts['cyl-cart'].features['Solid extrude-1'].setValues(
        sketch=model.sketches['__edit__'])
    del model.sketches['__edit__']
    model.parts['cyl-cart'].regenerate()

    model.rootAssembly.regenerate()

    model.StaticStep(name='pressfit', previous='Initial')


    model.ContactProperty('IntPropbone')
    model.interactionProperties['IntPropbone'].TangentialBehavior(
        dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None,
        formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION,
        pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF,
        table=((coeff_frict_bone, ), ), temperatureDependency=OFF)
    model.interactionProperties['IntPropbone'].NormalBehavior(
        allowSeparation=ON, constraintEnforcementMethod=DEFAULT,
        pressureOverclosure=HARD)


    model.ContactProperty('IntPropcart')
    model.interactionProperties['IntPropcart'].TangentialBehavior(
        dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None,
        formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION,
        pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF,
        table=((coeff_frict_cart, ), ), temperatureDependency=OFF)
    model.interactionProperties['IntPropcart'].NormalBehavior(
        allowSeparation=ON, constraintEnforcementMethod=DEFAULT,
        pressureOverclosure=HARD)


    model.SurfaceToSurfaceContactStd(adjustMethod=NONE,
        clearanceRegion=None, createStepName='pressfit', datumAxis=None,
        initialClearance=OMIT, interactionProperty='IntPropcart', interferenceType=
        SHRINK_FIT, master=Region(
        side1Faces=model.rootAssembly.instances['host_cart_cut-1'].faces.getSequenceFromMask(
        mask=('[#1 ]', ), )), name='cart_press', slave=Region(
        side1Faces=model.rootAssembly.instances['cyl-cart-1'].faces.getSequenceFromMask(
        mask=('[#1 ]', ), )), sliding=FINITE, thickness=ON)

    model.SurfaceToSurfaceContactStd(adjustMethod=NONE,
        clearanceRegion=None, createStepName='pressfit', datumAxis=None,
        initialClearance=OMIT, interactionProperty='IntPropbone', interferenceType=
        SHRINK_FIT, master=Region(
        side1Faces=model.rootAssembly.instances['host_cut-1'].faces.getSequenceFromMask(
        mask=('[#1 ]', ), )), name='bone_press', slave=Region(
        side1Faces=model.rootAssembly.instances['cyl-1'].faces.getSequenceFromMask(
        mask=('[#1 ]', ), )), sliding=FINITE, thickness=ON)

    #MESH
    model.parts['cyl-cart'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=0.1)
    model.parts['cyl-cart'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=1.0)
    model.parts['cyl-cart'].setMeshControls(algorithm=MEDIAL_AXIS,
        regions=model.parts['cyl-cart'].cells.getSequenceFromMask((
        '[#1 ]', ), ))
    model.parts['cyl-cart'].generateMesh()
    model.parts['cyl'].seedPart(deviationFactor=0.1, minSizeFactor=
        0.1, size=3.0)
    model.parts['cyl'].seedPart(deviationFactor=0.1, minSizeFactor=
        0.1, size=1.0)
    model.parts['cyl'].setMeshControls(algorithm=MEDIAL_AXIS,
        regions=model.parts['cyl'].cells.getSequenceFromMask((
        '[#1 ]', ), ))
    model.parts['cyl'].generateMesh()
    model.parts['host_cart_cut'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=2.0)
    model.parts['host_cart_cut'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=5.0)
    model.parts['host_cart_cut'].setMeshControls(elemShape=TET,
        regions=
        model.parts['host_cart_cut'].cells.getSequenceFromMask((
        '[#1 ]', ), ), technique=FREE)
    model.parts['host_cart_cut'].setElementType(elemTypes=(
        ElemType(elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15,
        elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)),
        regions=(
        model.parts['host_cart_cut'].cells.getSequenceFromMask((
        '[#1 ]', ), ), ))
    model.parts['host_cart_cut'].generateMesh()
    model.parts['host_cut'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=10.0)
    model.parts['host_cut'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=5.0)
    model.parts['host_cut'].setMeshControls(elemShape=TET, regions=
        model.parts['host_cut'].cells.getSequenceFromMask(('[#1 ]',
        ), ), technique=FREE)
    model.parts['host_cut'].setElementType(elemTypes=(ElemType(
        elemCode=C3D20R, elemLibrary=STANDARD), ElemType(elemCode=C3D15,
        elemLibrary=STANDARD), ElemType(elemCode=C3D10, elemLibrary=STANDARD)),
        regions=(model.parts['host_cut'].cells.getSequenceFromMask(
        ('[#1 ]', ), ), ))
    model.parts['host_cut'].generateMesh()


    model.Material(name='bone_host')
    model.materials['bone_host'].Elastic(table=((80.0, 0.4), ))
    model.Material(name='bone_graft')
    model.materials['bone_graft'].Elastic(table=((80.0, 0.4), ))
    model.HomogeneousSolidSection(material='bone_host', name=
        'bone_graft', thickness=None)
    model.Material(name='cart_host')
    model.materials['cart_host'].Elastic(table=((12.0, 0.46), ))
    model.HomogeneousSolidSection(material='cart_host', name=
        'cart_host', thickness=None)
    model.Material(name='cart_graft')
    model.materials['cart_graft'].Elastic(table=((12.0, 0.46), ))
    model.HomogeneousSolidSection(material='cart_graft', name=
        'cart_graft', thickness=None)
    model.HomogeneousSolidSection(material='bone_host', name=
        'bone_host', thickness=None)


    model.parts['host_cut'].SectionAssignment(offset=0.0,
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        cells=model.parts['host_cut'].cells.getSequenceFromMask(
        mask=('[#1 ]', ), )), sectionName='bone_host', thicknessAssignment=
        FROM_SECTION)
    model.parts['host_cart_cut'].SectionAssignment(offset=0.0,
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        cells=model.parts['host_cart_cut'].cells.getSequenceFromMask(
        mask=('[#1 ]', ), )), sectionName='cart_host', thicknessAssignment=
        FROM_SECTION)
    model.parts['cyl-cart'].SectionAssignment(offset=0.0,
        offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
        cells=model.parts['cyl-cart'].cells.getSequenceFromMask(
        mask=('[#1 ]', ), )), sectionName='cart_graft', thicknessAssignment=
        FROM_SECTION)
    model.parts['cyl'].SectionAssignment(offset=0.0, offsetField=''
        , offsetType=MIDDLE_SURFACE, region=Region(
        cells=model.parts['cyl'].cells.getSequenceFromMask(mask=(
        '[#1 ]', ), )), sectionName='bone_graft', thicknessAssignment=FROM_SECTION)
    model.rootAssembly.regenerate()
    model.sections['bone_graft'].setValues(material='bone_graft',
        thickness=None)


    rp = model.parts['cyl-cart'].ReferencePoint(point=(0.0, 0.0, 2.0)).id
    model.rootAssembly.Set(name='RF_POINT', referencePoints=(
        model.rootAssembly.instances['cyl-cart-1'].referencePoints[rp],
        ))
    model.rootAssembly.regenerate()
    model.Coupling(controlPoint=Region(referencePoints=(
        model.rootAssembly.instances['cyl-cart-1'].referencePoints[rp],
        )), couplingType=KINEMATIC, influenceRadius=WHOLE_SURFACE, localCsys=None,
        name='Constraint-3', surface=Region(
        side1Faces=model.rootAssembly.instances['cyl-cart-1'].faces.getSequenceFromMask(
        mask=('[#2 ]', ), )), u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
    model.EncastreBC(createStepName='Initial', localCsys=None,
        name='BC-1', region=Region(
        faces=model.rootAssembly.instances['host_cart_cut-1'].faces.getSequenceFromMask(
        mask=('[#1e ]', ), )+\
        model.rootAssembly.instances['host_cut-1'].faces.getSequenceFromMask(
        mask=('[#1e ]', ), )))
    model.StaticStep(name='disp', previous='pressfit',maxNumInc=100,
                    initialInc=0.1,
                    minInc=0.0000025,
                    maxInc=0.1,
                    nlgeom=ON,matrixSolver=DIRECT, matrixStorage=UNSYMMETRIC)
    model.DisplacementBC(amplitude=UNSET, createStepName='disp',
        distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
        'disp', region=Region(referencePoints=(
        model.rootAssembly.instances['cyl-cart-1'].referencePoints[rp],
        )), u1=UNSET, u2=UNSET, u3=displacement, ur1=UNSET, ur2=UNSET, ur3=UNSET)
    model.FieldOutputRequest(createStepName='pressfit', name='F-Output-1', variables=PRESELECT)
    # model.FieldOutputRequest(createStepName=
    # 'disp', name='F-Output-1', variables=PRESELECT)

    theJob = mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF,
        explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF,
        memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF,
        multiprocessingMode=DEFAULT, name=name,
        nodalOutputPrecision=SINGLE, numCpus=8, numDomains=8, numGPUs=0, queue=None
        , resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='',
        waitHours=0, waitMinutes=0)

    theJob.submit(consistencyChecking=OFF)
        #wait for job to complete before opening the odb and checking the stiffness
    theJob.waitForCompletion()


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

