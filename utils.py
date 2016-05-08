#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import os
import time

#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
xbmc.log('utils.py in %s' % ADDON.getAddonInfo('name'))
referral = ADDON.getSetting('my_referral_link')
IMAGE = os.path.join(ADDON.getAddonInfo('path'), 'icon' + referral + '.jpg')

def TVguide():
	TVguideNr= int(ADDON.getSetting('tvguidenr'))
	# 0= wozboxtvguide|1= tvguide|2= ftvguide|3= ivueguide|4= custom (if empty search all known)|5= no tv guide search
	#log('TVguideNr',repr(TVguideNr))
	if TVguideNr == 0:
		TVguide= [['script.wozboxtvguide','source.db']]
	elif TVguideNr == 1:
		TVguide= [['script.tvguide','source.db']]
	elif TVguideNr == 2:
		TVguide= [['script.ftvguide','source.db']]
	elif TVguideNr == 3:
		TVguide= [['script.ivueguide','master.db']]
	elif TVguideNr == 4:
		#TVguide= [ ['script.tvguide','source.db']]
		ExtraGuide= ''
		ExtraGuideDB= ''
		ExtraGuidePathDB= ADDON.getSetting('tvguidenotificationsDB')
		ExtraGuideList= ExtraGuidePathDB.split(os.sep)
		ExtraGuide= ExtraGuideList[-2]
		ExtraGuideDB= ExtraGuideList[-1]
		if ExtraGuide != '' and ExtraGuideDB != '':
			TVguide= [[ExtraGuide,ExtraGuideDB]]
		else:
			# If Extra TV Guide not complete - try all
			TVguide= [['script.wozboxtvguide','source.db'], ['script.tvguide','source.db'],['script.ftvguide','source.db'],['script.ivueguide','master.db']]
	else:
		# No search in TV Guide
		TVguide= []
	#log('findtvguidenotifications TVguide',repr(TVguide))
	if len(TVguide) != 0:
		ADDON.setSetting('activetvguide',repr(TVguide[0][0]))
	else:
		ADDON.setSetting('activetvguide','none')
	return TVguide
	
def ChannelNameLookuponWeb(cat):
	#print 'default.py ChannelName(cat)= %s' % str(cat)
	net.set_cookies(cookie_jar)
	imageUrl=definition.getBASEURL() + '/res/content/tv/'
	now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
	url='&mwAction=category&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%('-2',now)
	#print 'default.py XXXX site+url= %s%s'  % (site,url)
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	#print 'default.py XXXX ChannelName link= %s' % str(repr(link))
	data = json.loads(link)
	channels=data['contents']
	#print 'default.py cat= %s, CHANNELS= %s' % (cat,str(repr(channels)))
	for field in channels:
		channel      =  field['id']
		if channel == cat:
			name         =  field['name'].encode("utf-8")
			#utils.notification( 'name= %s, channel= %s' % (name,channel))
			return name
	utils.notification( 'NOT FOUND: channel= %s' % (cat))
	return 'no name'

def log(module,message):
	if ADDON.getSetting('DebugRecording')=='false' and module.upper()[:4] != 'TEST' or ADDON.getSetting('DebugRecording')=='true':
		xbmc.log(ADDON.getAddonInfo('name') + ' ' + module +': ' + message)

def logdebug(module,message):
	if ADDON.getSetting('DebugRecording')=='true':
		log(module,message)

def notification(message, time = 0):
	if (not ADDON.getSetting('RecursiveSearch')=='true' or ADDON.getSetting('NotifyOnSearch')=='true'):
		message = message.replace('"',  '')
		message = message.replace('\'', '')
		message = message.replace(',',  '')
		message = message.replace('(',  '')
		message = message.replace(')',  '')
	 
		if time == 0:
			try:
				time = int(ADDON.getSetting('NotificationTime'))
			except:
				pass
			if time == 0:
				time = 30

		header = ADDON.getAddonInfo('name') + '..........'

		cmd  = 'XBMC.Notification(%s, %s, %d, %s)' % (header, message, time*1000, IMAGE)
		print cmd  # Put in LOG
		log('notification',message)
		xbmc.executebuiltin(cmd)
	
