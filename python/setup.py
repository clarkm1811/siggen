#!/usr/bin/env python

import os

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension


if __name__ == "__main__":
    import sys


    import numpy
    from Cython.Build import cythonize
    from MakeGeometrySource import make_source

    geometry_list = ["PPC", "ICPC", "GEM"]
    #make all the necessary .pxi files
    make_source(geometry_list)

    # The root of the siggen repo.
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Set up the C++-extension.
    libraries = []
    if os.name == "posix":
        libraries.append("m")
    include_dirs = [
        "siggen",
        os.path.join(basedir, "code"),
        numpy.get_include(),
    ]

    src = [os.path.join(basedir, "code", fn) for fn in [
        "cyl_point.cpp",
        "point.cpp",
        "GEM.cpp",
        "ICPC.cpp",
        "PPC.cpp",
        "Setup.cpp",
        "Utils.cpp",
        "VelocityLookup.cpp",
        "VelocityModel.cpp"
    ]]
    src += [
        os.path.join("siggen", "_siggen.pyx"),
    ]

    ext = Extension(
        "siggen._siggen",
        sources=src,
        language="c++",
        libraries=libraries,
        include_dirs=include_dirs,
        extra_compile_args=["-std=c++11",
                            "-Wno-unused-function",
                            "-Wno-uninitialized",
                            "-DNO_THREADS"],
        extra_link_args=["-std=c++11"],
    )
    extensions = cythonize([ext])

    # Hackishly inject a constant into builtins to enable importing of the
    # package before the library is built.
    if sys.version_info[0] < 3:
        import __builtin__ as builtins
    else:
        import builtins
    builtins.__SIGGEN_SETUP__ = True
    import siggen

    setup(
        name="siggen",
        version=siggen.__version__,
        author="Ben Shanks",
        author_email="benjamin.shanks@gmail.com",
        packages=["siggen"],
        install_requires=[
          'numpy',
          'scipy',
          'cython'
        ],
        ext_modules=extensions,
    )