@echo off

cd c:/Devel/Workspace/GabeNTrader

set PATH=c:/Devel/Tools/Qt/Tools/CMake_64/bin;%PATH%

rem this is needed for automoc generation from cmake
rem otherwise it fails 'AutoMoc subprocess error'
set PATH=c:/Devel/Tools/Qt/Tools/mingw1310_64/bin/;%PATH%

cmake --build .
