from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

from functools import reduce

import os


os.makedirs('dist', exist_ok=True)
FTA = ['setup.py', 'auxil.py', '__init__.py']

def file_code(fldr, fn):
    fldr = os.path.join('dist', fldr)
    if fldr == '.':
        return fn[:-3]
    else:
        return fldr.replace('\\', '.') + '.' + fn[:-3]
        
def get_pys(fldr):
    return tuple((file_code(fldr, fn), fldr, fn) for fn in 
                 filter(lambda fn: fn.endswith('.py') 
                        and not (fn in FTA), 
                        os.listdir(fldr)))

lofdn = reduce(lambda a, b: a + b, (get_pys(fldr) for fldr in ['.', 'src', 
                                     'src\\commands', 
                                     'src\\models',
                                     'src\\classes',
                                     'src\\pysqlsimplecipher',
                                     'src\\services']))

ext_modules = [
    Extension(fc, 
              [os.path.join(fldr, fn)]) for fc, fldr, fn in lofdn
]

setup(
    name = 'main',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
