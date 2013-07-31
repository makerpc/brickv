'''OpenGL extension SGIX.ycrcba

This module customises the behaviour of the 
OpenGL.raw.GL.SGIX.ycrcba to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/SGIX/ycrcba.txt
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions, wrapper
from OpenGL.GL import glget
import ctypes
from OpenGL.raw.GL.SGIX.ycrcba import *
### END AUTOGENERATED SECTION