def notificationboxadd(message):
	oldmessage= ADDON.getSetting('allmessages')
	if oldmessage == '':
		allmessages= message
	else:
		allmessages= message + '/' + oldmessage
	ADDON.setSetting('allmessages',allmessages)
	
def notificationbox(message):
	oldmessage= ADDON.getSetting('allmessages')
	if oldmessage == '':
		allmessages= message
	else:
		allmessages= message + '[CR]' + oldmessage
	ADDON.setSetting('allmessages',allmessages)
	log('notificationbox',allmessages)
	xbmcgui.Dialog().ok( ADDON.getAddonInfo('name'), allmessages)
	ADDON.setSetting('allmessages','')
		
def folderwritable(path):
	if os.access(path, os.W_OK):
		return True
	else:
		if '://' in path:
			return True
		else:
			if path=='':
				xbmcgui.Dialog().ok( ADDON.getAddonInfo('name'), '[COLOR red]utils.py folderwritable: ERROR[/COLOR]', '[Empty path]', 'The folder is not writable!')
			else:
				xbmcgui.Dialog().ok( ADDON.getAddonInfo('name'), '[COLOR red]utils.py folderwritable: ERROR[/COLOR]', path, 'The folder is not writable!')
			return False

def filterfalse(predicate, iterable):
    # filterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def uniquecolon(items):
	# print 'utils.py uniquecolon(items)= %s' % repr(items) 
	listitems=items.split(':')
	result=':'.join(unique_everseen(listitems))
	# print 'utils.py uniquecolon(items) result= %s' % repr(result) 
	return result
	
def FindPlatform():
	# Find the actual platform
	Platform = ''
	try:
		kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'kodi.log'))
		try: logfile = open(kodilog,'r')
		except:
			pass
			kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'xbmc.log'))
			try: logfile = open(kodilog,'r')
			except:
				pass
				kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'tvmc.log'))
				try: logfile = open(kodilog,'r')
				except:
					pass
					kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'spmc.log'))
					try: logfile = open(kodilog,'r')
					except:
						pass
						log('FindPlatform','Logfile not found')
		line0 = logfile.readline()
		line1 = logfile.readline()
		line2 = logfile.readline()
		line3 = logfile.readline()
		line4 = logfile.readline()
		line5 = logfile.readline()
		line6 = logfile.readline()
		line7 = logfile.readline()
		Platform = line2.split('Platform:')[1].strip()
		ADDON.setSetting('platform',Platform)
		RunningOn = line5.split('Running on ')[1].split(' ')[0].strip()
		ADDON.setSetting('runningon',RunningOn)
		log ('Platform', repr(ADDON.getSetting('platform')))   # Put in LOG
		log ('RunningOn', repr(ADDON.getSetting('runningon')))   # Put in LOG
		log ('OS', os.environ['OS'])  # Put in LOG
	except: 
		pass
		log ('FindPlatform','FAILED')   # Put in LOG
	finally:
		logfile.close()
	return Platform

