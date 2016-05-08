#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import time
import os
import xbmc
import xbmcgui
import xbmcaddon
import time
import utils
import shutil
import re
import net
import locking
import json
import urllib
import glob
import urllib

from sqlite3 import dbapi2 as sqlite3

RECORDS_DB = 'recordings_adc.db'
CHANNEL_DB = 'channels.db'
SETTINGSXML = 'settings.xml'
#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
xbmc.log('recordings.py in %s' % ADDON.getAddonInfo('name'))
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))

def ftvntvlist():
# Create a FTVNTV.INI file with all channels from NTV.mx
## This file contains the "built-in" channels
## It is parsed by Pythons ConfigParser
#
#[plugin.video.ntv]
#* * * * * *  NEW NTV CHANNELS 2015-05-01 * * * * * * *=
#24 Techno=plugin://plugin.video.ntv/?url=url&mode=200&name=24+Techno+-+%5BCOLOR+yellow%5Dn+a%5B%2FCOLOR%5D&iconimage=http%3A%2F%2Fwww.ntv.mx%2Fres%2Fcontent%2Ftv%2F179.png&cat=179
#2x2=plugin://plugin.video.ntv/?url=url&mode=200&name=2x2+-+%5BCOLOR+yellow%5Dn+a%5B%2FCOLOR%5D&iconimage=http%3A%2F%2Fwww.ntv.mx%2Fres%2Fcontent%2Ftv%2F177.png&cat=177
#5 Star=plugin://plugin.video.ntv/?url=url&mode=200&name=5+Star+-+%5BCOLOR+yellow%5Dn+a%5B%2FCOLOR%5D&iconimage=http%3A%2F%2Fwww.ntv.mx%2Fres%2Fcontent%2Ftv%2F86.png&cat=86
#5 USA=plugin://plugin.video.ntv/?url=url&mode=200&name=5+USA+-+%5BCOLOR+yellow%5Dn+a%5B%2FCOLOR%5D&iconimage=http%3A%2F%2Fwww.ntv.mx%2Fres%2Fcontent%2Ftv%2F64.png&cat=64
	ftvntvini = os.path.join(datapath,'ftvntv-krogsbell') + '.ini'
	utils.log('ftvntvlist','ftvntvini= %s for %s' % (repr(os.path.isfile(ftvntvini)), repr(ftvntvini)))
	if os.path.isfile(ftvntvini) == True: 
		utils.log('ftvntvlist','ftvntvini exists - deleting')
		locking.deleteLockFile(ftvntvini)
	if os.path.isfile(ftvntvini) == False:
		now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		# create file
		utils.log('ftvntvlist','ftvntvini beeing created ' + now)
		LF = open(ftvntvini, 'a')
		# Write to our text file the information we have provided and then goto next line in our file.
		LF.write('# This file contains the NTV channels for your Package\n')
		LF.write('# Created by ' + ADDON.getAddonInfo('name') +' at ' + now + '\n')
		LF.write('[' + ADDON.getAddonInfo('id') + ']\n')
		LF.write('\n')
		try:
			CHANNELlist(LF)
		except:
			utils.notificationbox('[COLOR red]Check your internet connection![/COLOR][CR][CR][COLOR green]Access to %s channel list is not available[CR]ftvntv-krogsbell.ini NOT generated![/COLOR]' % ADDON.getAddonInfo('name') )
		LF.write('\n')
		now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		LF.write('# End of NTV channels - ended at ' + now + '\n')
		# Close our file so no further writing is posible.
		LF.close()

def CHANNELlist(LF):
	#cat = '16' # NTV Ultimate
	#cat = '-2' # My Channels
	#cat = '-1' # My Favorites
	#cat = '10' # Indian Tv
	#cat = '15' # Scandinavian
	#cat = '12' # DK + UK ?
	#cats = ['-2','-1','0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
	nowDate= datetime.datetime.today().strftime('%Y-%m-%d')
	if referralLink() == '1':
		cats = ['-2','16']
	if referralLink() == '2':
		cats = ['10']
	if referralLink() == '3':
		cats = ['-2','10','20','25']
	if not referralLink() == '1' and not referralLink() == '2' and not referralLink() == '3'  :
		cats = ['-2','-1','0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30']
	for cat in cats:
		if cat == '-2':
			LF.write('# cat= ' + cat + ' My ' + ADDON.getAddonInfo('name') + ' Channels\n')
			LF.write('*** My ' + ADDON.getAddonInfo('name') + ' Channels at ' + nowDate + ' ***********************=\n')
		elif cat == '16':
			LF.write('# cat= ' + cat + ' ' + ADDON.getAddonInfo('name') + ' Ultimate Channels\n')
			LF.write('*** ' + ADDON.getAddonInfo('name') + ' Ultimate Channels at ' + nowDate + ' ***********************=\n')
		else:
			LF.write('# cat= ' + cat + '\n')
			LF.write('*** ' + ADDON.getAddonInfo('name') + ' Channels #' + cat + ' at ' + nowDate + ' ***********************=\n')
		from hashlib import md5
		streamtype = ADDON.getSetting('streamtype')
		if streamtype == '0':
			STREAMTYPE = 'NTV-XBMC-HLS-'
		elif streamtype == '1':
			STREAMTYPE = 'NTV-XBMC-'
		site=definition.getBASEURL() + '/index.php?' + referral()+ 'c=6&a=0'
		datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		cookie_path = os.path.join(datapath, 'cookies')
		cookie_jar = os.path.join(cookie_path, "ntv.lwp")
		UA=STREAMTYPE + ADDON.getAddonInfo('version') 
		#print  "UA=STREAMTYPE + ADDON.getAddonInfo('version')= " + str(repr(UA))
		netX=net.Net()
		loginurl = definition.getBASEURL() + '/index.php?' + referral() + 'c=3&a=4'
		username    =ADDON.getSetting('user')
		password =md5(ADDON.getSetting('pass')).hexdigest()

		data     = {'email': username,
												'psw2': password,
												'rmbme': 'on'}
		headers  = {'Host':definition.getBASEURL().replace('http://',''),
												'Origin':definition.getBASEURL() + '',
												'Referer':definition.getBASEURL() + '/index.php?' + referral() + 'c=3&a=0','User-Agent' : UA}

		html = netX.http_POST(loginurl, data, headers).content
		if 'success' in html:
			if os.path.exists(cookie_path) == False:
				os.makedirs(cookie_path)
			netX.save_cookies(cookie_jar)


		#print 'default.py CHANNELS(name= %s, cat= %s)' % (repr(name),repr(cat))
		netX.set_cookies(cookie_jar)
		imageUrl=definition.getBASEURL() + '/res/content/tv/'
		now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
		url='&mwAction=category&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
		#print 'default.py YYYY site+url= %s%s'  % (site,url)
		link = netX.http_GET(site+url, headers={'User-Agent' : UA}).content
		#print 'default.py YYYY Channels link= %s' % str(repr(link))
		data = json.loads(link)
		channels=data['contents']
		#print 'default.py cat= %s, CHANNELS= %s' % (cat,str(repr(channels)))
		offset= int(data['offset'])
		from operator import itemgetter
		channels = sorted(channels, key=itemgetter('name'))
		BASE=data['base_url']
		utils.log('CHANNELlist','cat= %s with BASE= %s' % (cat, repr(BASE)))
		utils.log('CHANNELlist','imageUrl= %s' % repr(imageUrl))
		for field in channels:
			#iconimage=BASE+field['icon']
			endTime      =  field['time_to']
			name         =  field['name'].encode("utf-8")
			channel      =  field['id']
			whatsup      =  field['whatsup'].encode("utf-8")
			description  =  field['descr'].encode("utf-8")
			iconimage = getIcon(name,channel)   ##############################################################################################
			if referralLink() == '-1':   ### 2016-05-04 don't show (record)/(view) for wozbox any more
				line=name + ' (record)=plugin://' + ADDON.getAddonInfo('id') + '/?url=url&mode=2009&name=' + urllib.quote_plus(name) + '+-+%5BCOLOR+red%5Dn+a%5B%2FCOLOR%5D&iconimage=' + urllib.quote_plus(iconimage) + '&cat=' + channel 
				LF.write(line + '\n')
				line=name + ' (view)=plugin://' + ADDON.getAddonInfo('id') + '/?url=url&mode=200&name=' + urllib.quote_plus(name) + '+-+%5BCOLOR+green%5Dn+a%5B%2FCOLOR%5D&iconimage=' + urllib.quote_plus(iconimage) + '&cat=' + channel 
			if not referralLink() == '-1':
				line=name + ' =plugin://' + ADDON.getAddonInfo('id') + '/?url=url&mode=200&name=' + urllib.quote_plus(name) + '+-+%5BCOLOR+green%5Dn+a%5B%2FCOLOR%5D&iconimage=' + urllib.quote_plus(iconimage) + '&cat=' + channel 
			LF.write(line + '\n')

