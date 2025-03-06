@echo off

cd c:/Devel/Workspace/GabeNTrader

del CMakeCache.txt

rem CMake and Ninja
set PATH=c:/Devel/Tools/Qt/Tools/Ninja;c:/Devel/Tools/Qt/Tools/CMake_64/bin;%PATH%

rem gcc 13 from qt = ok but without cpp20-modules
rem set PATH=c:/Devel/Tools/Qt/Tools/mingw1310_64/bin;%PATH%

rem clang 17 from qt = fails to link QTimer::singleShot
rem set PATH=c:/Devel/Tools/Qt/Tools/llvm-mingw1706_64/bin;%PATH%

rem gcc 14 from mingw = fails to automoc, also fails on cpp20-modules
rem set PATH=c:/Devel/Tools/Msys2/mingw64/bin;%PATH%
rem cmake . -G Ninja --fresh -DCMAKE_C_COMPILER=c:/Devel/Tools/Msys2/mingw64/bin/gcc.exe -DCMAKE_CXX_COMPILER=c:/Devel/Tools/Msys2/mingw64/bin/g++.exe

rem cmake . -G Ninja --fresh

rem clang 19 from mingw
cmake . -G Ninja --fresh -DCMAKE_C_COMPILER=c:/Devel/Tools/Msys2/mingw64/bin/clang.exe -DCMAKE_CXX_COMPILER=c:/Devel/Tools/Msys2/mingw64/bin/clang++.exe
