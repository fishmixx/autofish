#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# A little script that is making auto-generated ogg playlists based on 
# files from a directory tree
#
# Copyright (C) 2011 Leonard Techel

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Based on https://github.com/telelo/autofish/blob/master/start.py which 
# is a bit like a version of Andreas Deutschmann, but its written
# completely from the ground, excepting some functions I've made before
# for the script of Andreas.

# The script depends on:
# • Python < 3
# • Mutagen
# • ffmpeg

import os, random, mutagen
from subprocess import Popen

# SETTINGS
Music_Dir			= "/home/leonard/NEW/Musik/sorted"	# dictionary with your music
Music_Out_Dir		= "/tmp/eisout/"					# the slash at the end is *very* important!
Music_Dir_Badword	= "NONFREE"							# if this word is in the path, the script won't add the file
Music_Out_Bitrate	= "128K"							# the bitrate of the converted ogg files
Playlist_Length		= 60								# in minutes

# DO NOT CHANGE
Music_Out			= [ ]								# the script stores the pathes there
Music_Out_Ogg		= [ ]								# the script stores the ogg pathes there
Music_Out_Length	= 0									# initialise a variable with the playlist length

# PROGRAM

# function to make a recursiv file listing of a directory, returns a list with pathes
def makeTree(DIR):
	out = [ ]
	# make the new tree
	for f, d, fs in os.walk(DIR):
		for i in fs:
			fpath = "{0}/{1}".format(f, i)
			# check for bad words in the path
			if Music_Dir_Badword not in fpath:
				out.append(fpath)
	return out
	
# function to get a random file from a list, returns an item of the given list and the number of the item in the list
def getRandomFromList(LIST):
	l_length = len(LIST)
	r = random.randrange(0, l_length)
	return r, LIST[r]
	
# function to get the length of an audio file in seconds
def getTitleLength(filepath):
	try:
		# get the informations of the audio file
		info = mutagen.File(filepath)
		# extract the first line
		info = info.pprint().split("\n")[0]
		# split it at the commas
		info = info.split(", ")
		# look for a split with the keyword "seconds"
		for thing in info:
			if "seconds" in thing:
				info = thing
				break
		# split it at the space to get only the seconds
		info = info.split(" ")[0]
		
		# return the length
		return info
	except:
		return False

# function to make minutes from seconds
def minutesFromSeconds(seconds):
	return int(seconds / 60)
	
# function to execute something at the command line, returns the exit code
def toSystem(COMMAND):
	p = Popen(COMMAND, shell=True)
	sts = os.waitpid(p.pid, 0)[1]
	return sts
	
# START EVERYTHING
if __name__ == "__main__":
	# get the file list
	files = makeTree(Music_Dir)
	
	# get a random file from the file list, look for its length and if its not already chosen and make the length higher
	while Music_Out_Length < Playlist_Length:
		# get a random file
		f = getRandomFromList(files)[1]
		# look if the file is not already on the playlist
		if f not in Music_Out:
			# get the length of the file
			length = getTitleLength(f)
			# check that the length thing was successfull
			if length is not False:
				# make the full playlist length higher
				Music_Out_Length = int(Music_Out_Length) + minutesFromSeconds(float(length))
				# append the file to the playlist
				Music_Out.append(f)
				
	# convert all files to ogg
	for f in Music_Out:
		# make the out path
		outpath = f.split("/")
		outpath = outpath[len(outpath)-1]
		outpath = Music_Out_Dir + outpath + ".ogg"
		# convert the 
		toSystem("ffmpeg -i '{0}' -ab {1} -acodec libvorbis '{2}'".format(f, Music_Out_Bitrate, outpath))
		# append the new path to a dictionary
		Music_Out_Ogg.append(outpath)
	
	# print out the whole playlist
	for f in Music_Out_Ogg:
		print f