def rtmpdumpFilename():
	if ADDON.getSetting('DebugRecording')=='false': #dont update Paltform if debugging recordings
		try:
			Platform = FindPlatform()
			ADDON.setSetting('osplatform','')
			if Platform == 'Windows NT x86 32-bit':
				ADDON.setSetting('os','11')
			elif Platform == 'Windows NT x86 64-bit':
				ADDON.setSetting('os','11')
			elif Platform == 'Android ARM 32-bit':
				ADDON.setSetting('os','13')
			elif Platform == 'Android x86 32-bit':
				ADDON.setSetting('os','13')
			elif Platform == 'Linux x86 64-bit':
				ADDON.setSetting('os','7')
			elif Platform == 'Linux x86 32-bit':
				ADDON.setSetting('os','6')
			else:
				log ('rtmpdumpFilename: ', 'Your platform= %s has not been set automatically!' % repr(Platform))  # Put in LOG
		except:
			pass
			log ('rtmpdumpFilename: ', 'Failed to automatically update platform!')  # Put in LOG
		ADDON.setSetting('osplatform',ADDON.getSetting('os'))
		log('rtmpdumpFilename','Running on %s' % repr( ADDON.getSetting('runningon')))
		if 'OpenELEC' in ADDON.getSetting('runningon'):
			ADDON.setSetting('os','12')
		if 'samsung' in ADDON.getSetting('runningon'):
			ADDON.setSetting('os','13')
		if 'WOZTEC' in ADDON.getSetting('runningon'):
			ADDON.setSetting('os','13')
		if 'MBX' in ADDON.getSetting('runningon'): 
			ADDON.setSetting('os','13')
		if 'Genymotion' in ADDON.getSetting('runningon'): 
			ADDON.setSetting('os','13')
		# Enable the following two lines to test running on Ubuntu!
		#if 'Ubuntu' in ADDON.getSetting('runningon'):  # ONLY TEST
		#	ADDON.setSetting('os','13')
	quality = ADDON.getSetting('os')
	log ('rtmpdumpFilename', 'quality= %s' %quality)
	#if quality == '0':
	#	return 'androidarm/rtmpdump'
	#elif quality == '1':
	#	return 'android86/rtmpdump'
	#el
	if quality == '2':
		return 'atv1linux/rtmpdump'
	elif quality == '3':
		return 'atv1stock/rtmpdump'
	elif quality == '4':
		return 'atv2/rtmpdump'
	elif quality == '5':
		return 'ios/rtmpdump'
	elif quality == '6':
		return 'linux32/rtmpdump'
	elif quality == '7':
		return 'linux64/rtmpdump'
	elif quality == '8':
		return 'osx106/rtmpdump'
	elif quality == '9':
		return 'osx107/rtmpdump'
	elif quality == '10':
		return 'pi/rtmpdump'
	elif quality == '11':
		return 'win/rtmpdump.exe'
	elif quality == '12':
		return '/usr/bin/rtmpdump'
	elif quality == '13' or quality == '0' or quality == '1':
		return  '/system/vendor/bin/rtmpdump' # HOTFIX Android - rtmpdump moved to /system/bin (using build in librtmp.so from kodi)
	else:
		log('rtmpdumpFilename: ','Your platform= %s has not been set automatically!' % repr(Platform))  # Put in LOG
		return

def libPath():
	quality = ADDON.getSetting('os')
	log ('libPath', 'quality= %s' %quality)
	#if quality == '0':
	#	return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'androidarm')
	#elif quality == '1':
	#	return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'android86')
	#el
	if quality == '2':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'atv1linux')
	elif quality == '3':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'atv1stock')
	elif quality == '4':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'atv2')
	elif quality == '5':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'ios')
	elif quality == '6':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'linux32')
	elif quality == '7':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'linux64')
	elif quality == '8':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'osx106')
	elif quality == '9':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'osx107')
	elif quality == '10':
		return os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'pi')
	elif quality == '11':
		return 'None'   
	elif quality == '12':
		return '/usr/bin/'
	elif quality == '13' or quality == '0' or quality == '1':
		LIBpath = '/data/data/org.xbmc.kodi/lib/'
		log( 'libPath: ', 'os.path.exists(%s)= %s' % (repr(LIBpath),repr(os.path.exists(LIBpath))))  # Put in LOG
		log( 'libPath: ', 'os.path.exists(%s)= %s' % (repr(LIBpath + 'librtmp.so'),repr(os.path.exists(LIBpath + 'librtmp.so'))))  # Put in LOG
		return LIBpath

	
