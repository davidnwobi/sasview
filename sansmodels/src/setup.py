"""
 Installation script for SANS models

  - To compile and install:
      python setup.py install
  - To create distribution:
      python setup.py bdist_wininst
  - To create odb files:
      python setup.py odb

"""
import sys
import os

from numpy.distutils.misc_util import get_numpy_include_dirs
numpy_incl_path = os.path.join(get_numpy_include_dirs()[0], "numpy")

def createODBcontent(class_name):
    """
        Return the content of the Pyre odb file for a given class
        @param class_name: Name of the class to write an odb file for [string]
        @return: content of the file [string]
    """
    content  = "\"\"\"\n"
    content += "  Facility for SANS model\n\n"
    content += "  WARNING: THIS FILE WAS AUTOGENERATED AT INSTALL TIME\n"
    content += "           DO NOT MODIFY\n\n"
    content += "  This code was written as part of the DANSE project\n"
    content += "  http://danse.us/trac/sans/\n"
    content += "  @copyright 2007:"
    content += "  SANS/DANSE Group (University of Tennessee), for the DANSE project\n\n"
    content += "\"\"\"\n"
    content += "def model():\n"
    content += "    from ScatteringIntensityFactory import ScatteringIntensityFactory\n"
    content += "    from sans.models.%s import %s\n" % (class_name, class_name)
    content += "    return ScatteringIntensityFactory(%s)('%s')\n"\
                 % (class_name, class_name)

    return content

def createODBfiles():
    """
       Create odb files for all available models
    """
    from sans.models.ModelFactory import ModelFactory
    
    class_list = ModelFactory().getAllModels()
    for name in class_list:
        odb = open("sans/models/pyre/%s.odb" % name, 'w')
        odb.write(createODBcontent(name))
        odb.close()
        print "sans/models/pyre/%s.odb created" % name
        
#
# Proceed with installation
#

# First, create the odb files
if len(sys.argv) > 1 and sys.argv[1].lower() == 'odb':
    print "Creating odb files"
    try:
        createODBfiles()
    except:    
        print "ERROR: could not create odb files"
        print sys.exc_value
    sys.exit()

# Then build and install the modules
from distutils.core import setup, Extension


# Build the module name
srcdir  = "sans/models/c_extensions"
igordir = "libigor"

print "Installing SANS models"


