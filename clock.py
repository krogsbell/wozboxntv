#!/usr/bin/python
# -*- coding: utf-8 -*-
import utils,datetime,recordings
import xbmcaddon

now=datetime.datetime.today()
RecordingsActive = recordings.getRecordingsActive(now,now)
nowHM=datetime.datetime.today().strftime('%H:%M')
if RecordingsActive == '':
	utils.notification('Clock [COLOR green]%s[/COLOR] %s' % (nowHM, RecordingsActive))
else:

	ADDON = xbmcaddon.Addon(id='plugin.video.wozboxntv')
	LastRecordProcess = ADDON.getSetting('LastRecordProcess')
	Pname = str(repr(LastRecordProcess))
	#ADDON.setSetting('LastRecordProcess', Pname)
	utils.notification('Clock [COLOR orange]%s[/COLOR] %s' % (nowHM, Pname))