def referralLink():
	# 0= NTV, 1= WOZBOX www.wozboxtv.com
	referralLink=ADDON.getSetting('my_referral_link')
	return referralLink

def referral():
	#site=definition.getBASEURL() + '/index.php?c=6&a=0'
	#referralLink=ADDON.getSetting('my_referral_link')
	#if referralLink == '1':
	#	referral = 'r=wb&'
	#else:
	referral = ''
	#referralsite='http://www.ntv.mx/index.php?' + referral+ 'c=6&a=0'
	return referral

def parseDate(dateString):
	#print 'recordings.py parseDate: dateString = %s' % (repr(dateString))
	try:
		#dateString = '2050-01-01 00:00:00'
		time_tuple = datetime.datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S")
		#time_tuple = time.strptime(dateString, "%Y-%m-%d %H:%M:%S")
		x = datetime.datetime(*time_tuple[0:6])
		return x
	except:
		pass
	try:
		if isinstance(dateString, datetime.date):
			time_tuple = dateString.timetuple()
			x = datetime.datetime(*time_tuple[0:6])
			#print x
			#print 1
			return x
	except:
		pass
		#print 'DateTime conversion failed!'
	try:
		x = dateString.replace('%20', ' ')
		dateString = x
		#print 'dateString = %s' % str(repr(dateString))
	except:
		pass
		#print 'dateString = %20 exchange failed' 
	try:
		x = datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d")))
		#print x
		#print 2
		return x
	except:
		pass
		#print 'parseDate default date failed'
	try:
		x = datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
		#print x
		#print 3
		return x
	except:
		pass
		#print 'parseDate default date failed'
	try:
		#date_str = "2008-11-10 17:53:59"
		#print dateString
		time_tuple = time.strptime(dateString, "%Y-%m-%d %H:%M:%S")
		#print time_tuple
		dt_obj = datetime.datetime(*time_tuple[0:6])
		#print  dt_obj
		#print 4
		return dt_obj
	except:
		pass
	try:
		x = datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
		#print x
		#print 5
		return x
	except:
		pass
		#print 'parseDate default failed'
	try:
		#print 'parseDate(1)'
		date_str = safe_str(dateString)
		time_tuple = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")
		x = datetime.datetime(*time_tuple[0:6])
		#print x
		#print 6
		return x
	except:
		pass
		#print 'parseDate(1) Failed!'
	try:
		#print 'parseDate(2)'
		xint = float(dateString)
		x = datetime.datetime.fromtimestamp(xint)
		#print 'dateString ==> %s' % repr(x)
		#print 7
		return x
	except:
		pass
		#print 8
	utils.log('parseDate','recordings.py parseDate failed returning original input: dateString= %s or some time in the future' % repr(dateString))  # Put in LOG
	return datetime.datetime.today()  + datetime.timedelta(days = 7) # ERROR RETURN 

def backupSetupxml():
	try:
		dbPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		if not os.path.exists(dbPath):
			os.mkdir(dbPath)		
		timestampnow = datetime.datetime.now()
		timestampnowS = str(datetime.datetime.now()).split('.')[0].replace('-','').replace(' ','').replace(':','') + '-'
		backupSrc = os.path.join(dbPath, SETTINGSXML)
		backupDst = os.path.join(dbPath, timestampnowS + SETTINGSXML)
		shutil.copyfile(backupSrc, backupDst)
	except:
		pass
		utils.log('backupSetupxml','recordings.py backup SETTINGSXML Failed!')  # Put in LOG
	
def restoreSetupXml(backupSrc):
	try:
		utils.notification('[COLOR green]Restoring %s[/COLOR]' % SETTINGSXML,time=1000)
		backupSetupxml()
		dbPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		if not os.path.exists(dbPath):
			os.mkdir(dbPath)
		backupDst = os.path.join(dbPath, SETTINGSXML)
		#print 'restoreBackupDataBase from backupSrc= %s to backupDst= %s' % (backupSrc,backupDst)
		#os.remove(backupDst)
		deleteFile(backupDst)
		shutil.copyfile(backupSrc, backupDst)
		#reschedule()
		utils.notification('[COLOR green]Restoring %s Finished![/COLOR]' % SETTINGSXML)
	except:
		pass
		utils.notification('[COLOR red]Restoring %s FAILED![/COLOR]' % SETTINGSXML)

def restoreLastSetupXml():
	#utils.notification('[COLOR green]Restoring %s[/COLOR]' % SETTINGSXML,time=1000)
	path = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	files =  glob.glob(os.path.join(path, '*.xml'))
	defaultfile = os.path.join(path, SETTINGSXML)
	files1 = sorted(files, reverse=True)
	index = 0
	restored = False
	for infile in files1:
		if index < 20:
			try:
				index += 1
				mail = utils.username(infile)
				if restored == False and not infile == defaultfile and '@' in mail: 
					deleteFile(defaultfile)
					shutil.copyfile(infile, defaultfile)
					#utils.notification('[COLOR green]Restoring %s Finished![/COLOR]' % SETTINGSXML)
					restored = True
			except:
				pass
				utils.notification('[COLOR red]Restoring %s FAILED![/COLOR]' % SETTINGSXML)
		else:
			try:
				if restored == True:
					index += 1
					if not infile == defaultfile: 
						deleteFile(infile)
			except:
				pass
				utils.notification('[COLOR red]Restoring %s cleanup FAILED![/COLOR]' % SETTINGSXML)
	return restored
		
def backupDataBase():
	try:
		dbPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		if not os.path.exists(dbPath):
			os.mkdir(dbPath)
		backupSrc = os.path.join(dbPath, RECORDS_DB)
		timestampnow = datetime.datetime.now()
		timestampnowS = str(datetime.datetime.now()).split('.')[0].replace('-','').replace(' ','').replace(':','') + '-'
		#print timestampnow
		#print timestampnowS
		backupDst = os.path.join(dbPath, timestampnowS + RECORDS_DB)
		#print 'Backup database from backupSrc= %s to backupDst= %s' % (backupSrc,backupDst)
		shutil.copyfile(backupSrc, backupDst)
		#SETTINGSXML = 'settings.xml'
		#backupSrc = os.path.join(dbPath, SETTINGSXML)
		#backupDst = os.path.join(dbPath, timestampnowS + SETTINGSXML)
		#shutil.copyfile(backupSrc, backupDst)
	except:
		pass
		utils.log('backupDataBase','recordings.py backupDataBase Failed!')  # Put in LOG
	
	path = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	files =  glob.glob(os.path.join(path, '*.db'))
	defaultfile = os.path.join(path, RECORDS_DB)
	files1 = sorted(files, reverse=True)
	index = 0
	for infile in files1:
		if index < 20:
			try:
				index += 1
			except:
				pass
				utils.notification('[COLOR red]Restoring %s cleanup FAILED![/COLOR]' % RECORDS_DB)
		else:
			try:
				index += 1
				if not infile == defaultfile: 
					deleteFile(infile)
			except:
				pass
				utils.notification('[COLOR red]Restoring %s cleanup FAILED![/COLOR]' % RECORDS_DB)

def restoreBackupDataBase(backupSrc):
	try:
		utils.notification('[COLOR green]Restoring Recordings Database[/COLOR]',time=100000)
		backupDataBase()
		stopAllRecordings()
		dbPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		if not os.path.exists(dbPath):
			os.mkdir(dbPath)
		backupDst = os.path.join(dbPath, RECORDS_DB)
		#print 'restoreBackupDataBase from backupSrc= %s to backupDst= %s' % (backupSrc,backupDst)
		#os.remove(backupDst)
		deleteFile(backupDst)
		shutil.copyfile(backupSrc, backupDst)
		reschedule()
		utils.notification('[COLOR green]Restoring Recordings Database Finished![/COLOR]')
	except:
		pass
		utils.notification('[COLOR red]Restoring Recordings Database FAILED![/COLOR]')
		utils.log('restoreBackupDataBase','recordings.py backupDataBase Failed!')

