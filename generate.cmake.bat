@echo off

cd c:/Devel/Workspace/GabeNTrader

rem gcc 13 from qt
set PATH=%PATH%;c:/Devel/Tools/Qt/Tools/Ninja;c:/Devel/Tools/Qt/Tools/CMake_64/bin;c:/Devel/Tools/Qt/Tools/mingw1310_64/bin

rem clang 17 from qt
rem set CMAKE_CXX_COMPILER_CLANG_SCAN_DEPS=c:/Devel/Tools/clang18.1.8/bin/clang-scan-deps.exe
rem set PATH=%PATH%;c:/Devel/Tools/Qt/Tools/Ninja;c:/Devel/Tools/Qt/Tools/CMake_64/bin;c:/Devel/Tools/Qt/Tools/llvm-mingw1706_64/bin

rem gcc 14 from xpack
rem set PATH=%PATH%;c:/Devel/Tools/Qt/Tools/Ninja;c:/Devel/Tools/Qt/Tools/CMake_64/bin;c:/Devel/Tools/xpack-mingw-w64-gcc-14.2.0-1/bin

rem gcc 13 from msys2
rem set PATH=%PATH%;c:/Devel/Tools/Qt/Tools/Ninja;c:/Devel/Tools/Qt/Tools/CMake_64/bin;c:/Devel/Tools/Msys2/mingw64/bin

cmake . -G Ninja --fresh
rem -DCMAKE_CXX_COMPILER_CLANG_SCAN_DEPS=c:\\Devel\\Tools\\clang18.1.8\\bin\\clang-scan-deps.exe
