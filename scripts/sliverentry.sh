#!/bin/bash

if [ ! -d /home/sliver/.sliver-client/configs ]
then
	mkdir -p /home/sliver/.sliver-client/configs
	/opt/sliver-server operator --name sliver --lhost localhost --save /home/sliver/.sliver-client/configs
fi

/opt/sliver-server
