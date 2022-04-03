#!/bin/bash

# Use REAL=1 to actually run the extraction

DIR=$1

if [ -z $1 ]; then
	echo "Error, provide directory parameter"
	exit 1
fi

for f in $(find "$DIR" -type f -name \*.svg); do
	SOURCE_DIR=`dirname $f`
	TARGET_DIR=`realpath "${SOURCE_DIR}/../.."`

	echo file $f
	#echo source $SOURCE_DIR
	#echo target $TARGET_DIR

	# The variant or type like 'round', 'outlined', 'twotone', etc.
	ICON_TYPE=$(basename $SOURCE_DIR)
	# Strip the 'materialicons' prefix from the type
	ICON_TYPE=${ICON_TYPE#materialicons}
	# Add a hyphen prefix if the type is not emtpy
	if [ ! -z $ICON_TYPE ]; then
		ICON_TYPE="-${ICON_TYPE}"
	fi

	ICON_SIZE=$(basename $f)
	ICON_NAME=$(basename `realpath ${SOURCE_DIR}/..`)
	ICON_FILE="${ICON_NAME}${ICON_TYPE}-${ICON_SIZE}"

	if [ ${REAL:-0} -ne 0 ]; then
		mv $f ${TARGET_DIR}/${ICON_FILE}
		rmdir ${SOURCE_DIR} 2>/dev/null
		rmdir ${TAGET_DIR}/${ICON_NAME} 2>/dev/null

		find $DIR -empty -delete
	else
		echo "mv '$f' '${TARGET_DIR}/${ICON_FILE}'"
		echo "rmdir '${SOURCE_DIR}' 2>/dev/null"
		echo "rmdir '${TAGET_DIR}/${ICON_NAME}' 2>/dev/null"
	fi

done

