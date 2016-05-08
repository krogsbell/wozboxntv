#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
import datetime
import time
import utils, recordings
import net
from hashlib import md5
import json

#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
#xbmc.log('recorduri.py: sys.argv= %s' %(str(repr(sys.argv))))
try:
	program  = sys.argv[0]
	uri           = sys.argv[1].replace('AAabBB',' ').replace('aAabBb','?').replace('BBabAA','=')
	title         = sys.argv[2]
except:
	pass
	title = 'DRarkiv-FilmOn Videos'
try:
	xbmc.log('recorduri.py: os.environ= %s' % os.environ['OS'] ) #put in LOG
except: pass

if not ADDON.getSetting('RecordFromTVguide') == 'true':
	utils.notification('Recording %s [COLOR red]NOT enabled[/COLOR]' % (title))
else:

	LoopCountMax = int(ADDON.getSetting('LoopCount'))

	rtmpdumpEXEp = utils.rtmpdumpFilename()
	rtmpdumpEXE = os.path.join(ADDON.getAddonInfo('path'),'rtmpdump',rtmpdumpEXEp)
	xbmc.log('recorduri.py: stats os.F_OK: %s' % os.access(rtmpdumpEXE, os.F_OK))
	xbmc.log('recorduri.py: stats os.W_OK: %s' % os.access(rtmpdumpEXE, os.W_OK))
	xbmc.log('recorduri.py: stats os.X_OK: %s' % os.access(rtmpdumpEXE, os.X_OK))
	#xbmc.log('1')
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
	#xbmc.log('3')
	if os.access(rtmpdumpEXE, os.X_OK):
		RecordingDisabled = False
		#xbmc.log('4')
	else:
	
		#xbmc.log('5')
		time.sleep(1)
		#recordings.updateRecordingPlanned(nameAlarm, '[COLOR red]Set this program executable:[/COLOR] %s' % (rtmpdumpEXE))
		utils.notification('Recording %s [COLOR red]NOT possible! Set this program executable:[/COLOR] %s' % (title,rtmpdumpEXE))
		time.sleep(1000)
		RecordingDisabled = True
	#xbmc.log('6')
	recordPath = xbmc.translatePath(os.path.join(ADDON.getSetting('record_path')))
	if not utils.folderwritable(recordPath):
		utils.notification('Recording %s [COLOR red]FAILED - You must set the recording path writable![/COLOR]' % title)
		#xbmc.log('7')
	else:
		if xbmc.getCondVisibility('system.platform.linux'):
		    for dirpath, dirnames, filenames in os.walk(os.path.join(ADDON.getAddonInfo('path'),'rtmpdump')):
			for filename in filenames:
			    path = os.path.join(dirpath, filename)
			    os.chmod(path, 0777)
		#xbmc.log('8')
		datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		nowHM=datetime.datetime.today().strftime('%H:%M:%S')
		rtmp  = uri.replace('xXx',' ').replace('###',',')
		cmd  =  os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', utils.rtmpdumpFilename())
		###cmd = 'ffmpeg -i '  # Use seperately installed ffmpeg program ###
		duration = ADDON.getSetting('RecordFromTVguideDurationMinutes')
		cmdoption=' -V'  # Verbose
		qrecord = xbmcgui.Dialog()
		arecord = qrecord.yesno(ADDON.getAddonInfo('name'),'Do you want to record?', '' ,title)
		xbmc.log('recorduri: answer= %s' % repr(arecord))
		if arecord:
			if duration == 'ask':
				dialog = xbmcgui.Dialog()
				duration = dialog.numeric(0, ADDON.getAddonInfo('name') + ': Time to record in minutes, empty or 0=until end','0')
			try:
				cmdoption += ' -B ' + str(int(duration)*60) 
			except:
				pass
				cmdoption += ' -B ' +str(60*60)
			if duration == 'ignore' or duration == '' or duration == '0' or duration == 'ask':
				#cmdoption =  ' -V -B '  +str(60*60)
				cmdoption = ' -V '
				duration = '0'
			#xbmc.log('recorduri.py: cmd= %s' % cmd)
			#cmd += ' --live '
			#cmd += ' --flv "' + recordPath + '['+datetime.datetime.today().strftime('%Y-%m-%d %H-%M')+'] - ' + re.sub('[,:\\/*?\<>|"]+', '', title) + '.flv"'
			quality = ADDON.getSetting('os')
			#if quality=='13':
			#cmd += cmdoption + ' -i "' + rtmp  + ' stop=' + str(int(duration)*60000) + '"'
			if duration == '0':
				cmd += cmdoption + ' -i "' + rtmp + '"'
			else:
				cmd += cmdoption + ' -i "' + rtmp + ' stop=' + str(int(duration)*60000) + '"'
			#cmd += ' -r "' + rtmp + '"'  ## TEST
			#else:
			#	cmd += ' --rtmp "' + rtmp + '"'
			###cmd += ' -c copy -bsf:a aac_adtstoasc -o '  ### For use with ffmpeg
			cmd += ' -o '
			filetitle = recordings.latin1_to_ascii_force(title)
			filetitle = filetitle.replace('?', '')
			filetitle = filetitle.replace(':', ' -')
			filetitle = filetitle.replace('/', '')
			filetitle = filetitle.replace('+', '')
			filetitle = filetitle.replace('\\', '')
			filetitle = re.sub('[,:\\/*?\<>|"]+', '', filetitle)
			filetitle = " ".join(filetitle.split())  # Remove extra spaces from filename
			source = ''
			if ' - ' in filetitle:
				filename = filetitle.replace(' - ','####',1).split('####')
				filetitle = filename[1]
				source = filename[0]
			if duration == '0':
				cmd += '"' + recordPath + filetitle + ' ['+datetime.datetime.today().strftime('%Y-%m-%d %H-%M') + ' ' + source + '].mp4"'
			else:
				durationH = int(int(duration)/60)
				durationM = int(duration) - durationH*60
				cmd += '"' + recordPath + filetitle + ' ['+datetime.datetime.today().strftime('%Y-%m-%d %H-%M')  + ' ' + str(durationH) + 'h' + str(durationM) + 'm ' + source + '].mp4"'
			#cmd += ' --rtmp "' + rtmp
			#cmd += '"'
			xbmc.log( 'recorduri: cmd= %s' % repr(cmd))
			nowHM=datetime.datetime.today().strftime('%H:%M')
			if not RecordingDisabled:
				utils.notification('Recording %s [COLOR green]started %s[/COLOR]' % (title, nowHM))
				#recordings.updateRecordingPlanned(nameAlarm, '[COLOR green]Started ' + nowHM + '[/COLOR] ' + title)
			
			if ADDON.getSetting('os')=='11':
				utils.runCommand(cmd, LoopCount=0, libpath=None)
			else:
				libpath = utils.libPath()
				utils.runCommand(cmd, LoopCount=0, libpath=libpath)
	
			if not RecordingDisabled:
				nowHM=datetime.datetime.today().strftime('%H:%M')
				utils.notificationbox('Recording %s [COLOR red]complete[/COLOR] %s' % (title, nowHM))
