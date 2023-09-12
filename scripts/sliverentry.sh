#!/bin/bash

SLIVERHOME="/root"

if [ ! -d $SLIVERHOME/.sliver-client/configs ]
then
	mkdir -p $SLIVERHOME/.sliver-client/configs
	/opt/sliver-server operator --name sliver --lhost localhost --save $SLIVERHOME/.sliver-client/configs
fi

/opt/sliver-server