def stopAllRecordings():
	recordings = getRecordings()
	#print len(recordings)
	#print recordings
	for index in range(0, len(recordings)): 
		cat       = recordings[index][0]
		name      = recordings[index][1]
		startDate = recordings[index][2]
		endDate   = recordings[index][3]
		try:
			delRecordingPlanned(cat, startDate, endDate, name)
			#print 'delRecordingPlanned(index= %s, cat= %s, startDate= %s, endDate= %s, name= %s)' %(str(repr(index)),str(repr(cat)), str(repr(startDate)), str(repr(endDate)), str(repr(name)))
		except:
			pass
			utils.log('stopAllRecordings','delRecordingPlanned FAILED(index= %s, cat= %s, startDate= %s, endDate= %s, name= %s)' %(str(repr(index)),str(repr(cat)), str(repr(startDate)), str(repr(endDate)), str(repr(name))))  # Put in LOG

def deleteFile(file):
	tries    = 0
	maxTries = 10
	while os.path.exists(file) and tries < maxTries:
		try:
			os.remove(file)
			break
		except:
			xbmc.sleep(500)
			tries = tries + 1

def FindPlatformMoved():
	# Find the actual platform
	Platform = ''
	try:
		kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'kodi.log'))
		#print kodilog
		try: logfile = open(kodilog,'r')
		except:
			pass
			kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'xbmc.log'))
			#print kodilog
			try: logfile = open(kodilog,'r')
			except:
				pass
				kodilog = xbmc.translatePath(os.path.join('special://logpath' , 'tvmc.log'))
				#print kodilog
				logfile = open(kodilog,'r')
		#print kodilog
		#print repr(logfile)
		line0 = logfile.readline()
		#print line0
		line1 = logfile.readline()
		#print line1
		line2 = logfile.readline()
		#print line2
		line3 = logfile.readline()
		#print line3
		line4 = logfile.readline()
		#print line4
		line5 = logfile.readline()
		#print line5
		line6 = logfile.readline()
		#print line6
		line7 = logfile.readline()
		#print line7
		Platform = line2.split('Platform:')[1].strip()
		#print Platform
		ADDON.setSetting('platform',Platform)
		RunningOn = line5.split('Running on ')[1].split(' ')[0].strip()
		#print 'RunningOn: %s' % repr(RunningOn) 
		ADDON.setSetting('runningon',RunningOn)
		utils.log('FindPlatformMoved','RunningOn: %s' % repr(ADDON.getSetting('runningon')))   # Put in LOG
		#print os.environ
		utils.log('FindPlatformMoved',os.environ['OS'])  # Put in LOG
	except: 
		pass
		utils.log('FindPlatformMoved','recordings.py FindPlatform FAILED')   # Put in LOG
	finally:
		logfile.close()
	return Platform

