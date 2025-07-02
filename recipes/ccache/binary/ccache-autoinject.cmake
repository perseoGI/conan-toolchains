include_guard()

# Find ccache executable
find_program(CCACHE_PROGRAM NAMES ccache)

if(CCACHE_PROGRAM)
    message(STATUS "ccache found: ${CCACHE_PROGRAM}, enabling via CMake launcher and environment.")
    # Method 1: Set CMake launcher variables
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM} CACHE FILEPATH "CXX compiler cache used" FORCE)
    set(CMAKE_C_COMPILER_LAUNCHER ${CCACHE_PROGRAM} CACHE FILEPATH "C compiler cache used" FORCE)
else()
    message(WARNING "ccache not found. Not enabling ccache integration.")
endif()
