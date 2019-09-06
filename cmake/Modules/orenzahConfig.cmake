INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_ORENZAH orenzah)

FIND_PATH(
    ORENZAH_INCLUDE_DIRS
    NAMES orenzah/api.h
    HINTS $ENV{ORENZAH_DIR}/include
        ${PC_ORENZAH_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    ORENZAH_LIBRARIES
    NAMES gnuradio-orenzah
    HINTS $ENV{ORENZAH_DIR}/lib
        ${PC_ORENZAH_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ORENZAH DEFAULT_MSG ORENZAH_LIBRARIES ORENZAH_INCLUDE_DIRS)
MARK_AS_ADVANCED(ORENZAH_LIBRARIES ORENZAH_INCLUDE_DIRS)

