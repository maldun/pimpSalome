import os
import sys
import subprocess


class Pimp(object):
    """ Class for salome modifiying"""

    def __init__(self):
        # get workpath
        WORK_DIR=os.getcwd()
        # read pimp.cfg
        cfg_file = open(WORK_DIR + '/pimp.cfg','r')

        # get lines and filter out newlines
        cfg_lines = cfg_file.readlines()
        cfg_lines = [line.rstrip() for line in cfg_lines if line.rstrip() ]

        self.cfg = cfg_lines
        # close cfg file
        cfg_file.close()

        #make setup
        self.setup()

    def findKeyWordOption(self,key):
        """
        Searches for options in cfg
        """
        for line in self.cfg:
            if key in line:
                return line

    def getSalomeHome(self):
        exec(self.findKeyWordOption('SALOME_HOME'))
        self.salome_home = os.path.expanduser(SALOME_HOME)

    def getFolders(self):
        """
        Get Saolome binary folders
        """
        content = subprocess.check_output(['ls',self.salome_home + '/prerequisites/'])
        content = content.splitlines()
        self.folders = content

    def getLibDirs(self):
        """
        get directories for libraries
        """
        exec(self.findKeyWordOption('SYSTEM_LIB'))
        self.system_lib = SYSTEM_LIB
        self.debian_lib = self.salome_home + '/prerequisites/debianForSalome/lib' 

    def findProgram(self,prog_name):
        
        for prog in self.folders:
            if prog_name in prog:
                return prog

    def getPythonBin(self):
        
        python_ver = self.findProgram("Python")
        self.python_bin = self.salome_home + '/prerequisites/' + python_ver + '/bin/python'
        print self.python_bin

    def getNumpyBuildConfig(self):

        output = []
        exec(self.findKeyWordOption('NUMPY_FC'))
        output+=[NUMPY_FC]

        return output

    def installNumpy(self):
        
        # get directories
        exec(self.findKeyWordOption('NUMPY_SRC'))
        NUMPY_SRC = os.path.expanduser(NUMPY_SRC)
        numpy_setup = NUMPY_SRC + '/setup.py'
        numpy_home =  self.salome_home + '/prerequisites/' + self.findProgram('Numpy') + '/'
        
        #clean up
        subprocess.call([self.python_bin,numpy_setup,'clean'])
        #build
        np_opts = self.getNumpyBuildConfig()
        subprocess.call([self.python_bin,numpy_setup,'build'] + np_opts)
        #install
        subprocess.call([self.python_bin,numpy_setup,'install',
                         '--force','--prefix=' + numpy_home])

        #post install (assuming install goes to lib64)
        subprocess.call(['rm','-r', numpy_home + '/lib'])
        subprocess.call(['ln','-s', numpy_home + '/lib64',numpy_home + '/lib'])
        libg = '/libgfortran.so.3'
        subprocess.call(['rm', self.debian_lib + libg])
        subprocess.call(['ln','-s', self.system_lib + libg, self.debian_lib + libg])

    def setup(self):
        
        # set basic paths
        self.getSalomeHome()
        self.getFolders()
        self.getPythonBin()
        self.getLibDirs()
        # install packages
        self.installNumpy()

Pimp()
