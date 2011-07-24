#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# By Leonard Techel, 2011
# It works a bit like http://www.paste42.de/1449/ from Andreas Deutschmann, but its written completely from the ground (excepting some functions I made before for the other script)
# Depends on:
# • Python < 3
# • pymad
# • espeak
# •	moc
# Works only with MP3-Files, no OGG Vorbis support yet
# You _have to_ (re)name your mp3 files in this style: [artist]-[title].mp3. Replace spaces with _ and delete all special chars (like ' or äöü).

import os, mad, random
from subprocess import Popen

# SETTINGS
Music_Dir = "/home/leonard/Musik"
Playlist_Length = 60
TTS_Dir = "/tmp/moderation"
TTS_Voice = "mb-us1"
TTS_Speed = 130
TTS_Phrases = [
		'The next song is "%title%" by "%artist%".',
		'And now "%title%" by "%artist%".',
		'My next song is by "%artist%" and is called "%title%".',
		'Now you are listening to "%title%" of "%artist%".',
		'Its time to play "%title%" by "%artist%".'
]

# DO NOT CHANGE
random_files = [ ]
Last_TTS_Phrase = -1
Current_Length = 0

# function to make a recursiv file listing of a directory, returns a list with pathes
def makeTree(DIR):
	out = [ ]
	# make the new tree
	for f, d, fs in os.walk(DIR):
		for i in fs:
			fpath = "{0}/{1}".format(f, i)
			out.append(fpath)
	return out

# function to get a random file from a list, returns an item of the given list and the number of the item in the list
def getRandomFromList(LIST):
	l_length = len(LIST)
	r = random.randrange(0, l_length)
	return r, LIST[r]
	
# function to get the length of a title in minutes, returns the length in minutes
def getTitleLength(FILE):
	tf = mad.MadFile(FILE)
	msTime = tf.total_time()
	sTime = msTime / 1000
	mTime = sTime / 60
	return mTime
	
# function to execute something at the command line, returns the exit code
def toSystem(COMMAND):
	p = Popen(COMMAND, shell=True)
	sts = os.waitpid(p.pid, 0)[1]
	return sts
	
# function to get the title and artist from the id3 tags of a mp3 file, returns a list with the title and artist
def getTags(PATH):
	# get the tags from the path
	s_path = os.path.split(PATH)
	s_path = s_path[1]
	ss_path = s_path.split("-")
	title = ss_path[1].replace(".mp3", "")
	artist = ss_path[0]
			
	return title, artist
	
# function to make a tts based moderation, returns the path to a mp3-file
def makeModeration(title, artist, Last_TTS_Phrase):
	# get a random phrase from the list
	phrase = getRandomFromList(TTS_Phrases)
	while Last_TTS_Phrase == phrase[0]:
		phrase = getRandomFromList(TTS_Phrases)
	Last_TTS_Phrase = phrase[0]
	phrase = phrase[1]
	# replace the placeholder
	phrase = phrase.replace("%title%", title)
	phrase = phrase.replace("%artist%", artist)
	# make the path
	wav_path = "{0}/{1}_-_{2}.wav".format(TTS_Dir, title, artist).replace("'", "\'")
	wav_path = wav_path.replace(" ", "_")
	# make the wav voice file
	command = "espeak -v {0} -s {1} -w '{2}' '{3}'".format(TTS_Voice, TTS_Speed, wav_path, phrase)
	toSystem(command)
	# return the wav path
	return wav_path
	
if __name__ == "__main__":
	# clear the moderation directory
	toSystem("rm {0}/*".format(TTS_Dir))
	
	# clear mocp
	toSystem("mocp -c")
	
	# get the random file list
	files = makeTree(Music_Dir)
	
	# make the playlist
	while Current_Length < Playlist_Length:
		# get a random file
		out = getRandomFromList(files)[1]
		# look for the file in the playlist list
		if out not in random_files:
			# get the length of the new title
			out_length = getTitleLength(out)
			new_length = Current_Length + out_length
			# check the length
			if new_length < Playlist_Length:
				# make the moderation
				m_tags = getTags(out)
				mm_path = makeModeration(m_tags[0], m_tags[1], Last_TTS_Phrase)
				# add the moderation to the random_files list
				random_files.append(mm_path)
				# add the file to the random_files list
				random_files.append(out)
				# make the new Current_Length
				Current_Length = new_length
			else:
				break
			
	# put the playlist into mocp
	for i in random_files:
		toSystem("mocp -a '{0}'".format(i))
