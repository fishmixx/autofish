#!/usr/bin/env python
# -*- coding: utf-8 -*-

# By Leonard Techel, 2011
# It checks the current title of mocp every X seconds, if it has changed it'll update ices2.

import time, os
from subprocess import Popen

# CONFIG
check = 60
title_file = "/tmp/ices-metadata"
pid_file = "/tmp/ices2.pid"

# function to execute something at the command line, returns the exit code
def toSystem(COMMAND):
	p = Popen(COMMAND, shell=True)
	sts = os.waitpid(p.pid, 0)[1]
	return sts

if __name__ == "__main__":
	# get the pid of ices
	f = open(pid_file, "r")
	pid = f.read()
	f.close()
	
	# start an endless loop
	while True:
		# put the data into the metadata file
		act_title = toSystem('mocp -Q "artist=%artist\ntitle=%song" > {0}'.format(title_file))
		
		# let ices reload the metadata
		toSystem("kill -usr1 {0}".format(pid))
		
		# sleep the given time
		time.sleep(check)
		
	