def runCommand(cmd, LoopCount, libpath = None, module_path = './'):
	log('runCommand','cmd= %s' % repr(cmd)) # Put in LOG
	log('runCommand','LoopCount= %s' % repr(LoopCount)) # Put in LOG
	log('runCommand','libpath= %s' % repr(libpath)) # Put in LOG
	log('runCommand','module_path= %s' % repr(module_path)) # Put in LOG
	from subprocess import Popen, PIPE, STDOUT
	# get the list of already defined env settings
	env = os.environ
	log('runCommand','env= %s' % env)
	if LoopCount == 0:
		if (libpath):
			log('runCommand','libpath1= %s' %repr(libpath))
			# add the additional env setting
			envname = "LD_LIBRARY_PATH"
			if (env.has_key(envname)):
				env[envname] = env[envname] + ":" + libpath
				env[envname]=uniquecolon(env[envname])
			else:
				env[envname] = libpath
			envname = "DYLD_LIBRARY_PATH"
			if (env.has_key(envname)):
				env[envname] = uniquecolon(env[envname] + ":" + libpath)
			else:
				env[envname] = libpath
		envname = 'PYTHONPATH'
		if (env.has_key(envname)):
			env[envname] = uniquecolon(env[envname] + ":" + module_path)
		else:
			env[envname] = module_path
	try:
		log('runCommand','env[PYTHONPATH] = ' + env['PYTHONPATH'])  # Put in LOG
		log('runCommand','env[LD_LIBRARY_PATH] = ' + env['LD_LIBRARY_PATH']) # Put in LOG
		log('runCommand','env[DYLD_LIBRARY_PATH] = ' + env['DYLD_LIBRARY_PATH'])  # Put in LOG
	except:
		pass

	# subpr = Popen(cmd, shell=True, env=env, stdin=PIPE, stdout=PIPE, stderr=STDOUT) # original
	quality = ADDON.getSetting('os')
	if quality=='13' or  quality=='0' or quality=='1':
		subpr = Popen(cmd, executable='/system/bin/sh', shell=True, close_fds=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
	else:
		subpr = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT) 

	x = subpr.stdout.read()
	if ADDON.getSetting('DebugRecording')=='true':
		log('runCommand','subpr.stdout.read()= %s' % repr(x))
		if 'ERROR' in x:
			xError=x.replace('\n','[cr]')
			notification('[COLOR red]ERROR utils.py runCommand: Basic recording function failed![/COLOR]')
			xbmcgui.Dialog().ok( ADDON.getAddonInfo('name'), 'utils.py runCommand: ERROR', '', repr(xError))
	time.sleep(2)
	while subpr.poll() == None:
		time.sleep(2)
		x = subpr.stdout.read()
		if ADDON.getSetting('DebugRecording')=='true':
			if 'ERROR' in x:
				xError=x.replace('\n','[cr]')
				notification('[COLOR red]ERROR utils.py runCommand: Basic recording function failed![/COLOR]')
				xbmcgui.Dialog().ok( ADDON.getAddonInfo('name'), 'utils.py runCommand: ERROR in Loop', '', repr(xError))

