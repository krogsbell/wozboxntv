#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
import datetime
import time
import utils, recordings
import net
from hashlib import md5  
import json  
import xbmcaddon
import xbmcgui

#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
#print 'record.py: sys.argv= %s' %(str(repr(sys.argv)))
program  = sys.argv[0]
cat      = sys.argv[1]
startTime= sys.argv[2]
endTime  = sys.argv[3]
duration = sys.argv[4]
title    = sys.argv[5]
argv6    = sys.argv[6]
argv7    = sys.argv[7]
nameAlarm= sys.argv[8]
try: 
	#get description
	description= sys.argv[9]
except:
	pass
	description= 'Error getting description'

try: 
	#print os.environ
	print os.environ['OS']  #put in LOG
except: pass

LoopCountMax = int(ADDON.getSetting('LoopCount'))

rtmpdumpEXEp = utils.rtmpdumpFilename()
quality = ADDON.getSetting('os')
if quality == '13':
	osplatform = ADDON.getSetting('osplatform')
	print 'record.py: osplatform= %s' % osplatform
	try:
		import shutil
		os.chmod(rtmpdumpEXEp, 0777)
	except:
		pass
	try:
		if osplatform == 0:
			osplatformexe = 'androidarm/rtmpdump'
			#osplatformlib = 'androidarm/librtmp.so'
		else:
			osplatformexe = 'android86/rtmpdump'
			#osplatformlib = 'android86/librtmp.so.0'
		print 'record.py: try to copy %s --> %s' % (osplatformexe,rtmpdumpEXEp)
		shutil.copyfile(os.path.join(ADDON.getAddonInfo('path'),'rtmpdump',osplatformexe),rtmpdumpEXEp) # Folder should xist!	
		print 'record.py: copied %s --> %s' % (osplatformexe,rtmpdumpEXEp)
	except:
		pass
		print 'record.py: copied FAILED %s --> %s' % (osplatformexe,rtmpdumpEXEp)
	try:
		os.chmod(rtmpdumpEXEp, 0777) 
	except:
		pass
		print 'record.py: set 0777 FAILED %s --> /system/bin/rtmpdump' % osplatformexe

	rtmpdumpEXE = rtmpdumpEXEp
else:
	rtmpdumpEXE = os.path.join(ADDON.getAddonInfo('path'),'rtmpdump',rtmpdumpEXEp)
print 'record.py: rtmpdumpEXE= %s' % repr(rtmpdumpEXE)
print 'record.py: os.path.exists(rtmpdumpEXE)= %s' % repr(os.path.exists(rtmpdumpEXE))
xbmc.log('stats os.F_OK: %s' % os.access(rtmpdumpEXE, os.F_OK))
xbmc.log('stats os.W_OK: %s' % os.access(rtmpdumpEXE, os.W_OK))
xbmc.log('stats os.X_OK: %s' % os.access(rtmpdumpEXE, os.X_OK))

if not xbmc.getCondVisibility('system.platform.windows'):
	if os.access(rtmpdumpEXE, os.X_OK):
		print 'Permissions ------ 0777 ----- GREAT !!'  # Put in LOG
	else:
		print 'Permissions -----------------   BAD !!'  # Put in LOG
		for dirpath, dirnames, filenames in os.walk(os.path.join(ADDON.getAddonInfo('path'),'rtmpdump')):
			for filename in filenames:
				path = os.path.join(dirpath, filename)
				try:
					os.chmod(path, 0777) 
					print 'Permissions set with: CHMOD 0777 !!'  # Put in LOG
				except: pass
# LINUX ?
try:
	if xbmc.getCondVisibility('system.platform.linux'):
	    for dirpath, dirnames, filenames in os.walk(os.path.join(ADDON.getAddonInfo('path'),'rtmpdump')):
		for filename in filenames:
		    path = os.path.join(dirpath, filename)
		    os.chmod(path, 0777) 
except:
	pass
