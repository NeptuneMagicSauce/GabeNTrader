#!/bin/bash


mydir=$(realpath $(dirname $0))
mydir=$(echo $mydir | sed 's+/c+c:+')
CMD="cmd.exe"
if [[ "$(uname)" == MINGW* ]] ; then
    CMD+=" //c"
else
    CMD+=" /c"
fi
batch=$(basename $0)
batch=$(echo $batch | sed 's/sh$/bat/')
$CMD $mydir/$batch
