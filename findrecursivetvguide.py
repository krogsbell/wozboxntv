#!/usr/bin/env python
# -*- coding: utf-8 -*-
import definition
ADDON      = definition.getADDON()
import sys,re,os
import datetime
import time
import utils
import glob
import recordings
import locking
from operator import itemgetter

utils.log('findrecursivetvguide.py','Start')
def deleteFile(file):
    tries    = 0
    maxTries = 10
    while os.path.exists(file) and tries < maxTries:
        try:
            os.remove(file)
            break
        except:
            xbmc.sleep(50)
            tries = tries + 1

def RecursiveRecordingsPlanned(SearchAllFavorites):
	#import recordings
	cat = ADDON.getSetting('SearchRecursiveIn')
	if locking.isAnyRecordLocked():
		locking.scanUnlockAll()
		return
	elif  locking.isAnyScanLocked():
		return
	else:
		locking.scanLock(SearchAllFavorites)
	if not locking.isScanLocked(SearchAllFavorites):
		return
	utils.log('findrecursivetvguide.py RUNNING RecursiveRecordingsPlanned','cat= %s, SearchAllFavorites= %s' % (repr(cat), repr(SearchAllFavorites)))
	ADDON.setSetting('RecursiveSearch','true')
	
	conn = recordings.getConnection()
	c = conn.cursor()
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE name LIKE '%Recursive:%' COLLATE NOCASE")  # Find all recursive recordings
	recordingsE = c.fetchall()
	# Put recursive recordings changed last - first
	recordingsC = sorted(recordingsE, key=itemgetter(2), reverse=True)
	utils.log('findrecursivetvguide.py: Recursive recordings',repr(recordingsC))
	for index in range(0, len(recordingsC)):
		if isinstance(recordings.parseDate(recordingsC[index][2]), datetime.date) and isinstance(recordings.parseDate(recordingsC[index][3]), datetime.date) and 'Recursive:' in recordingsC[index][1]:
			if int(ADDON.getSetting('SearchRecursiveIn')) > 0 or ((not SearchAllFavorites == 'NotAllFavorites')and(not SearchAllFavorites == 'Once')and(not SearchAllFavorites == 'Hour')):
				if not recordingsC[index][0] in uniques:
					findrecursiveinplaychannel(recordingsC[index][0],recordingsC[index][1],index) # Allways search channel in record
					if ADDON.getSetting('NotifyOnSearch')=='true' and not '[COLOR orange]' in recordingsC[index][1]:
						utils.notification('Find%s [COLOR green]complete in own channel[/COLOR]' % recordingsC[index][1])
				for cat in uniques:
					findrecursiveinplaychannel(cat,recordingsC[index][1],index)
				if ADDON.getSetting('NotifyOnSearch')=='true' and not '[COLOR orange]' in recordingsC[index][1]:
					utils.notification('Find%s [COLOR green]complete[/COLOR]' % recordingsC[index][1])
			else:
				findrecursiveinplaychannel(recordingsC[index][0],recordingsC[index][1],index)
				if ADDON.getSetting('NotifyOnSearch')=='true' and not '[COLOR orange]' in recordingsC[index][1]:
					utils.notification('Find%s [COLOR green]complete[/COLOR] in selected channel: %s' % (recordingsC[index][1], recordingsC[index][0]))
	conn.commit()
	c.close()
	if ADDON.getSetting('NotifyOnSearch')=='true':
		utils.notification('Find all recursives [COLOR green]complete[/COLOR]')
	locking.scanUnlockAll()
	ADDON.setSetting('RecursiveSearch','false')
	return

def findrecursiveinplaychannel(cat,title,index):
	if locking.isAnyRecordLocked():
		locking.scanUnlockAll()
		return
	if '[COLOR orange]' in title:
		utils.log('findrecursiveinplaychannel','DISABLED: %s' % repr(title))  # Put message in LOG
		return

	name = title
	try:
		name = name.split('Recursive:')[1]
	except:
		pass
	newname = recordings.latin1_to_ascii(name)
	newname = newname.strip()
	now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
	nowT= recordings.parseDate(datetime.datetime.today())
	
	conn = recordings.getConnection() ###################### TV Guide database
	c = conn.cursor()
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE name CONTAINS 'Recursive:'")  ####################################################################################################
	recordingsE = c.fetchall()
	# Put recursive recordings changed last - first
	recordingsC = sorted(recordingsE, key=itemgetter(2), reverse=True)
	utils.log('findrecursivetvguide.py: Recursive recordings',repr(recordingsC))
	for field in recordingsC:
		time='[COLOR yellow](%s) - [/COLOR]'%(startDate.strftime('%H:%M'))
		recordnameT = recordings.latin1_to_ascii(recordname)
		startDateT = recordings.parseDate(startDate)
		if (newname.upper() in recordnameT.upper()) and (nowT < startDateT):
			recordings.schedule(cat, startDate, endDate, recordname, description)

