#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# By Leonard Techel, 2011
# It works a bit like http://www.paste42.de/1449/ from Andreas Deutschmann, but its written completely from the ground (excepting some functions I made before for the other script)
# Depends on:
# •	Python < 3
# •	mplayer
# •	pymplayer (http://code.google.com/p/python-mplayer)
# • espeak
# You _have to_ (re)name your mp3 files in this style: [artist]-[title].mp3. Replace spaces with _ and delete all chars who are not [a-zA-Z0-9].

import os, random, mplayer, time
from subprocess import Popen

# SETTINGS
Music_Dir = "/home/leonard/Music/Playlist2"

Ices_Title_File = "/tmp/ices-metadata"
Ices_PID_File = "/tmp/ices2.pid"

Playlist_Length = 60
Playlist_File = "/tmp/playlist"

TTS_Dir = "/tmp/moderation"
TTS_Voice = "en"
TTS_Speed = 130
TTS_Phrases = [
		'The next song is "%title%" by "%artist%".',
		'And now "%title%" by "%artist%".',
		'My next song is by "%artist%" and is called "%title%".',
		'Now you are listening to "%title%" of "%artist%".',
		'Its time to play "%title%" by "%artist%".'
]

Jingles = [
		'You are listening to fishmixx - mixxing the waves!',
		'I am the crazy underwater machine and you are listening to my broadcast. Look at fishmixx.de for broadcasts who are moderated by some crazy humans who made me.',
		'This is fishmixx, your creative commons webradio. Just visit fishmixx.de if you like it.'
]
Jingle_Rythm = 3

# DO NOT CHANGE
random_files = [ ]
Last_TTS_Phrase = -1
Last_Jingle_Phrase = -1
Current_Length = 0
Playlist_Count = 0
Jingle_Count = 0

# PROGRAM

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
	lplayer = mplayer.Player(args="-ao null")
	lplayer.loadfile(FILE)
	length = int(lplayer.length)
	lplayer.quit()
	return length
	
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
	# split file ending and title name
	title = ss_path[1].split(".")
	title = title[0].replace("_", " ")
	# the artist
	artist = ss_path[0].replace("_", " ")
			
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
	wav_path = "{0}/M_{1}_-_{2}.wav".format(TTS_Dir, title, artist).replace("'", "\'")
	wav_path = wav_path.replace(" ", "_")
	# make the wav voice file
	command = "espeak -v {0} -s {1} -w '{2}' '{3}'".format(TTS_Voice, TTS_Speed, wav_path, phrase)
	toSystem(command)
	# return the wav path
	return wav_path
	
# function to start the streaming mplayer instance, feed it with the playlist and change the title after each track
def startPlayer(Playlist_Count):
	# make a new mplayer instance
	player = mplayer.Player(args="-ao 'jack:port=alsa-jack.jackC.{0}.0:name=autofish'".format(Ices_PID))
	
	# load the playlist
	player.loadlist(Playlist_File)
	
	# start the track waiter for the icecast title info
	a = 0
	while a < Playlist_Count:
		# check for metadata, moderation WAV files have no tags
		print player.filename
		if player.filename[0:2] != "M_":
			# make the title info
			title, artist = getTags(player.filepath)
			print "Now playing: {0} - {1}".format(artist, title)
			metadata = "artist={0}\ntitle={1}\n".format(artist, title)
			# set the title info
			tinfo = open(Ices_Title_File, "w")
			tinfo.write(metadata)
			tinfo.close()
			# send a signal to the ices process
			toSystem("kill -usr1 {0}".format(Ices_PID))
		# get the remaining title length
		remaining = player.length - player.time_pos + 2
		# wait for the end
		time.sleep(int(remaining))
		# count a one up
		a += 1
		
	# stop the mplayer instance
	player.quit()
	print "job done."
	
if __name__ == "__main__":
	# clear the moderation directory
	for item in os.listdir(TTS_Dir):
		os.unlink(os.path.join(TTS_Dir, item))
		
	# open the playlist file
	pl = open(Playlist_File, "w")
	
	# get the random file list
	files = makeTree(Music_Dir)
	
	# get ices pid number
	pidf = open(Ices_PID_File, "r")
	Ices_PID = pidf.read()
	pidf.close()
	
	# make seconds of the paylist length
	Playlist_Length = Playlist_Length * 60
	
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
				
				# look if its time to play a jingle
				if Jingle_Count == Jingle_Rythm:
					# get a random jingle
					jingle = getRandomFromList(Jingles)
					while jingle[0] == Last_Jingle_Phrase:
						jingle = getRandomFromList(Jingles)
					# make the jingle
					wav_path = "{0}/M_J_{1}.wav".format(TTS_Dir, Playlist_Count)
					command = "espeak -v {0} -s {1} -w '{2}' '{3}'".format(TTS_Voice, TTS_Speed, wav_path, jingle[1])
					toSystem(command)
					# put the jingle into the playlist
					random_files.append(wav_path)
					# make the new Last_Jingle_Phrase
					Last_Jingle_Phrase = jingle[0]
					
				# make the moderation
				m_tags = getTags(out)
				mm_path = makeModeration(m_tags[0], m_tags[1], Last_TTS_Phrase)
				# add the moderation to the random_files list
				random_files.append(mm_path)
				# add the file to the random_files list
				random_files.append(out)
				# make the new Current_Length
				Current_Length = new_length
				# count the Playlist_Count up
				Playlist_Count += 1
				# count up the jingle insert counter
				if Jingle_Count < Jingle_Rythm:
					Jingle_Count += 1
				else:
					Jingle_Count = 0					
			else:
				break
			
	# put the tracks and there moderation into the playlist file
	for item in random_files:
		pl.write("{0}\n".format(item))
		
	# close the playlist file
	pl.close()
	
	# start the streaming mplayer instance
	startPlayer(Playlist_Count)