#ANDROID ?
try:
	if xbmc.getCondVisibility('system.platform.android'):
	    os.system('mount -o remount rw /sdcard')
	    for dirpath, dirnames, filenames in os.walk(os.path.join(ADDON.getAddonInfo('path'),'rtmpdump')):
		for filename in filenames:
		    path = os.path.join(dirpath, filename)
		    if not path.startswith('/'):
		        path='/'+path
		    os.system("chmod 777 %s" % path)
	    os.system('mount -o remount ro /sdcard')
except:
	pass
    

if os.access(rtmpdumpEXE, os.X_OK):
	#print 'os.access(/home/hans/.xbmc/addon/plugin.video.wozboxntv/rtmpdump/linux32/rtmpdump, os.X_OK)= OK'
	RecordingDisabled = False
else:
	time.sleep(1)
	#print 'os.access(/home/hans/.xbmc/addon/plugin.video.wozboxntv/rtmpdump/linux32/rtmpdump, os.X_OK)= FAIL'
	recordings.updateRecordingPlanned(nameAlarm, '[COLOR red]Set this program executable:[/COLOR] %s' % (rtmpdumpEXE))
	utils.notification('Recording %s [COLOR red]NOT possible! Set this program executable:[/COLOR] %s' % (title,rtmpdumpEXE))
	time.sleep(1000)
	RecordingDisabled = True

#print 'record.py: nameAlarm= %s' % (str(repr(nameAlarm)))
#print 'record.py: LoopCountMax= %s' % (str(repr(LoopCountMax)))
recordPath = xbmc.translatePath(os.path.join(ADDON.getSetting('record_path')))
print 'record.py: recordPath= %s' %recordPath
if not utils.folderwritable(recordPath):
	utils.notification('Recording %s [COLOR red]FAILED - You must set the recording path writable![/COLOR]' % title)
