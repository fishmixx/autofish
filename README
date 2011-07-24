How-To autofish:
----------------

1) Install all dependencies:
	Debian:
		•	python-pymad
		•	espeak
		•	mbrola
		•	mbrola-us1
		•	moc
		•	jackd1	(_NOT_ jackd//jackd2)
		•	ices2
		•	libasound2-plugins
	Archlinux:
		From the repositories:
			•	pymad
			•	espeak
			•	moc
			•	jack	(_NOT_ jack2)
			•	alsa-utils
		From the AUR:
			•	mbrola
			•	mbrola-voices-us1
			•	ices2
			
2)	Configure your alsa for a virtual sound interface to jack:
		-->	Put the content of the asoundrc.txt in your ~/.asoundrc
			
3)	Start jackd with a dummy sound interface:
		$ jackd -r -ddummy -r44100 -p1024
		
4)	Configure and start ices2 :
		1)	Open the ices2.xml with your editor of choice and change the
			values as you need it, the file is documented at
			http://icecast.org/docs/ices-2.0.0/
		2)	Create the metadata file, default is /tmp/ices-metadata
				$ touch /tmp/ices-metadata
		3)	Start ices2
				$ ices2 ices2.xml

5)	Start mocp as server:
		$ mocp -S
		
6)	Configure and start the autofish start.py script:
		1)	Open the start.py file with your editor of choice
		2)	Change the values under the comment "# SETTINGS" as you need 
			it
		3)	Create the moderation directory, default is /tmp/moderation
				$ mkdir /tmp/moderation
		4)	Start the script
				$ python(2) start.py
		
7) Start the mocp playlist
		$ mocp -p
		
8) Start the metadata watcher
		$ python(2) titel.py
