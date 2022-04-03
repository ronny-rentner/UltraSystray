#!/bin/bash

# Script that uses imagemagick's `convert` to convert a single input image to an ICO with various sizes

IN=$1
OUT="${IN%.*}.ico"

if [ -z $1 ]; then
	echo "Error, provide input file path"
	exit 1
fi

if [ ! -f $1 ]; then
	echo "Error, input file '$IN' does not exist"
	exit 1
fi

convert -background none -density 1200 -scale 1024 "$IN" -define icon:auto-resize=256,96,64,48,32,24,16 "$OUT"

