#!/usr/bin/python
# -*- coding: utf-8 -*-
import recordings, utils, locking
import xbmcaddon, xbmc, datetime
utils.log('service.py','Start')
#PLUGIN='plugin.video.wozboxntv'
#ADDON = xbmcaddon.Addon(id=PLUGIN)
#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
#xbmc.log('service.py in %s' % ADDON.getAddonInfo('name'))
utils.log('Version',utils.version())	
utils.log('VersionDate',utils.versiondate())
try:
	Platform = utils.rtmpdumpFilename()
	if not Platform == '':
		utils.notification('[COLOR green]Platform found and set[/COLOR]')
except:
	pass
	utils.log('FindPlatform','FAILED')  # Put in LOG
locking.recordUnlockAll()
locking.scanUnlockAll()
recordings.backupSetupxml()
recordings.restoreLastSetupXml()
recordings.ftvntvlist()
ADDON.setSetting('allmessages','')
ADDON.setSetting('RecursiveSearch','false')
if ADDON.getSetting('enable_record')=='true':
	now = recordings.parseDate(datetime.datetime.now()) 
	startDate=now - datetime.timedelta(days = 10)
	endDate=now + datetime.timedelta(days = 100)
	recordingsActive=recordings.getRecordingsActive(startDate, endDate)
	utils.log('recordingsActive',repr(recordingsActive))
	try:
		recordings.backupDataBase()
		recordings.reschedule()
		utils.notification('[COLOR green]Reschedule Complete[/COLOR]')
		ADDON.setSetting('DebugRecording','false')
	except:
		pass
		utils.notification('[COLOR red]Reschedule failed:[/COLOR] Check your planned recordings! - Recording Debug has been set')
		ADDON.setSetting('DebugRecording','true')
		xbmc.sleep(5000)

