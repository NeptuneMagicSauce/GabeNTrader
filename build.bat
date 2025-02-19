@echo off

cd c:/Devel/Workspace/GabeNTrader

set PATH=%PATH%;c:\Devel\Tools\Qt\Tools\Ninja;c:\Devel\Tools\Qt\Tools\CMake_64\bin;c:\Devel\Tools\Qt\Tools\mingw1310_64\bin

cmake --build .
