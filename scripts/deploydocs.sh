#!/usr/bin/bash

BRANCH=$1
SOURCE=$2
DEST=$3

function get_version ()
{
	VERSION=$(grep 'release = ' docs/source/conf.py | awk -F "'" '{print $2}')
}

case $BRANCH in
	version)
		get_version
		echo $VERSION
		;;
	development)
		test -d $DEST/development && rm -rf $DEST/development
		cp -r $SOURCE $DEST/development
		;;
	main)
		get_version
		if [ $(echo $VERSION | grep -P "\d+\.\d+\.\d+") ]
		then
		    test -d $DEST/$VERSION && rm -rf $DEST/$VERSION
		    cp -r $SOURCE $DEST/$VERSION
		    test -e $DEST/current && unlink $DEST/current
		    ln -s $DEST/$VERSION $DEST/current
		else
			echo "Unable to identify the aminer-version!"
			exit 1
		fi
		;;
	*)
		echo "usage: $0 main|development"
		exit 1
		;;
esac

exit 0
