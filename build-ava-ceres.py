import sys
sys.dont_write_bytecode = True

from mingw_scripts.default_args import process_default_args
import mingw_scripts.qt6_base
import mingw_scripts.qt6_shadertools
import mingw_scripts.qt6_declarative
import mingw_scripts.qt6_activeqt
import mingw_scripts.qt6_svg
import mingw_scripts.qt6_jkqtplotter
import mingw_scripts.hdf5
import mingw_scripts.wine
import mingw_scripts.zlib
import mingw_scripts.ceres_solver
import mingw_scripts.google_glog
import mingw_scripts.gflags
import mingw_scripts.eigen
import mingw_scripts.cmake_toolchain


process_default_args()
mingw_scripts.cmake_toolchain.build()
mingw_scripts.eigen.build()
mingw_scripts.gflags.build()
mingw_scripts.google_glog.build()
mingw_scripts.ceres_solver.build_with_glog()
mingw_scripts.zlib.build()
mingw_scripts.wine.build()
mingw_scripts.hdf5.build()
mingw_scripts.qt6_base.build()
#mingw_scripts.qt6_shadertools.build()
#mingw_scripts.qt6_declarative.build()
#mingw_scripts.qt6_activeqt.build()
mingw_scripts.qt6_svg.build()
mingw_scripts.qt6_jkqtplotter.build()