def datetimeconversions():
	# Test date time conversions on this system
	#-------------------------------------------------
	# conversions to strings
	#-------------------------------------------------
	# datetime object to string
	dt_obj = datetime.datetime(2008, 11, 10, 17, 53, 59)
	date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
	print date_str

	# time tuple to string
	time_tuple = (2008, 11, 12, 13, 51, 18, 2, 317, 0)
	date_str = time.strftime("%Y-%m-%d %H:%M:%S", time_tuple)
	print date_str

	#-------------------------------------------------
	# conversions to datetime objects
	#-------------------------------------------------
	# time tuple to datetime object
	time_tuple = (2008, 11, 12, 13, 51, 18, 2, 317, 0)
	dt_obj = datetime.datetime(*time_tuple[0:6])
	print 'datetime.datetime(*time_tuple[0:6])'
	print repr(dt_obj)
	print str(dt_obj)
	
	# date string to datetime object
	date_str = "2008-11-10 17:53:59"
	##fejler## dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
	date_str = "2008-11-10 17:53:59"
	time_tuple = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
	dt_obj = datetime.datetime(*time_tuple[0:6])
	print repr(dt_obj)
	print str(dt_obj)

	# timestamp to datetime object in local time
	timestamp = 1226527167.595983
	dt_obj = datetime.datetime.fromtimestamp(timestamp)
	print repr(dt_obj)
	print str(dt_obj)

	# timestamp to datetime object in UTC
	timestamp = 1226527167.595983
	dt_obj = datetime.datetime.utcfromtimestamp(timestamp)
	print repr(dt_obj)
	print str(dt_obj)

	#-------------------------------------------------
	# conversions to time tuples
	#-------------------------------------------------
	# datetime object to time tuple
	dt_obj = datetime.datetime(2008, 11, 10, 17, 53, 59)
	time_tuple = dt_obj.timetuple()
	print repr(time_tuple)
	print str(time_tuple)

	# string to time tuple
	date_str = "2008-11-10 17:53:59"
	time_tuple = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
	print repr(time_tuple)
	print str(time_tuple)

	# timestamp to time tuple in UTC
	timestamp = 1226527167.595983
	time_tuple = time.gmtime(timestamp)
	print repr(time_tuple)
	print str(time_tuple)

	# timestamp to time tuple in local time
	timestamp = 1226527167.595983
	time_tuple = time.localtime(timestamp)
	print repr(time_tuple)
	print str(time_tuple)

	#-------------------------------------------------
	# conversions to timestamps
	#-------------------------------------------------
	# time tuple in local time to timestamp
	time_tuple = (2008, 11, 12, 13, 59, 27, 2, 317, 0)
	timestamp = time.mktime(time_tuple)
	print repr(timestamp)
	print str(timestamp)

	# time tuple in utc time to timestamp
	time_tuple_utc = (2008, 11, 12, 13, 59, 27, 2, 317, 0)
	timestamp_utc = calendar.timegm(time_tuple_utc)
	print repr(timestamp_utc)
	# time tuple in utc time to timestamp
	time_tuple_utc = (2008, 11, 12, 13, 59, 27, 2, 317, 0)
	#timestamp_utc = calendar.timegm(time_tuple_utc)
	timestamp_utc = calendar.timegm(time_tuple_utc)
	print repr(timestamp_utc)
	print str(timestamp_utc)

	#-------------------------------------------------
	# results
	#-------------------------------------------------
	# 2008-11-10 17:53:59
	# 2008-11-12 13:51:18
	# datetime.datetime(2008, 11, 12, 13, 51, 18)
	# datetime.datetime(2008, 11, 10, 17, 53, 59)
	# datetime.datetime(2008, 11, 12, 13, 59, 27, 595983)
	# datetime.datetime(2008, 11, 12, 21, 59, 27, 595983)
	# (2008, 11, 10, 17, 53, 59, 0, 315, -1)
	# (2008, 11, 10, 17, 53, 59, 0, 315, -1)
	# (2008, 11, 12, 21, 59, 27, 2, 317, 0)
	# (2008, 11, 12, 13, 59, 27, 2, 317, 0)
	# 1226527167.0
	# 1226498367
	
def username(infile):
	#Open settings file and find username/mailaddress
	LF = open(infile, 'r')
	input = LF.read()
	marker = '<setting id="user" value="'
	markerend = '" />'
	user=''
	if marker in input and user == '':
		user = input.split(marker)[1].split(markerend)[0]
	# Close our file
	LF.close()
	return user
	
def versiondate():
	#Open addon.xml file and find version and date
	infile = os.path.join(ADDON.getAddonInfo('path'), 'addon.xml')
	LF = open(infile, 'r')
	input = LF.read()
	marker = 'Version Date'
	markerend = '</description>'
	user=''
	if marker in input and user == '':
		user = input.split(marker)[1].split(markerend)[0]
	# Close our file
	LF.close()
	return user
	
def version():
	#Open addon.xml file and find version info
	infile = os.path.join(ADDON.getAddonInfo('path'), 'addon.xml')	
	log ('Path to addon.xml',infile)		
	LF = open(infile, 'r')
	input = LF.read()
	marker = '<addon id='
	markerend = '>'
	user=''
	if marker in input and user == '':
		user = input.split(marker)[1].split(markerend)[0]
	# Close our file
	LF.close()
	return user
	