def getConnection():    
    dbPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
    if not os.path.exists(dbPath):
        os.mkdir(dbPath)

    conn   = sqlite3.connect(os.path.join(dbPath, RECORDS_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    createTable(conn)
    return conn

def getIconConnection():    
    dbPath = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('path')),'resources')
    #xbmc.log('recordings.py: getIconConnection dbPath= %s' % repr(dbPath))
    if not os.path.exists(dbPath):
        os.mkdir(dbPath)
    conn   = sqlite3.connect(os.path.join(dbPath, CHANNEL_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    conn.text_factory = str
    createIconTable(conn)
    return conn

def createTable(conn):
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS recordings_adc (cat TEXT, name TEXT, start TEXT, end TEXT, alarmname TEXT, description TEXT, playchannel TEXT,PRIMARY KEY (cat, name,start,end))")
	try:
		conn.commit()
	except:
		pass
	c.close()

def createIconTable(conn):
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS channels(id TEXT, title TEXT NOT NULL, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (title), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	try:
		conn.commit()
	except:
		pass
	c.close()

def getIcon(title,cat):
	#xbmc.log('recordings.py: getIcon title= %s, cat= %s' % (repr(title), repr(cat)))
	c = getIconConnection().cursor()
	#c.execute("SELECT * FROM channels WHERE title=? COLLATE NOCASE", [title.strip()])
	c.execute("SELECT * FROM channels WHERE id=?", [cat.strip()])
	logos = c.fetchall()
	#xbmc.log('recordings.py: logos title= %s' % repr(logos))
	if len(logos) > 0:
		logo = logos[0][2]
	else:
		logo = 'http://ntv.mx/res/ntvsmall.png'  # Fetch NTV logo http://www.ntv.mx/res/content/tv/<no>.png - http://ntv.mx/res/ntvsmall.png - http://www.brandsoftheworld.com/sites/default/files/styles/logo-thumbnail/public/032014/ntv_rgb_logo.png?itok=pDTFcL3w
	#xbmc.log('recordings.py: getIcon logo= %s' % repr(logo))
	c.close()
	return logo


def ChannelName(cat):
	#xbmc.log('recordings.py: ChannelName cat= %s' % (repr(cat)))
	c = getIconConnection().cursor()
	#c.execute("SELECT * FROM channels WHERE title=? COLLATE NOCASE", [title.strip()])
	c.execute("SELECT * FROM channels WHERE id=?", [cat.strip()])
	logos = c.fetchall()
	#xbmc.log('recordings.py: ChannelName logos title= %s' % repr(logos))
	if len(logos) > 0:
		logo = logos[0][1]
	else:
		logo = 'no name'
		utils.notification( 'NOT FOUND: channel= %s' % (cat))
	#xbmc.log('recordings.py: ChannelName logo= %s' % repr(logo))
	c.close()
	return logo

def CatFromChannelName(ChannelName):
	c = getIconConnection().cursor()
	c.execute("SELECT * FROM channels WHERE title=? COLLATE NOCASE", [ChannelName.strip()])
	#c.execute("SELECT * FROM channels WHERE id=?", [cat.strip()])
	logos = c.fetchall()
	utils.logdebug('CatFromChannelName', 'ChannelName= %s, CatFromChannelName= %s' % (repr(ChannelName), repr(logos)))
	try:
		cat= int(logos[0][0])
	except:
		pass
		return '0'
	if len(logos) > 0:
		logo = logos[0][0]
	else:
		logo = '0'
		utils.notification( 'NOT FOUND: channel= %s' % (ChannelName))
	utils.logdebug('CatFromChannelName', 'ChannelName= %s, cat= %s' % (repr(ChannelName),repr(logo)))
	c.close()
	return logo

def getRecordings():
	#print "getRecordings"
	c = getConnection().cursor()
	#print "getRecordings1"
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc")
	#print "getRecordings2"
	recordings = c.fetchall()
	#print "getRecordings3"
	#print "len(recordings)= " + str(len(recordings))
	#print 'recordings %s' %(repr(recordings))

	for index in range(0, len(recordings)):
		#print "getRecordings4"
		cat         = recordings[index][0]
		#print "getRecordings5"
		name        = recordings[index][1]
		#print "getRecordings6"
		startDate   = parseDate(recordings[index][2])
		#print "getRecordings7"
		endDate     = parseDate(recordings[index][3])
		#print "getRecordings8"
		alarmname   = recordings[index][4]
		#print "getRecordings9"
		description = recordings[index][5]
		#print "getRecordings9a"
		#print "recording# " + str(index) + ": " + str(cat) + " , " + str(name) + " , " + repr(startDate) + " , " + repr(endDate) + " , " + alarmname + " , " + str(description)
	#print "getRecordings10"
	#try:
	#	conn.commit()
	#	#print 'recordings.py conn.commit OK'
	#except:
	#	pass
	#	#print 'recordings.py conn.commit failed!'
	#try:
	#	c.commit()
	#	#print 'recordings.py c.commit OK'
	#except:
	#	pass
	#	#print 'recordings.py c.commit failed!'
	c.close()
	#print "getRecordings"
	return recordings

def getRecordingsActive(startD,endD):
	#print 'recordings.py getRecordingsActive(startD= %s,endD= %s)' % (repr(startD),repr(endD))
	startPadding = 60 * int(ADDON.getSetting('TimeBefore')) + 1
	endPadding   = 60 * int(ADDON.getSetting('TimeAfter')) + 1
	startD = parseDate(startD)
	endD = parseDate(endD)
	#print 'getRecordingsActive 1 startD= %s, endD= %s' % (repr(startD),repr(endD))
	startD = startD + datetime.timedelta(seconds = startPadding)
	endD = endD - datetime.timedelta(seconds = endPadding)
	#print 'getRecordingsActive 2 startD= %s, endD= %s' % (repr(startD),repr(endD))
	if endD < startD:
		endD = startD
	#print 'getRecordingsActive 3 startD= %s, endD= %s' % (repr(startD),repr(endD))
	c = getConnection().cursor()
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc")
	recordings = c.fetchall()
	recordingsActive=[]

	for index in range(0, len(recordings)): 
		cat         = recordings[index][0]
		name        = recordings[index][1]
		startDate   = parseDate(recordings[index][2]) + datetime.timedelta(seconds = startPadding+1)
		endDate     = parseDate(recordings[index][3]) - datetime.timedelta(seconds = endPadding+1)
		#xbmc.log('recordings.py: recordings.py getRecordingsActive name= %s, startDate= %s, endDate= %s' % (repr(name),repr(startDate),repr(endDate)))
		#xbmc.log("recordings.py: TEST: Recording Active: " + str(cat) + " , " + name.encode('ascii', 'replace') + " , startDate= " + str(startDate) + " , endDate= " + str(endDate)+ " , startD= " + str(startD) + " , endD= " + str(endD))
		#xbmc.log('recordings.py: TEST: ((endDate >= startD=%s and startDate <= endD= %s) or (endDate >= endD= %s and startDate <= startD= %s) or (endDate <= endD= %s and startDate >= startD= %s))' %(repr(endDate >= startD),repr(startDate <= endD),repr(endDate >= endD),repr(startDate <= startD),repr(endDate <= endD),repr(startDate >= startD)))
		alarmname   = recordings[index][4]
		description = recordings[index][5]
		#if not('Recursive:' in name) and not ('[COLOR blue]' in name) and not ('[COLOR orange]' in name):
		if not('Recursive:' in name) and not ('[COLOR blue]' in name):
			if ((endDate >= startD and startDate <= endD) or (endDate >= endD and startDate <= startD) or (endDate <= endD and startDate >= startD)):
				#recordingsActive.append(latin1_to_ascii(name.encode('ascii', 'replace')))
				recordingsActive.append(name)
				#print 'SET Recording Active= %s' % repr(recordingsActive)
	#try:
	#	conn.commit()
	#	#print 'recordings.py conn.commit OK'
	#except:
	#	pass
	#	#print 'recordings.py conn.commit failed!'
	#try:
	#	c.commit()
	#	#print 'recordings.py c.commit OK'
	#except:
	#	pass
	#	#print 'recordings.py c.commit failed!'
	c.close()
	#print  'RETURN Recording Active= %s' % repr(recordingsActive)
	return recordingsActive


def add(cat, startDate, endDate, recordname, description):
	startDate = parseDate(startDate)
	endDate = parseDate(endDate)
	if  ('Recursive:' in recordname):
		recordingsActive = []
	else:
		recordingsActive=getRecordingsActive(startDate, endDate)
	if not recordingsActive == []:
		#print "Do not accept new recording overlapping" + str(recordingsActive)
		utils.notification('[COLOR red]OVERLAPPING Recording NOT allowed:[/COLOR] %s' % str(recordingsActive))
		#dialog = xbmcgui.Dialog()
		#if dialog.yesno("NTV.mx", "[COLOR red]Stop recording?[/COLOR]",'', "What Do You Want To Do","[COLOR red]Stop recording[/COLOR]","[COLOR green]Ignore[/COLOR]"):
		#	return
		#else:
		if schedule(cat, startDate, endDate, recordname, description):
			utils.notification('Recording [COLOR red]set[/COLOR] for %s' % recordname)
	else:
		if schedule(cat, startDate, endDate, recordname, description):
			utils.notification('Recording [COLOR red]set[/COLOR] for %s' % recordname)
	return

def schedule(cat, startDate, endDate, recordname, description):
		import net
		from hashlib import md5  
		import json  
		#PLUGIN= 'plugin.video.wozboxntv'
		#ADDON = xbmcaddon.Addon(id=PLUGIN)
		import definition
		ADDON      = definition.getADDON()
		streamtype = ADDON.getSetting('streamtype')
		if streamtype == '0':
			STREAMTYPE = 'NTV-XBMC-HLS-'
		elif streamtype == '1':
			STREAMTYPE = 'NTV-XBMC-'
		UA=STREAMTYPE + ADDON.getAddonInfo('version') 
		net=net.Net()
		datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
		cookie_path = os.path.join(datapath, 'cookies')
		loginurl = definition.getBASEURL() + '/index.php?' + referral()+ 'c=3&a=4'  ### 2016-02-26
		username    =ADDON.getSetting('user')
		password = md5(ADDON.getSetting('pass')).hexdigest()
		data     = {'email': username,
												'psw2': password,
												'rmbme': 'on'}
		headers  = {'Host':definition.getBASEURL().replace('http://',''),
												'Origin':definition.getBASEURL() + '',
												'Referer':definition.getBASEURL() + '/index.php?' + referral()+ 'c=3&a=0'}
												
		#create cookie
		html = net.http_POST(loginurl, data, headers)
		cookie_jar = os.path.join(cookie_path, "ntv.lwp")
		if os.path.exists(cookie_path) == False:
				os.makedirs(cookie_path)
		net.save_cookies(cookie_jar)
		#set cookie to grab url
		net.set_cookies(cookie_jar)
		url      = definition.getBASEURL() + '/index.php?' + referral()+ 'c=6&a=0&mwAction=content&xbmc=1&mwData={"id":%s,"type":"tv"}' % cat
		link     = net.http_GET(url,headers={"User-Agent":"NTV-XBMC-" + ADDON.getAddonInfo('version')}).content
		data     = json.loads(link)
		#print repr(data)
		playchannel = str(data['name']) # Krogsbell 2014-10-15
		#print playchannel
		originalduration = ''
		startDate = parseDate(startDate)
		endDate   = parseDate(endDate)
		durationstring = str(endDate - startDate).split(':')
		#xbmc.log('recordings.py: durationstring= %s' % repr(durationstring))
		originalduration = ''
		if endDate > startDate and not 'day' in durationstring[0] :
			originalduration =  'Duration [' + durationstring[0] + ':' + durationstring[1] + ']. '
		if not 'Duration [' in description and not ']. ' in description:
			description = originalduration + description
		AdjustDates = False
		recordModified = False
		recordRescheduled = False
		recordRecursive = False
		recordInactive = False
		t = startDate - datetime.datetime.now()
		timeToRecording = (t.days * 86400) + t.seconds
		now = parseDate(datetime.datetime.now()) 
		startPadding = 60 * int(ADDON.getSetting('TimeBefore'))
		endPadding   = 60 * int(ADDON.getSetting('TimeAfter'))
		if ('CcCc' in recordname) and (timeToRecording < (startPadding * 2)):
			return ## Dont accept schedule from TV Grab if they are late
		recordname = recordname.replace('CcCc','',1)
		if ('AaAa' in recordname):
			AdjustDates = True
			recordModified = True
			if 'Modified' in recordname:
				recordname = recordname.replace('AaAa','',1)
			else:
				#recordname = recordname.replace('AaAa',' Modified',1)  # 2015-10-11 Don't add Modified to record name
				recordname = recordname.replace('AaAa','',1)
		if ('BbBb' in recordname):
			recordRescheduled = True
			AdjustDates = False
			if 'Rescheduled' in recordname:
				recordname = recordname.replace('BbBb','',1)
			else:
				#recordname = recordname.replace('BbBb',' Rescheduled',1)  # 2015-10-11 Don't put Rescheduled in recordname
				recordname = recordname.replace('BbBb','',1)
		if ('Recursive' in recordname):
			#print 'Recursive: - %s' % (recordname)
			recordRecursive = True
			AdjustDates = False
			recordname = recordname.replace('AaAa','',1)
			recordname = recordname.replace('BbBb','',1)
			recordname = recordname.replace('Modified','',1)
			recordname = recordname.replace('Rescheduled','',1)
			recordname = recordname.replace('  ',' ')
		recordname = recordname.replace('[COLOR blue]','') # remove inactive marker
		recordname = recordname.replace('[COLOR green]','') # remove inactive marker
		recordname = recordname.replace('[COLOR orange]','*') # remove inactive marker
		recordname = recordname.replace('[COLOR red]','') # remove inactive marker
		recordname = recordname.replace('[/COLOR]','')
		if recordname[0][0] == '*':   # DISABLE RECORD
			recordInactive = True
			AdjustDates = False
			recordname = recordname.replace('*','',1)  # 'schedule *-->inactive'
			recordname = recordname.replace('AaAa','',1)
			recordname = recordname.replace('BbBb','',1)
			recordname = recordname.replace('Modified','',1)
			recordname = recordname.replace('Rescheduled','',1)
			recordname = recordname.replace('  ',' ')
		
		showNotification = True
		if timeToRecording < 0:
			showNotification = True
			timeToRecording  = 0
			startDate        = now
		else:
			if (not recordModified) and (not recordRescheduled) and (not recordRecursive) and (not recordInactive): 
				startDate = startDate - datetime.timedelta(seconds = startPadding)
			#modify startDate if necessary; it shouldn't be earlier that 'now'
			if startDate < now:
				startDate = now
		if (startDate == now or recordModified) and (not recordRescheduled) and (not recordRecursive) and (not recordInactive):
			AdjustDates = True
		if AdjustDates == True:
			startDate=AdjustDateTime(startDate,"Start")
		if (endDate <= startDate) and (not recordRecursive) and (not recordInactive):
			endDate = startDate + datetime.timedelta(seconds = endPadding)
			AdjustDates = True
		if AdjustDates == True:
			endDate=AdjustDateTime(endDate,"End")
		if (recordname == 'n a' or AdjustDates == True) and (not recordRescheduled) and (not recordInactive) or recordModified:
			if recordModified and recordRecursive:
				recordname='Recursive:' + NAMErecord(recordname.replace('Recursive:','',1).strip())
			else:
				recordname=NAMErecord(recordname)
		if recordModified:
			try:
				description = latin1_to_ascii(DescriptionRecord(description))
			except:
				pass
		recordname= latin1_to_ascii(recordname)
		t =  startDate - now
		timeToRecording = (t.days * 86400) + t.seconds     
		showNotification = True
		if timeToRecording < 0:
			timeToRecording  = 0
			startDate        = now
		nameAlarm = 'ntv-recording-%s-%s-%s' % (cat, startDate, latin1_to_ascii_force(recordname))
		duration = endDate - startDate
		#utils.log('schedule','duration is %s, if less than 3 minutes - no recording of %s with startDate= %s and endDate= %s' % (repr(duration),repr(recordname),repr(startDate),repr(endDate)))
		if (not recordRecursive) and duration < datetime.timedelta(0, 180): # Dont record if les than 3 minutes 2016-03-16
			utils.log('schedule','duration is %s, is less than 3 minutes - no recording of %s with startDate= %s and endDate= %s' % (repr(duration),repr(recordname),repr(startDate),repr(endDate)))
			return
		#xbmc.log('recordings.py: durationDeltaTime= %s' % repr(duration))
		duration = (duration.days * 86400) + duration.seconds
		#xbmc.log('recordings.py: durationNumber= %s' % repr(duration))
		#xbmc.log('recordings.py: endPadding= %s' % repr(endPadding))
		if (not recordModified) and (not recordRescheduled) and (not recordInactive):
			duration = duration + endPadding
			#xbmc.log('recordings.py: duration+endPadding= %s' % repr(duration))
		if recordRecursive or recordInactive:
			script         =  ''   #os.path.join(ADDON.getAddonInfo('path'), 'findrecursiveX.py')
		else:
			if ADDON.getSetting('recordusing')  == '0':
				script   = os.path.join(ADDON.getAddonInfo('path'), 'record-rtmpdump.py')
			else:
				script   = os.path.join(ADDON.getAddonInfo('path'), 'record-ffmpeg.py')
		if (not recordModified) and (not recordRescheduled) and (not recordRecursive) and (not recordInactive):
			endDate = endDate + datetime.timedelta(seconds = endPadding)
		recordname = re.sub(',', '', recordname) 
		#if (int(cat) == 147) and (not recordRecursive) and (not recordInactive):  # change DR1 to DR1 HD - Krogsbell 2015-02-27 DR1 HD now have TV Guide so no switch of channel
		#	#print 'Exchange DR1(183->147) with DR1 HD(508->413) Krogsbell 2014-12-20'
		#	cat = '413'
		##args     = str(cat) + ',' + str(startDate) + ',' + str(endDate) + ',' + str(duration) + ',' + str(recordname) + ',' + str('60') + ',' + str('True')
		utils.log('TEST','recordname= %s' % repr(recordname))
		args     = cat + ',' + str(startDate) + ',' + str(endDate) + ',' + str(duration) + ',' + recordname + ',' + '60' + ',' + 'True'
		utils.log('TEST','args= %s' % repr(args))
		cmd     = ''
		if not(recordRecursive or recordInactive):
			#args= args + ',' + str(nameAlarm) + ',' + urllib.quote_plus(stringtoargument(description))  ####
			args= args + ',' + nameAlarm + ',' + stringtoargument(description)
			#cmd = 'AlarmClock(%s,RunScript(%s,%s),%d,True)' % (nameAlarm.encode('utf-8', 'replace'), script.encode('utf-8', 'replace'), args.encode('utf-8', 'replace'), timeToRecording/60)
			cmd = 'AlarmClock(%s,RunScript(%s,%s),%d,True)' % (nameAlarm, script, args, timeToRecording/60)
			#cmd = 'AlarmClock(%s,RunScript(%s,%s),%d,True)' % (nameAlarm, script, args, timeToRecording/60)
		recordingsActive = []
		if recordRecursive or recordInactive:
			if recordRecursive:
				endDate = startDate
		else:
			recordingsActive=getRecordingsActive(startDate, endDate)
		recordname = latin1_to_ascii(recordname) ##############################
		#recordingsActive = latin1_to_ascii((recordingsActive)) # Done when creating list
		if recordInactive:
			addRecordingPlanned(cat, startDate, endDate, '[COLOR orange]' + recordname + '[/COLOR]', '[COLOR orange]' + nameAlarm + '[/COLOR]', description, playchannel)
			return
		for  RecordingActive in recordingsActive:
			if ('[COLOR orange]' in RecordingActive) and (recordname in RecordingActive):
				# 2016-03-13 utils.notification('[COLOR orange]Disabled Recording: [/COLOR] %s' % (str(RecordingActive)))
				return
			if (not '[COLOR orange]' in RecordingActive) and (not recordRescheduled) and (not recordRecursive):
				try:
					if (not recordname in RecordingActive):
						utils.log('Schedule','if not recordname= %s in RecordingActive= %s' % (repr(recordname),repr(RecordingActive)))
						# 2016-03-13 utils.notification('[COLOR red]OVERLAPPING Recording NOT allowed:[/COLOR] %s' % (str(RecordingActive)))
						delRecordingPlanned(cat, startDate, endDate, '[COLOR blue]' + recordname + '[/COLOR]')
						addRecordingPlanned(cat, startDate, endDate, '[COLOR blue]' + recordname + '[/COLOR]', '[COLOR blue]' + nameAlarm + '[/COLOR]', description, playchannel)
					else:
						# 2016-03-13 utils.notification('[COLOR red]Ignore scheduling of same RecordName:[/COLOR] %s' % (str(RecordingActive)))
						xbmc.sleep(1)
					return
				except:
					pass
					utils.log('schedule', 'scheduling ERROR!')  # Put in LOG
					return
		#cancel alarm first just in case it already exists
		if not recordRescheduled:
			xbmc.executebuiltin('CancelAlarm(%s,True)' % nameAlarm)
		utils.log('TEST','cmd= %s' %repr(cmd))
		cmd= latin1_to_ascii(cmd)
		utils.log('TEST1','cmd= %s' %repr(cmd))
		xbmc.executebuiltin(cmd)
		if recordRecursive:
			#cancel alarm first just in case it already exists
			if not recordRescheduled:
				xbmc.executebuiltin('CancelAlarm(%s,True)' % nameAlarm)
		#print 'addRecordingPlanned(cat= %s, startDate= %s, endDate= %s, recordname= %s, nameAlarm= %s, description= %s, playchannel= %s)' %(cat, repr(startDate), repr(endDate), repr(recordname), repr(nameAlarm), repr(description), repr(playchannel))
		addRecordingPlanned(cat, startDate, endDate, recordname, nameAlarm, description, playchannel)
		if ('Recursive:' not in recordname):
			utils.notification('Recording [COLOR red]set[/COLOR] for %s' % recordname)
		return

def reschedule():
	backupSetupxml()
	if ADDON.getSetting('enable_record')=='true':
		backupDataBase()
		args     = str('True')
		#script   = os.path.join(ADDON.getAddonInfo('path'), 'findrecursivetimed.py')
		#scriptOnce   = os.path.join(ADDON.getAddonInfo('path'), 'findrecursivetimedOnce.py')
		#scriptHour   = os.path.join(ADDON.getAddonInfo('path'), 'findrecursivetimedHour.py')
		
		#nameAlarmRepeat = 'ntv-recording-recursive-repeat' 
		#cmdrepeat = 'AlarmClock(%s,RunScript(%s,%s),02:00:00,loop,silent)' % (nameAlarmRepeat.encode('utf-8', 'replace'), script.encode('utf-8', 'replace'), args.encode('utf-8', 'replace'))
		#xbmc.executebuiltin('CancelAlarm(%s,True)' % nameAlarmRepeat)
		# xbmc.executebuiltin(cmdrepeat)  # Active
		#nameAlarmRepeat = 'ntv-recording-recursive-once' 
		#cmdrepeat = 'AlarmClock(%s,RunScript(%s,%s),00:05:00,silent)' % (nameAlarmRepeat.encode('utf-8', 'replace'), scriptOnce.encode('utf-8', 'replace'), args.encode('utf-8', 'replace'))
		#xbmc.executebuiltin('CancelAlarm(%s,True)' % nameAlarmRepeat)
		#xbmc.executebuiltin(cmdrepeat)  # Active
		TVguide= utils.TVguide()
		nameAlarmRepeat = 'ntv-recording-recursive-hours' 
		scriptHour   = os.path.join(ADDON.getAddonInfo('path'), 'findtvguidenotificationstimed.py')
		cmdrepeat = 'AlarmClock(%s,RunScript(%s,%s),01:00:00,loop,silent)' % (nameAlarmRepeat.encode('utf-8', 'replace'), scriptHour.encode('utf-8', 'replace'), args.encode('utf-8', 'replace'))
		xbmc.executebuiltin('CancelAlarm(%s,True)' % nameAlarmRepeat)
		xbmc.executebuiltin(cmdrepeat)  # Active
		utils.notification('[COLOR green]Timers set[/COLOR] for TV Guide grab recordings hourly')
		##xbmc.executebuiltin("Container.Refresh")
		now = parseDate(datetime.datetime.now())
		recordings = getRecordings()
		utils.notification('[COLOR green]Rescheduling Recordings[/COLOR]',time=100000)
		#print len(recordings)
		#print recordings
		for index in range(0, len(recordings)): 
			cat       = recordings[index][0]
			name      = recordings[index][1]
			#startDate = parseDate(recordings[index][2])
			startDate = recordings[index][2]
			#endDate   = parseDate(recordings[index][3])
			endDate   = recordings[index][3]
			alarmname = recordings[index][4]
			description = recordings[index][5]
			try:
				delRecordingPlanned(cat, startDate, endDate, name)
			except:
				pass
				utils.log('delRecordingPlanned','FAILED(index= %s, cat= %s, startDate= %s, endDate= %s, name= %s)' %(str(repr(index)),str(repr(cat)), str(repr(startDate)), str(repr(endDate)), str(repr(name))))  # Put in LOG
			startDate = parseDate(startDate)
			endDate   = parseDate(endDate)
			if (('[COLOR blue]' not in name) and (endDate > now)) or ('Recursive' in name):
				schedule(cat,startDate,endDate,name+'BbBb',description)

def Numeric(timeT,funk):
        dialog = xbmcgui.Dialog()
        keyboard=dialog.numeric(2, funk + ' Time To Record?',timeT)
        return keyboard

def NumericStart(timeD,funk):
        dialog = xbmcgui.Dialog()
        keyboard=dialog.numeric(1, funk + ' Date To Record?',timeD)
        return keyboard

def NAMErecord(recordName):
        search_entered = recordName
        keyboard = xbmc.Keyboard(search_entered, 'Please Enter Programme Name')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText()
            if search_entered == None:
                return False          
        return search_entered 
         
def DescriptionRecord(recordName):
        search_entered = recordName
        keyboard = xbmc.Keyboard(search_entered, 'Please Enter Programme Description')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText()
            if search_entered == None:
                return False          
        return search_entered  

def AdjustDateTime(aDateTime,funk):
    startTime=aDateTime.strftime('%H:%M')
    aDateTime=NumericStart(aDateTime.strftime('%d/%m/%Y'),funk)
    startTime=Numeric(startTime,funk)
    startYear=int(aDateTime.split('/')[2])
    startMonth=int(aDateTime.split('/')[1])
    startDay=int(aDateTime.split('/')[0])
    startHour=int(startTime.split(':')[0])
    startMinute=int(startTime.split(':')[1])
    aDateTime=(startYear,startMonth,startDay,startHour,startMinute,0,0,0,-1)
    aDateTime=datetime.datetime(*aDateTime[0:6])
    return aDateTime

def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        return unicode(obj, *args)
    except UnicodeDecodeError:
        ascii_text = str(obj).encode('string_escape')
        return unicode(ascii_text)

def safe_str(obj):
    """ return the byte string representation of obj """
    try:
        return str(obj)
    except UnicodeEncodeError:
        return unicode(obj).encode('unicode_escape')

# ------------------------------------------------------------------------
# Sample code below to illustrate their usage

def write_unicode_to_file(filename, unicode_text):
    """
    Write unicode_text to filename in UTF-8 encoding.
    Parameter is expected to be unicode. But it will also tolerate byte string.
    """
    fp = file(filename,'wb')
    # workaround problem if caller gives byte string instead
    unicode_text = safe_unicode(unicode_text)
    utf8_text = unicode_text.encode('utf-8')
    fp.write(utf8_text)
    fp.close()


def _decodeHtmlEntities(string):
        """Decodes the HTML entities found in the string and returns the modified string.

        Both decimal (&#000;) and hexadecimal (&x00;) are supported as well as HTML entities,
        such as &aelig;

        Keyword arguments:
        string -- the string with HTML entities

        """
        if type(string) not in [str, unicode]:
            return string

        def substituteEntity(match):
            ent = match.group(3)
            if match.group(1) == "#":
                # decoding by number
                if match.group(2) == '':
                    # number is in decimal
                    return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x' + ent, 16))
            else:
                # they were using a name
                cp = name2codepoint.get(ent)
                if cp:
                    return unichr(cp)
                else:
                    return match.group()

        entity_re = re.compile(r'&(#?)(x?)(\w+);')
        return entity_re.subn(substituteEntity, string)[0]


"""
latin1_to_ascii -- The UNICODE Hammer -- AKA "The Stupid American"

This takes a UNICODE string and replaces Latin-1 characters with
something equivalent in 7-bit ASCII. This returns a plain ASCII string. 
This function makes a best effort to convert Latin-1 characters into 
ASCII equivalents. It does not just strip out the Latin1 characters.
All characters in the standard 7-bit ASCII range are preserved. 
In the 8th bit range all the Latin-1 accented letters are converted to 
unaccented equivalents. Most symbol characters are converted to 
something meaningful. Anything not converted is deleted.

Background:

One of my clients gets address data from Europe, but most of their systems 
cannot handle Latin-1 characters. With all due respect to the umlaut,
scharfes s, cedilla, and all the other fine accented characters of Europe, 
all I needed to do was to prepare addresses for a shipping system.
After getting headaches trying to deal with this problem using Python's 
built-in UNICODE support I gave up and decided to use some brute force.
This function converts all accented letters to their unaccented equivalents. 
I realize this is dirty, but for my purposes the mail gets delivered.


#!/usr/bin/env python
# -*- coding: utf-8 -*-

u = 'idzie wąż wąską dróżką'
uu = u.decode('utf8')
s = uu.encode('cp1250')
print(s)
"""

import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def latin1_to_ascii (unicrap):
	"""This takes a UNICODE string and replaces Latin-1 characters with
		something equivalent in 7-bit ASCII. It returns a plain ASCII string. 
		This function makes a best effort to convert Latin-1 characters into 
		ASCII equivalents. It does not just strip out the Latin-1 characters.
		All characters in the standard 7-bit ASCII range are preserved. 
		In the 8th bit range all the Latin-1 accented letters are converted 
		to unaccented equivalents. Most symbol characters are converted to 
		something meaningful. Anything not converted is deleted.
	"""
	u = unicrap   ## TEST 2016-04-29 ###############################################################################################
	utils.log('TEST-unicrap',repr(u))
	return u
	#return u ######################################
	if isinstance(u, unicode):
        #	uu = u.encode('utf-8')
        #else:
        #	uu = u
	#try:
		uu = u.encode('utf8')
	else:
		uu = u.encode('utf8', 'xmlcharrefreplace')
	#except:
	#	uu = 'a' + u +'b'
	utils.log('TEST-utf8',repr(uu))
	#try:
	##s = uu.encode('ascii', 'xmlcharrefreplace')
	#except:
	#	s = 'x' + u +'y'
	##utils.log('TEST-ascii',repr(s))
	return uu ## TEST 2016-04-29 ###############################################################################################

def latin1_to_ascii_force (unicrap):
	"""This takes a UNICODE string and replaces Latin-1 characters with
		something equivalent in 7-bit ASCII. It returns a plain ASCII string. 
		This function makes a best effort to convert Latin-1 characters into 
		ASCII equivalents. It does not just strip out the Latin-1 characters.
		All characters in the standard 7-bit ASCII range are preserved. 
		In the 8th bit range all the Latin-1 accented letters are converted 
		to unaccented equivalents. Most symbol characters are converted to 
		something meaningful. Anything not converted is deleted.
	"""	
	#return unicrap
	utils.log('TEST-unicrap',repr(unicrap))
	xlate={0x82:'Euro', 0x85:'Aa', 0x86:'Ae', 0x98:'Oe', 0xc0:'A', 0xc1:'A', 0xc2:'', 0xc3:'', 0xc4:'A', 0xc5:'A',
		0xc6:'Ae', 0xc7:'C',
		0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
		0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
		0xd0:'Th', 0xd1:'N',
		0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'O', 0xd8:'O',
		0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'U',
		0xdd:'Y', 0xde:'th', 0xdf:'ss',
		0xe0:'a', 0xe1:'a', 0xe3:'a', 0xe4:'a', 0xe5:'a',
		0xe6:'ae', 0xe7:'.0xe7.',
		0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
		0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
		0xf0:'th', 0xf1:'n',
		0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'o', 0xf8:'o',
		0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'u',
		0xfd:'y', 0xfe:'th', 0xff:'y',0xa0:'a',
		0xa1:'a', 0xa2:'.0xa2.', 0xa3:'', 0xa4:'a',
		0xa5:'aa', 0xa6:'ae', 0xa7:'s', 0xa8:'u',
		0xa9:'e', 0xaa:'e', 0xab:'<<', 0xac:'',
		0xad:'-', 0xae:'R', 0xaf:'_', 0xb0:'d',
		0xb1:'+/-', 0xb2:'^2', 0xb3:'^3', 0xb4:"'",
		0xb5:'m', 0xb6:'o', 0xb7:'*', 0xb8:'oe',
		0xb9:'^1', 0xba:'^o', 0xbb:'>>', 
		0xbc:'u', 0xbd:'1/2', 0xbe:'3/4', 0xbf:'?',
		0xd7:'*', 0xf7:'/'
		}
	r = ''
	for i in unicrap:
		if xlate.has_key(ord(i)):
			r += xlate[ord(i)]
		elif ord(i) >= 0x80:
			pass
		else:
			r += str(i)
	utils.log('TEST-unicrap',repr(r))
	return r

def imageUrlicon(imageUrl,cat,ext):
	#print 'recordings.py imageUrlicon(imageUrl,cat,ext)'
	iurl=icon(cat)
	#print repr(iurl)
	if iurl == '':
		return imageUrl + 'ntvlogo' + ext
	#print iurl.lower()[0] 
	if iurl.lower()[0] =='h':
		return iurl
	else:
		return imageUrl + 'ntvlogo' + ext

def icon(oldicon):
	#print repr(ADDON.getSetting('Use2014Icons').lower())
	#print repr('true')
	if not ADDON.getSetting('Use2014Icons').lower()=='true':
		return oldicon
	#print 'Exchange DR1(183->147) with DR1 HD(508->413) Krogsbell 2014-12-20
	
	""""
	Icons found with this lookup: Krogsbell 2015-02-15
	http://www.ntv.mx/res/content/tv/<no>.png
	2	Itv
	3	Itv 2
	4	BBC ONE
	5	BBC TWO
	7	SKY 1
	8	SKY Movies Action & Adventure
	9	SKY Comedy
	10	SKY Movies Sci Fi & Horror
	11	SKY Movies Sci Fi & Horror
	12	SKY Sports 1
	13	SKY Sports 3
	14	SKY Sports F1
	15	ESPN
	17	SKY News
	26	SKY Movies Drama & Romance
	27	SKY Movies Family
	29	SKY Movies Modern Great
	30	SKY Movies Premiere
	33	SKY Movies Showcase
	39	SKY Sports 2
	40	SKY 2
	43	Animal Planet	310 + 55 *
	44	Discovery Channel	56 + 306 *
	51	SKY Sports 4
	52	SKY Sports News
	54	FOX News
	56	National Geographic Channel
	57	SKY Movies Chrime & Thriller
	59	Itv 4
	60	Five
	61	5USA
	63	Movies4men
	64	Aljazeera
	65	4 (build of sticks)
	79	Gold (in a circle)
	80	Y Yesterday
	81	MTV
	82	VHR	71
	83	VIVA	72
	84	Alibi
	93	SKY Movies Select
	94	SKY Atlantic
	96	Discovery History	78 *
	97	Sc Discovery Science	79 *
	99	Discovery Home & Health	80 *
	100	Eden
	101	Comedy Channel
	102	Fox
	106	4E (E within 4)
	108	4More
	123	TCM Turner Classic Movies
	125	5*
	126	4Film	109 *
	135	NickJR
	137	Nickelodeon
	138	N TV Norge	100 *
	139	2 Bliss
	141	STV 1	91 *
	142	STV 2	104*
	143	4 Guld (in a star)	105 *
	146	2 Filmkanalen
	153	2
	157	4 Sport	119 *
	159	TV2 Lorry
	164	BBC News
	167	NRK 1 	127 *
	168	NRK 2 	128 *
	169	NRK 3 	129 *
	170	3	140 + 141
	171	3 Puls Viasat
	175	3 tv3.se
	177	6 in circle
	179	4 in quadrant	125 *
	183	DR1	147 *
	184	DR2	148 *
	187	TV2 zulu *
	188	TV2 charlie *
	192	Dave
	197	At The Races
	198	Racing UK	Pure Racing Entertainment
	199	BT Sport1
	201	BT Sport2
	202	Box Nation
	204	TLC
	207	SETANTA IRELAND
	208	SETANTA SPORTS
	209	Aljazeera +6
	210	Aljazeera +7
	211	Aljazeera +8
	212	Aljazeera +9
	213	Aljazeera +5
	214	Bein Sports 1
	215	Bein Sports 2
	216	Bein Sports 3
	217	Bein Sports 4
	218	Bein Sports 10
	219	H History UK
	224	Virgin
	241	TNT HD
	252	RT Russia Today
	273	Gulli
	282	DR K	230 *
	283	DR Ultra	231 *
	286	6 on blue background
	290	H2
	291	DBC Drama
	292	Pick TV
	294	Euronews
	295	BBC News
	296	Cartoonito
	297	SKY Arts 2
	298	SKY Movies Disney
	299	Itv 3+1
	303	SKY Arts 1
	304	SKY Living
	305	Good Food
	309	TV2 Fri	261 *
	310	3+ Viasat	262 *
	315	FEM
	316	SKY Sports 1 HD
	317	SKY Sports 2 HD
	318	SKY Sports 4 HD
	319	SKY Sports News HD
	320	SKY Sports 3 HD
	321	SKY Sports F1 HD
	330	OSN Sports 3
	331	OSN Sports 4
	333	Fox Sports 1 HD
	336	TSN 2 HD
	337	Sports Net World HD
	339	Sports Net One HD
	340	Bein Sport HD
	341	CTV HD
	341	HBO HD
	343	NBA  TV High Definition
	344	NBC & N HD
	http://www.ntv.mx/res/content/tv/400.png
	http://www.ntv.mx/res/content/tv/478.png
	115	http://cloud.yousee.tv/static/img/logos/Large_TV2_ny.png
	136	http://cloud.yousee.tv/static/img/logos/Large_TV2_NEWS.png
	259	http://cloud.yousee.tv/static/img/logos/Large_DR_3.png
	249 	http://cloud.yousee.tv/static/img/logos/IK_dk4.png
	"""
	iconold =['71','72','115','136','259','249','99','303','412','245','267','298','227','141','125','127','128','129','119','105','104','91','100','109','78','79','80','306','56','55','310','115','235','140','240','138','231','131','230','261','137','148','262','147','413']
	iconnew=['82','83','a','b','c','d','139','204','141','56','315','44','44','170','179','167','168','169','157','143','142','141','138','126','96','97','99','44','44','43','43','155','287','170','294','187','283','171','282','309','188','184','310','183','183']
	i = 0
	r = ''
	while i < len(iconold) and r =='':
		if oldicon==iconold[i]:
			r = iconnew[i]
		i += 1
	#print r
	#r = ''
	#for i in oldicon:
	#	if xlate.has_key(str(i)):
	#		r += xlate[str(i)]
	#		print 'recordings.py icon(oldicon) %s--> icon= %s' %(str(repr(oldicon)),str(repr(r)))
	if r=='':
		r = ''
	elif r=='a':
		return 'http://cloud.yousee.tv/static/img/logos/Large_TV2_ny.png'
	elif r=='b':
		return 'http://cloud.yousee.tv/static/img/logos/Large_TV2_NEWS.png'
	elif r=='c':
		return 'http://cloud.yousee.tv/static/img/logos/Large_DR_3.png'
	elif r=='d':
		return 'http://cloud.yousee.tv/static/img/logos/IK_dk4.png'
	#	else:
	#		r += str(i)
	#print 'recordings.py icon(oldicon) %s--> icon= %s' %(str(repr(oldicon)),str(repr(r)))
	return r
	
def stringtoargument(txtstring):
	txtstring= txtstring.replace('/n','..NewLine..')
	txtstring= txtstring.replace(',','..Comma..')
	return txtstring
def argumenttostring(txtstring):
	txtstring= txtstring.replace('..NewLine..','/n')
	txtstring= txtstring.replace('..Comma..',',')
	return txtstring


def addRecordingPlanned(cat, startDate, endDate, recordname, alarmname, description, playchannel):
	startDate = parseDate(startDate)
	endDate   = parseDate(endDate)
	conn      = getConnection()
	#conn.text_factory = str  ### 2016-04-30 TEST
	c         = conn.cursor()
	c.execute("INSERT OR REPLACE INTO recordings_adc(cat, name, start, end, alarmname, description, playchannel) VALUES(?, ?, ?, ?, ?, ?, ?)", [cat, recordname, str(startDate), str(endDate), alarmname, description, playchannel])
	#print 'addRecordingPlanned(cat=%s, startDate=%s, endDate=%s, recordname=%s, alarmname=%s, description, playchannel=%s)' % (str(repr(cat)), str(repr(startDate)), str(repr(endDate)), str(repr(recordname)), str(repr(alarmname)), str(repr(playchannel)))
	
	conn.commit()
	try:
		conn.commit()
	except:
		pass
	c.close()

def updateRecordingPlanned(alarmname, name):
	#print 'recordings.py updateRecordingPlanned(alarmname= %s, name= %s)' %(repr(alarmname), repr(name))
	conn = getConnection()
	c    = conn.cursor()
	c4   = c.execute("SELECT * FROM recordings_adc WHERE alarmname=?",  [alarmname])
	recordingsSelected = c4.fetchall()
	if len(recordingsSelected) > 0:
		for index in range(0, len(recordingsSelected)): 
			cat       = recordingsSelected[index][0]
			nameOLD      = recordingsSelected[index][1]
			startDate = recordingsSelected[index][2]
			endDate   = recordingsSelected[index][3]
			alarmnameOLD = recordingsSelected[index][4]
			description = recordingsSelected[index][5]
			playchannel = recordingsSelected[index][6]
			c4.execute("DELETE FROM recordings_adc WHERE alarmname=?",  [alarmname])
			c4.execute("INSERT OR REPLACE INTO recordings_adc(cat, name, start, end, alarmname, description, playchannel) VALUES(?, ?, ?, ?, ?, ?, ?)", [cat, name, startDate, endDate, alarmname, description, playchannel])
	try:
		conn.commit()
		#print 'recordings.py conn.commit OK'
	except:
		pass
		#print 'recordings.py conn.commit failed!'
	c.close()
	xbmc.executebuiltin("Container.Refresh")

def delRecordingPlanned(cat, startDate, endDate, recordname):
	try:
		xint = float(startDate)
		startDateX = datetime.datetime.fromtimestamp(xint)
		xint = float(endDate)
		endDateX = datetime.datetime.fromtimestamp(xint)
		#print 'delRecordingPlanned from timestamp'
	except:
		pass
	conn = getConnection()
	c    = conn.cursor()
	c4=c.execute("SELECT * FROM recordings_adc WHERE end=?", [endDate])
	recordingsSelected = c4.fetchall()
	#print repr(recordingsSelected)
	for index in range(0, len(recordingsSelected)): 
		#cat       = recordingsSelected[index][0]
		name       = recordingsSelected[index][1]
		#startDate = recordingsSelected[index][2]
		endDateXX  = recordingsSelected[index][3]
		#print 'recordings.py endDate= %s, endDateXX = %s' % (str(repr(endDate)),str(repr(endDateXX)))
		alarmname = recordingsSelected[index][4]
	if len(recordingsSelected) > 0:
		c4.execute("DELETE FROM recordings_adc WHERE alarmname=? and end=?",  [alarmname,endDate])
		xbmc.executebuiltin('CancelAlarm(%s,True)' % alarmname)
		conn.commit()
	try:
		conn.commit()
		#print 'recordings.py conn.commit OK'
	except:
		pass
		#print 'recordings.py conn.commit failed!'
	c.close()

def modifyRecordingPlanned(cat, startDate, endDate, recordname, description):
	startDate = parseDate(startDate)
	endDate   = parseDate(endDate)
	conn      = getConnection()
	c         = conn.cursor()
	recordingsSelected = c.fetchall()
	dialog = xbmcgui.Dialog()
	c1=c.execute("SELECT * FROM recordings_adc WHERE cat=?", [cat])
	recordingsSelected = c1.fetchall()
	c2=c1.execute("SELECT * FROM recordings_adc WHERE name=?",  [unicode(recordname, 'utf-8')])
	recordingsSelected = c2.fetchall()
	c3=c2.execute("SELECT * FROM recordings_adc WHERE start=?", [startDate])
	recordingsSelected = c3.fetchall()
	c4=c3.execute("SELECT * FROM recordings_adc WHERE end=?", [endDate])
	recordingsSelected = c4.fetchall()
	for index in range(0, len(recordingsSelected)): 
		cat         = recordingsSelected[index][0]
		name        = recordingsSelected[index][1]
		startDateXX = parseDate(recordingsSelected[index][2])
		endDateXX   = parseDate(recordingsSelected[index][3])
		alarmname   = recordingsSelected[index][4]
		description = recordingsSelected[index][5]
	if len(recordingsSelected) > 0:
		name = unicode(recordname, 'utf-8')
		c4.execute("DELETE FROM recordings_adc WHERE alarmname=?",  [alarmname])
		xbmc.executebuiltin('CancelAlarm(%s,True)' % alarmname)
		try:
			conn.commit()
			#print 'recordings.py conn.commit OK'
		except:
			pass
			#print 'recordings.py c4.commit failed!'
		c4.close()
		recordname = recordname.replace('[COLOR blue]','') # remove inactive marker
		recordname = recordname.replace('[COLOR green]','') # remove inactive marker
		recordname = recordname.replace('[COLOR orange]','') # remove inactive marker
		recordname = recordname.replace('[COLOR red]','') # remove inactive marker
		recordname = recordname.replace('[/COLOR]','')
		recordname = recordname +'AaAa' # marker to force change of date
		add(cat, startDate, endDate, recordname, description)
	else:
		dialog.ok("NTV.mx Modify Recording planned [COLOR red]FAILED![/COLOR]", "Selected record? " + unicode(recordname, 'utf-8'),'', "How many selected: " + str(len(recordingsSelected)))
	try:
		conn.commit()
		#print 'recordings.py conn.commit OK'
	except:
		pass
		#print 'recordings.py conn.commit failed!'
	c.close()