setup(
    name="models",
    version = "0.4",
    description = "Python module for SANS scattering models",
    author = "Mathieu Doucet",
    author_email = "doucet@nist.gov",
    url = "http://danse.us/trac/sans",
    
    # Place this module under the sans package
    #ext_package = "sans",
    
    # Use the pure python modules
    package_dir = {"sans_extension":"sans/models/c_extensions"},
    
    packages = ["sans","sans.models","sans.models.test",
                "sans_extension","sans.models.pyre"],
    
    ext_modules = [ Extension("sans_extension.c_models",
     sources = [
        "sans/models/c_models/c_models.cpp",
        #srcdir+"/CSphereModel.c",
        #srcdir+"/sphere.c",
        "sans/models/c_models/CSphereModel.cpp",
        "sans/models/c_models/COnionModel.cpp",
        "sans/models/c_models/onion.cpp",
        srcdir+"/onion.c",
        "sans/models/c_models/CReflModel.cpp",
        "sans/models/c_models/refl.cpp",
        srcdir+"/refl.c",
        srcdir+"/SquareWell.c",
        "sans/models/c_models/CSquareWellStructure.cpp",  
        "sans/models/c_models/SquareWell.cpp", 
        srcdir+"/StickyHS.c",         
        "sans/models/c_models/CStickyHSStructure.cpp", 
        "sans/models/c_models/StickyHS.cpp",      
        srcdir+"/Hardsphere.c",         
        "sans/models/c_models/CHardsphereStructure.cpp", 
        "sans/models/c_models/Hardsphere.cpp",    
        srcdir+"/DiamCyl.c",         
        "sans/models/c_models/CDiamCylFunc.cpp", 
        "sans/models/c_models/DiamCyl.cpp",   
        srcdir+"/DiamEllip.c",         
        "sans/models/c_models/CDiamEllipFunc.cpp", 
        "sans/models/c_models/DiamEllip.cpp",     
        srcdir+"/HayterMSA.c",         
        "sans/models/c_models/CHayterMSAStructure.cpp", 
        "sans/models/c_models/HayterMSA.cpp",             
        "sans/models/c_models/sphere.cpp",
        srcdir+"/fuzzysphere.c",
        "sans/models/c_models/CFuzzySphereModel.cpp",
        "sans/models/c_models/fuzzysphere.cpp",
        #srcdir+"/CCylinderModel.c",
        "sans/models/c_models/CCylinderModel.cpp",
        "sans/models/c_models/cylinder.cpp",
        "sans/models/c_models/parameters.cpp",
        "sans/models/c_models/dispersion_visitor.cpp",
        srcdir+"/cylinder.c",
        #srcdir+"/CParallelepiped.c",
        "sans/models/c_models/CParallelepipedModel.cpp",
        "sans/models/c_models/parallelepiped.cpp",
        srcdir+"/parallelepiped.c",
        #srcdir+"/CCoreShellCylinderModel.c",
        "sans/models/c_models/CCoreShellCylinderModel.cpp",
        "sans/models/c_models/coreshellcylinder.cpp",
        srcdir+"/core_shell_cylinder.c",
        #srcdir+"/CHollowCylinderModel.c",
        "sans/models/c_models/CHollowCylinderModel.cpp",
        "sans/models/c_models/hollowcylinder.cpp",
        srcdir+"/hollow_cylinder.c",
        #srcdir+"/CCoreShellModel.c",
        #srcdir+"/core_shell.c",
        "sans/models/c_models/CCoreShellModel.cpp",
        "sans/models/c_models/coreshellsphere.cpp",
        #srcdir+"/CEllipsoidModel.c",
        "sans/models/c_models/CEllipsoidModel.cpp",
        "sans/models/c_models/ellipsoid.cpp",        
        srcdir+"/ellipsoid.c",
        "sans/models/c_models/CCoreFourShellModel.cpp",
        "sans/models/c_models/corefourshell.cpp",
        srcdir+"/corefourshell.c",
        #srcdir+"/CEllipticalCylinderModel.c",
        "sans/models/c_models/CEllipticalCylinderModel.cpp",
        "sans/models/c_models/ellipticalcylinder.cpp",                
        srcdir+"/elliptical_cylinder.c",
        #srcdir+"/CTriaxialEllipsoidModel.c",
        "sans/models/c_models/CTriaxialEllipsoidModel.cpp",
        "sans/models/c_models/triaxialellipsoid.cpp",                
        srcdir+"/triaxial_ellipsoid.c",
        #srcdir+"/CFlexibleCylinderModel.c",
        "sans/models/c_models/CFlexibleCylinderModel.cpp",
        "sans/models/c_models/flexiblecylinder.cpp",                
        srcdir+"/flexible_cylinder.c",
        "sans/models/c_models/CFlexCylEllipXModel.cpp",
        "sans/models/c_models/flexcyl_ellipX.cpp",         
        srcdir+"/flexcyl_ellipX.c",
        #srcdir+"/CStakedDisksModel.c",
        "sans/models/c_models/CSCCrystalModel.cpp",
        "sans/models/c_models/sc.cpp",                
        srcdir+"/sc.c",
        "sans/models/c_models/CFCCrystalModel.cpp",
        "sans/models/c_models/fcc.cpp",                
        srcdir+"/fcc.c",
        "sans/models/c_models/CBCCrystalModel.cpp",
        "sans/models/c_models/bcc.cpp",                
        srcdir+"/bcc.c",
        "sans/models/c_models/CStackedDisksModel.cpp",
        "sans/models/c_models/stackeddisks.cpp",                
        srcdir+"/stacked_disks.c",
        #srcdir+"/CLamellarModel.c",
        "sans/models/c_models/CLamellarModel.cpp",
        "sans/models/c_models/lamellar.cpp",                
        srcdir+"/lamellar.c",
        #srcdir+"/CLamellarFFHGModel.c",
        "sans/models/c_models/CLamellarFFHGModel.cpp",
        "sans/models/c_models/lamellarFF_HG.cpp",                
        srcdir+"/lamellarFF_HG.c",
        #srcdir+"/CLamellarPSModel.c",
        "sans/models/c_models/CLamellarPSModel.cpp",
        "sans/models/c_models/lamellarPS.cpp",                
        srcdir+"/lamellarPS.c",
        #srcdir+"/CLamellarPSHGModel.c",
        "sans/models/c_models/CLamellarPSHGModel.cpp",
        "sans/models/c_models/lamellarPS_HG.cpp",                
        srcdir+"/lamellarPS_HG.c",
        #"sans/models/c_models/CLamellarPCrystalModel.cpp",
        #"sans/models/c_models/lamellarPC.cpp",                
        #srcdir+"/lamellarPC.c",
        #srcdir+"/COblateModel.c",
        "sans/models/c_models/CCoreShellEllipsoidModel.cpp",
        "sans/models/c_models/spheroid.cpp",   
        srcdir+"/spheroid.c",             
        #srcdir+"/COblateModel.c",
        #"sans/models/c_models/COblateModel.cpp",
        #"sans/models/c_models/oblate.cpp",                
        #srcdir+"/oblate.c",
        #srcdir+"/CProlateModel.c",
        #"sans/models/c_models/CProlateModel.cpp",
        #"sans/models/c_models/prolate.cpp",                
        #srcdir+"/prolate.c",
        #srcdir+"/CMultishellModel.c",
        "sans/models/c_models/CMultiShellModel.cpp",
        "sans/models/c_models/multishell.cpp",                
        srcdir+"/multishell.c",
        #srcdir+"/CVesicleModel.c",
        "sans/models/c_models/CVesicleModel.cpp",
        "sans/models/c_models/vesicle.cpp",                
        srcdir+"/vesicle.c",
        #srcdir+"/CBinaryHSModel.c",
        "sans/models/c_models/CBinaryHSModel.cpp",
        "sans/models/c_models/binaryHS.cpp",                
        "sans/models/c_models/CPoly_GaussCoil.cpp",
        "sans/models/c_models/polygausscoil.cpp",   
        srcdir+"/rpa.c",             
        "sans/models/c_models/CRPAModel.cpp",
        "sans/models/c_models/rpa.cpp", 
        srcdir+"/fractal.c",             
        "sans/models/c_models/CFractalModel.cpp",
        "sans/models/c_models/fractal.cpp", 
        
        #gammainc function need to imported from somewhere  
        #srcdir+"/polyexclvol.c",             
        #"sans/models/c_models/CPolymerExclVolModel.cpp",
        #"sans/models/c_models/polyexclvol.cpp",  
         
        srcdir+"/polygausscoil.c",             
        srcdir+"/binaryHS.c",
        srcdir+"/disperser.c",
        igordir+"/libCylinder.c",
        igordir+"/libStructureFactor.c",
        igordir+"/libSphere.c",
        igordir+"/libTwoPhase.c",
        srcdir+"/gaussian.c",
        srcdir+"/CGaussian.c",
        srcdir+"/logNormal.c",
        srcdir+"/CLogNormal.c",
        srcdir+"/schulz.c",
        srcdir+"/CSchulz.c",
        srcdir+"/lorentzian.c",
        srcdir+"/CLorentzian.c"
            ],
         include_dirs=[igordir,srcdir,"sans/models/c_models",numpy_incl_path])])
        