else:
	net=net.Net()

	datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	cookie_path = os.path.join(datapath, 'cookies')

	loginurl = definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=3&a=4'  ## 2016-02-26 Mikey1234 ver 3.4.6
	username = ADDON.getSetting('user')
	password = md5(ADDON.getSetting('pass')).hexdigest()


	data     = {'email': username,
		                                'psw2': password,
		                                'rmbme': 'on'}
	headers  = {'Host':definition.getBASEURL().replace('http://',''),
		                                'Origin':definition.getBASEURL(),
		                                'Referer':definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=3&a=0'}
		                                
	#create cookie
	html = net.http_POST(loginurl, data, headers)
	cookie_jar = os.path.join(cookie_path, "ntv.lwp")
	if os.path.exists(cookie_path) == False:
		os.makedirs(cookie_path)
	net.save_cookies(cookie_jar)

	#set cookie to grab url
	net.set_cookies(cookie_jar)

	Retry = True
	LoopCount = 0
	import locking
	try:
		nowHM=datetime.datetime.today().strftime('%H:%M:%S')
	except:
		pass
	try:
		#locking.recordUnlock(title)
		#A new recording unlocks all previous - otherwise the retry feature will make some fuzz
		locking.recordUnlockAll()
	except:
		pass
	try:
		locking.recordLock(nameAlarm)
	except:
		pass
	#print 'record.py: title= %s' % repr(title)
	while (Retry == True) and (LoopCount < LoopCountMax) and (locking.isRecordLocked(nameAlarm)):
		nowHM=datetime.datetime.today().strftime('%H:%M:%S')
		#print 'record.py0: title= %s, LoopCount= %s at %s' % (repr(title),repr(LoopCount),nowHM)
		url      = definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=6&a=0&mwAction=content&xbmc=1&mwData={"id":%s,"type":"tv"}' % cat
		link     = net.http_GET(url,headers={"User-Agent":"NTV-XBMC-" + ADDON.getAddonInfo('version')}).content
		data     = json.loads(link)
		playchannelName = recordings.ChannelName(cat)
		if playchannelName == '':
			playchannel = str(cat) 
		else:
			playchannel = playchannelName
		try:
			rtmp     = data['src']
		except:
			pass
			utils.notification('Recording [COLOR red]NOT possible! No data on channel[/COLOR] %s' % (playchannel))
			recordings.updateRecordingPlanned(nameAlarm, 'Recording [COLOR red]NOT possible! No data on channel[/COLOR] '+ playchannel + " - " + title + ' at ' + nowHM)
			#nowHM=datetime.datetime.today().strftime('%H:%M:%S')
			#print 'record.py1: title= %s, LoopCount= %s at %s' % (repr(title),repr(LoopCount),nowHM)
			time.sleep(10)
			#nowHM=datetime.datetime.today().strftime('%H:%M:%S')
			#print 'record.py2: title= %s, LoopCount= %s at %s' % (repr(title),repr(LoopCount),nowHM)
			rtmp = ''
		#nowHM=datetime.datetime.today().strftime('%H:%M:%S')
		#print 'record.py3: title= %s, LoopCount= %s at %s' % (repr(title),repr(LoopCount),nowHM)
		#utils.notification('Recording %s [COLOR orange]LOOP %s[/COLOR]' % (title, nowHM))
		if rtmp == '' :
			Retry = True
			LoopCount += 1
			LoopCountMax = int(ADDON.getSetting('LoopCount'))
			nowHM=datetime.datetime.today().strftime('%H:%M:%S')
			#print 'record.py4: title= %s, LoopCount= %s at %s' % (repr(title),repr(LoopCount),nowHM)
		else:
			nowHM=datetime.datetime.today().strftime('%H:%M:%S')
			#print 'record.py5: title= %s, LoopCount= %s at %s' % (repr(title),repr(LoopCount),nowHM)
			rtmp  = '%s' % (rtmp)
			cmd  =  os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', utils.rtmpdumpFilename())
			cmd += ' --stop ' + str(duration) 
			cmd += ' --live '
			#cmd += ' --flv "' + recordPath + '['+datetime.datetime.today().strftime('%Y-%m-%d %H-%M')+ ' ' +str(LoopCount) +'] - ' + playchannel + ' - ' + re.sub('[,:\\/*?\<>|"]+', '', title) + '.flv"'
			filetitle = recordings.latin1_to_ascii_force(title)
			filetitle = filetitle.replace('?', '')
			filetitle = filetitle.replace(':', ' -')
			filetitle = filetitle.replace('/', '')
			filetitle = filetitle.replace('+', '')
			filetitle = filetitle.replace('\\', '')
			filetitle = re.sub('[,:\\/*?\<>|"]+', '', filetitle)
			filetitle = " ".join(filetitle.split())  # Remove extra spaces from filename
			recordstarttime = datetime.datetime.today().strftime('%Y-%m-%d %H-%M')
			durationH = 0
			durationM = 0
			if 'Duration [' in description and '].' in description:
				orgduration = (description.split('uration [')[1].split('].')[0] + 'm').replace(':','h')
			else:
				durationH = int(int(duration)/3600)
				durationM = (int(duration) - durationH*3600)/60
				orgduration =  str(durationH) + 'h' + str(durationM) + 'm'
			xbmc.log('record.py: duration= %s, durationH= %s, durationM= %s' %(repr(duration),repr(durationH),repr(durationM)))
			cmd += ' --flv "' + recordPath + filetitle + ' ['+recordstarttime+ ' NTV-' + playchannel + ' ' + orgduration +']' 
			if LoopCount >0:
				cmd += ' ' + str(LoopCount) + '.flv"'
			else:
				cmd += '.flv"'
			infofilename = recordPath + filetitle + ' ['+recordstarttime+ ' NTV-' + playchannel  + ' ' + orgduration + '].txt'
			print 'record.py: infofilename= %s' % (repr(infofilename))
			#cmd += ' --rtmp "' + rtmp
			quality = ADDON.getSetting('os')
			if quality=='13':
				cmd += ' -i "' + rtmp + '&stop=' + str(int(duration)*60000) + '"'
			else:
				cmd += ' --rtmp "' + rtmp + '"'
				#cmd += ' -i "' + rtmp + '&end=' + str(int(duration)) + '"'  ### TEST option -i ########################################################
			#cmd += '"'
	
			nowHM=datetime.datetime.today().strftime('%H:%M')
		
			if LoopCount == 0 and not RecordingDisabled:
				utils.notification('Recording %s [COLOR green]started %s[/COLOR]' % (title, nowHM))
				recordings.updateRecordingPlanned(nameAlarm, '[COLOR green]Started ' + nowHM + '[/COLOR] ' + title)
				try:
					# Create file with info on recording 'infofilename'
					LF = open(infofilename, 'a')
					crlf = '\r\n'
					# Write to our text file the information we have provided and then goto next line in our file.
					LF.write('Recorded using: ' + ADDON.getAddonInfo('name')+ crlf)
					LF.write('Version= ' + ADDON.getAddonInfo('version')+ crlf)
					LF.write('Version Info= ' + utils.version()+ crlf)
					LF.write('Version Date= ' + utils.versiondate()+ crlf)
					program  = sys.argv[0]
					LF.write('Program Name= ' + program+ crlf)
					LF.write('Platform= ' + ADDON.getSetting('platform')+ crlf)
					LF.write('Running on= ' + ADDON.getSetting('runningon')+ crlf)
					LF.write('OS= ' + ADDON.getSetting('os')+ crlf)
					LF.write('Record Path= ' + ADDON.getSetting('record_path')+ crlf + crlf)
					LF.write('Record Command: ' + crlf + cmd+ crlf + crlf)
					LF.write('Title= ' + title + crlf)
					LF.write('PlayChannel= ' + playchannel + crlf)
					LF.write('cat= ' + cat + crlf)
					LF.write('StartTime= ' + startTime + crlf)
					LF.write('EndTime= ' + endTime + crlf)
					LF.write('Duration= ' + str(int(round(int(duration)/60))) + ' minutes' + crlf)
					LF.write('Argv6= ' + argv6 + crlf)
					LF.write('Argv7= ' + argv7 + crlf)
					LF.write('NameAlarm= ' + nameAlarm + crlf)
					if not len(description) == 3 and not description == 'n a':
						LF.write('Description:' + crlf + recordings.argumenttostring(description) + crlf)
					else:
						LF.write('No description!' + crlf)
					# Close our file so no further writing is posible.
					LF.close()
					print 'record.py: infofilename= %s written and closed' % (repr(infofilename)) # Add to log
				except:
					pass
			else:
				LoopNr = str(LoopCount)
				if not RecordingDisabled:
					utils.notification('Recording %s [COLOR orange]RESTARTED# %s %s[/COLOR]' % (title, LoopNr, nowHM))
					recordings.updateRecordingPlanned(nameAlarm, '[COLOR orange]Restarted# %s %s[/COLOR] %s' % (LoopNr, nowHM, title))
		
			if ADDON.getSetting('os')=='11':
					#print 'libpath= None os=11'
					utils.runCommand(cmd, LoopCount, libpath=None)
			else:
					libpath = utils.libPath()
					print 'record.py: libpath= %s' % repr(libpath)
					#print 'libpath= %s' % libpath
					utils.runCommand(cmd, LoopCount, libpath=libpath)

			nowP = recordings.parseDate(datetime.datetime.today())
			endTimeO =  recordings.parseDate(endTime)
			time_tuple = endTimeO.timetuple()
			timestamp = time.mktime(time_tuple) - 120
			endTimeM = datetime.datetime.fromtimestamp(timestamp)
			endTimeP =  recordings.parseDate(endTimeM)
			nowHM=datetime.datetime.today().strftime('%H:%M')
			if 	endTimeP > nowP and not RecordingDisabled:
				recordings.updateRecordingPlanned(nameAlarm, '[COLOR red]Completed Early ' + nowHM + '[/COLOR] ' + title)
				startTime = nowP
				Retry = True
				LoopCount += 1
				LoopCountMax = int(ADDON.getSetting('LoopCount'))
			else:
				if not RecordingDisabled:
					recordings.updateRecordingPlanned(nameAlarm, '[COLOR green]Complete ' + nowHM + '[/COLOR] ' + title)
				Retry = False

	if not RecordingDisabled:
		utils.notification('Recording %s [COLOR red]complete[/COLOR]' % title)
	locking.recordUnlock(nameAlarm)
	utils.log('Recording finished',title)
	
