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
print 'recordffmpeguri.py:  sys.argv= %s' %(str(repr(sys.argv)))

try:
	program  = sys.argv[0]
	uri           = sys.argv[1].replace('AAabBB',' ').replace('aAabBb','?').replace('BBabAA','=').replace('xXx',' ').replace('###',',')
	title         = sys.argv[2]
except:
	pass
	title = 'DRarkiv Video'
try:
	#print os.environ
	print os.environ['OS']  #put in LOG
except: pass

if not ADDON.getSetting('RecordFromTVguide') == 'true':
	utils.notification('Recording %s [COLOR red]NOT enabled[/COLOR]' % (title))
else:
	LoopCountMax = int(ADDON.getSetting('LoopCount'))
	recordPath = xbmc.translatePath(os.path.join(ADDON.getSetting('record_path')))
	print 'recordPath= %s' %recordPath
	if not utils.folderwritable(recordPath):
		utils.notification('Recording %s [COLOR red]FAILED - You must set the recording path writable![/COLOR]' % title)
	else:
		datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		nowHM=datetime.datetime.today().strftime('%H:%M:%S')
		#print 'recorduri.py5: title= %s, LoopCount= %s at %s' % (repr(title),repr(0),nowHM)
		duration = ADDON.getSetting('RecordFromTVguideDurationMinutes')
		cmdoption=''  
		qrecord = xbmcgui.Dialog()
		arecord = qrecord.yesno(ADDON.getAddonInfo('name'),'Do you want to record?', '' ,title)
		xbmc.log('recorduriffmpeg: answer= %s' % repr(arecord))
		if arecord:
			if duration == 'ask' or 'swfUrl=http://www.filmon.com' in uri or 'http://hls.dvr.gv.filmon.com/dvr' in uri:
				dialog = xbmcgui.Dialog()
				duration = dialog.numeric(0, ADDON.getAddonInfo('name') + ': Time to record in minutes, empty or 0=until end','0')
			try:
				#cmd += ' -V --stop ' + ADDON.getSetting('RecordFromTVguideDurationMinutes')
				cmdoption += ' -t ' + str(int(duration)*60) 
			except:
				pass
				cmdoption += ' -t ' +str(120*60)
			if duration == 'ignore' or duration == '' or duration == '0' or duration == 'ask':
				#cmdoption =  ' -t ' +str(120*60)
				cmdoption = ''
				duration = '0'
			rtmp  = uri
			#xbmc.log('recorduriffmpeg.py: uri= %s' % repr(uri))
			###cmd  =  os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', utils.rtmpdumpFilename())
			if os.access('/system/vendor/bin/ffmpeg', os.X_OK):
				cmd = '/system/vendor/bin/ffmpeg -y -i '  # Use seperately installed ffmpeg program ###
			else:
				cmd = 'ffmpeg -y -i '  # Use seperately installed ffmpeg program ###
			#cmd += ' -V --stop 10000'
			#cmd += ' --live '
			#cmd += ' --flv "' + recordPath + '['+datetime.datetime.today().strftime('%Y-%m-%d %H-%M')+'] - ' + re.sub('[,:\\/*?\<>|"]+', '', title) + '.flv"'
			cmd += '"' + rtmp + '"'
			ffmpegoptions= ADDON.getSetting('ffmpegoptions')
			utils.log('ffmpegoptions',repr(ffmpegoptions))
			if ffmpegoptions == '1':
				cmd += ' -f flv -c:v libx264 -b:v 2000k -c:a aac -strict experimental -b:a 128k -ar 44100 ' + cmdoption + ' ' ### For use with ffmpeg
			else:
				cmd += ' -c copy -bsf:a aac_adtstoasc ' + cmdoption + ' ' ### For use with ffmpeg
			#cmd += ' -c copy -bsf:a aac_adtstoasc ' + cmdoption + ' ' ### For use with ffmpeg
			#cmd += ' -o '
			filetitle = title.replace('?', '')
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
				cmd += '"' + recordPath + filetitle + ' ['+datetime.datetime.today().strftime('%Y-%m-%d %H-%M')  +' ' + str(durationH) + 'h' + str(durationM) + 'm ' + source + '].mp4"'
			#cmd += ' --rtmp "' + rtmp
			#cmd += '"'
			xbmc.log('recordffmpeguri.py: cmd= %s' % repr(cmd))
			nowHM=datetime.datetime.today().strftime('%H:%M')
			utils.notification('Recording %s [COLOR green]started %s[/COLOR]' % (title, nowHM))
			
			if ADDON.getSetting('os')=='11':
				#print 'libpath= None os=11'
				utils.runCommand(cmd, LoopCount=0, libpath=None)
			else:
				libpath = utils.libPath()
				#print 'libpath= %s' % libpath
				utils.runCommand(cmd, LoopCount=0, libpath=libpath)

			nowHM=datetime.datetime.today().strftime('%H:%M')
			utils.notificationbox('Recording %s [COLOR red]complete[/COLOR] %s' % (title, nowHM))

