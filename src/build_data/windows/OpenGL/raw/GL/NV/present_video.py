'''OpenGL extension NV.present_video

Automatically generated by the get_gl_extensions script, do not edit!
'''
from OpenGL import platform, constants, constant, arrays
from OpenGL import extensions
from OpenGL.GL import glget
import ctypes
EXTENSION_NAME = 'GL_NV_present_video'
_DEPRECATED = False
GL_FRAME_NV = constant.Constant( 'GL_FRAME_NV', 0x8E26 )
GL_FIELDS_NV = constant.Constant( 'GL_FIELDS_NV', 0x8E27 )
GL_CURRENT_TIME_NV = constant.Constant( 'GL_CURRENT_TIME_NV', 0x8E28 )
GL_NUM_FILL_STREAMS_NV = constant.Constant( 'GL_NUM_FILL_STREAMS_NV', 0x8E29 )
GL_PRESENT_TIME_NV = constant.Constant( 'GL_PRESENT_TIME_NV', 0x8E2A )
GL_PRESENT_DURATION_NV = constant.Constant( 'GL_PRESENT_DURATION_NV', 0x8E2B )
glPresentFrameKeyedNV = platform.createExtensionFunction( 
'glPresentFrameKeyedNV',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,constants.GLuint64EXT,constants.GLuint,constants.GLuint,constants.GLenum,constants.GLenum,constants.GLuint,constants.GLuint,constants.GLenum,constants.GLuint,constants.GLuint,),
doc='glPresentFrameKeyedNV(GLuint(video_slot), GLuint64EXT(minPresentTime), GLuint(beginPresentTimeId), GLuint(presentDurationId), GLenum(type), GLenum(target0), GLuint(fill0), GLuint(key0), GLenum(target1), GLuint(fill1), GLuint(key1)) -> None',
argNames=('video_slot','minPresentTime','beginPresentTimeId','presentDurationId','type','target0','fill0','key0','target1','fill1','key1',),
deprecated=_DEPRECATED,
)

glPresentFrameDualFillNV = platform.createExtensionFunction( 
'glPresentFrameDualFillNV',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,constants.GLuint64EXT,constants.GLuint,constants.GLuint,constants.GLenum,constants.GLenum,constants.GLuint,constants.GLenum,constants.GLuint,constants.GLenum,constants.GLuint,constants.GLenum,constants.GLuint,),
doc='glPresentFrameDualFillNV(GLuint(video_slot), GLuint64EXT(minPresentTime), GLuint(beginPresentTimeId), GLuint(presentDurationId), GLenum(type), GLenum(target0), GLuint(fill0), GLenum(target1), GLuint(fill1), GLenum(target2), GLuint(fill2), GLenum(target3), GLuint(fill3)) -> None',
argNames=('video_slot','minPresentTime','beginPresentTimeId','presentDurationId','type','target0','fill0','target1','fill1','target2','fill2','target3','fill3',),
deprecated=_DEPRECATED,
)

glGetVideoivNV = platform.createExtensionFunction( 
'glGetVideoivNV',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,constants.GLenum,arrays.GLintArray,),
doc='glGetVideoivNV(GLuint(video_slot), GLenum(pname), GLintArray(params)) -> None',
argNames=('video_slot','pname','params',),
deprecated=_DEPRECATED,
)

glGetVideouivNV = platform.createExtensionFunction( 
'glGetVideouivNV',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,constants.GLenum,arrays.GLuintArray,),
doc='glGetVideouivNV(GLuint(video_slot), GLenum(pname), GLuintArray(params)) -> None',
argNames=('video_slot','pname','params',),
deprecated=_DEPRECATED,
)

glGetVideoi64vNV = platform.createExtensionFunction( 
'glGetVideoi64vNV',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,constants.GLenum,arrays.GLint64Array,),
doc='glGetVideoi64vNV(GLuint(video_slot), GLenum(pname), GLint64Array(params)) -> None',
argNames=('video_slot','pname','params',),
deprecated=_DEPRECATED,
)

glGetVideoui64vNV = platform.createExtensionFunction( 
'glGetVideoui64vNV',dll=platform.GL,
extension=EXTENSION_NAME,
resultType=None, 
argTypes=(constants.GLuint,constants.GLenum,arrays.GLuint64Array,),
doc='glGetVideoui64vNV(GLuint(video_slot), GLenum(pname), GLuint64Array(params)) -> None',
argNames=('video_slot','pname','params',),
deprecated=_DEPRECATED,
)


def glInitPresentVideoNV():
    '''Return boolean indicating whether this extension is available'''
    return extensions.hasGLExtension( EXTENSION_NAME )
