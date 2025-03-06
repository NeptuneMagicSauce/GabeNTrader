cmake_minimum_required(VERSION 3.28) # min 3.28 for cpp modules

project(Trader)

set(sources src/main.cpp src/gui.cpp)
set(sources_modules src/foo.cxx)
# FILE(GLOB_RECURSE sources CONFIGURE_DEPENDS src/*.cpp)
# FILE(GLOB_RECURSE sources_modules CONFIGURE_DEPENDS src/*.cxx)
# FILE(GLOB_RECURSE resources CONFIGURE_DEPENDS data/*.qrc)

message(">>> sources ${sources}")
message(">>> modules ${sources_modules}")
message(">>> resources ${resources}")

set(CMAKE_CXX_STANDARD 23)
# set(CMAKE_CXX_SCAN_FOR_MODULES 0) # needed for qt-clang-17 which does not have clang-scan-deps

set(PATHROOT "c:") # cmake from qt
# set(PATHROOT "/c") # cmake from mingw
set(QT6_PATH "${PATHROOT}/Devel/Tools/Qt/6.8.2")
set(QT6_MINGW "${QT6_PATH}/mingw_64")
set(CMAKE_PREFIX_PATH "${QT6_MINGW}")
set(QT6_LLVM  "${QT6_PATH}/llvm-mingw_64")
# set(CMAKE_PREFIX_PATH "${QT6_LLVM}") # not needed, QT6_MINGW works for clang

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(default_build_type "Debug")
  message(STATUS "Setting build type to '${default_build_type}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${default_build_type}" CACHE
      STRING "Choose the type of build." FORCE)
  # build type possible values:
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS
    "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
endif()

set(CMAKE_AUTOMOC ON) # must be before add_executable() # fails with clang19 (and modules?)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

if(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX)
  add_compile_options(-Wall -Wextra) # must be before add_executable()
endif()

add_executable(${PROJECT_NAME} ${sources} ${resources})

set(LIB_NAME "cppmodules")
add_library(${LIB_NAME})
target_sources(${LIB_NAME} PUBLIC FILE_SET CXX_MODULES FILES ${sources_modules})
target_link_libraries(${PROJECT_NAME} ${LIB_NAME})

if(CMAKE_BUILD_TYPE STREQUAL "Release")
  set(CMAKE_EXE_LINKER_FLAGS "-mwindows")
else()
  set(CMAKE_EXE_LINKER_FLAGS "-mconsole")
endif()

# set(CMAKE_INSTALL_PREFIX ${PROJECT_BINARY_DIR}/install)
# install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX})

set(QTLIBLIST Core Widgets Gui) # Gui Network Test WebSockets OpenGL ...
find_package(Qt6 REQUIRED ${QTLIBLIST})
foreach(qtlib ${QTLIBLIST})
  target_link_libraries(${PROJECT_NAME} Qt6::${qtlib})
endforeach()

# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_BINARY_DIR}/${BINARY_OUTPUT_DIR})

set(CMAKE_CXX_STANDARD_LIBRARIES "-limagehlp") # SymInitialize()
set (dllpath "")
# these 3 dlls are needed for both gcc and clang
foreach(dll stdc++-6 gcc_s_seh-1 winpthread-1)
  set(dllpath ${dllpath} ${QT6_MINGW}/bin/lib${dll}.dll)
endforeach()
# these 2 dlls are needed for clang only
foreach(dll unwind c++)
  set(dllpath ${dllpath} ${QT6_LLVM}/bin/lib${dll}.dll)
endforeach()
foreach(qtlib ${QTLIBLIST})
  set(dllpath ${dllpath} ${QT6_MINGW}/bin/Qt6${qtlib}.dll)
endforeach()
file(COPY ${dllpath} DESTINATION ${CMAKE_BINARY_DIR})
install(FILES ${dllpath} DESTINATION ${CMAKE_INSTALL_PREFIX})

set(QTPLUGINDIR plugins/platforms)
set(QTPLUGIN ${QT6_MINGW}/${QTPLUGINDIR}/qwindows.dll)
file(COPY ${QTPLUGIN} DESTINATION ${CMAKE_BINARY_DIR}/${QTPLUGINDIR})
install(FILES ${QTPLUGIN} DESTINATION ${CMAKE_INSTALL_PREFIX}/${QTPLUGINDIR})
