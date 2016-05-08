#!/usr/bin/python
# -*- coding: utf-8 -*-
#print "findtvguidenotifications.py"
import xbmcplugin,xbmcgui,xbmc,xbmcaddon
import definition
ADDON      = definition.getADDON()
import urllib,urllib2,sys,re,os
import utils
import net
from hashlib import md5  
import json
import glob
import recordings
import locking
import definition
import sqlite3
import datetime, time
from operator import itemgetter

utils.log('findtvguidenotifications.py','Start')
try:
	TimeZoneOffset = int(ADDON.getSetting('AdjustTVguideTimeZoneOffset'))
	if TimeZoneOffset > 24 or TimeZoneOffset < -24 :
		TimeZoneOffset = 0
except:
	pass
	TimeZoneOffset = 0
#EPG_DB = 'source.db'  Depends on actual TV Guide
RECORDS_DB = 'recordings_adc.db'
CHANNEL_DB = 'channels.db'
RECURSIVEMARKER = 'Recursive:'
streamtype = ADDON.getSetting('streamtype')
if streamtype == '0':
    STREAMTYPE = 'NTV-XBMC-HLS-'
elif streamtype == '1':
    STREAMTYPE = 'NTV-XBMC-'
UA=STREAMTYPE + ADDON.getAddonInfo('version') 
net=net.Net()
site=definition.getBASEURL() +'/index.php?' + recordings.referral()+ 'c=6&a=0'
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookie_path = os.path.join(datapath, 'cookies')
cookie_jar = os.path.join(cookie_path, "ntv.lwp")

ADDON      = definition.getADDON()
xbmc.log('recordings.py in %s' % ADDON.getAddonInfo('name'))
dbPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
dbPathNTV = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('path')),'resources')

def adapt_datetime(ts):
    return time.mktime(ts.timetuple())

def convert_datetime(ts):
        try:
            return datetime.datetime.fromtimestamp(float(ts))
        except ValueError:

            return None
               
# http://docs.python.org/2/library/sqlite3.html#registering-an-adapter-callable
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('timestamp', convert_datetime)



def LOGIN():
        #xbmc.log('default.py: LOGIN')
        #restoreXml=recordings.restoreLastSetupXml()
        #xbmc.log('default.py: LOGIN restoreXml= %s' % repr(restoreXml))
        loginurl = definition.getBASEURL() +'/index.php?' + recordings.referral() + 'c=3&a=4'
        username    =ADDON.getSetting('user')
        #xbmc.log('default.py: LOGIN username= %s' % repr(username))
        if  not '@' in username:
        	AUTH()
        else:
		password =md5(ADDON.getSetting('pass')).hexdigest()

		data     = {'email': username,
		                                        'psw2': password,
		                                        'rmbme': 'on'}
		headers  = {'Host':definition.getBASEURL().replace('http://',''),
		                                        'Origin':definition.getBASEURL(),
		                                        'Referer':definition.getBASEURL() +'/index.php?' + recordings.referral() + 'c=3&a=0','User-Agent' : UA}
		                                        
		html = net.http_POST(loginurl, data, headers).content
		if 'success' in html and '@' in username:
		    if os.path.exists(cookie_path) == False:
		            os.makedirs(cookie_path)
		    net.save_cookies(cookie_jar)

def MyChannels():
	LOGIN()
	cat='-2'
	net.set_cookies(cookie_jar)
	now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
	url='&mwAction=category&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	data = json.loads(link)
	channels=data['contents']
	from operator import itemgetter
	#Sort channels by name 
	channels = sorted(channels, key=itemgetter('name'))
	AllMyChannels=[]
	
	for field in channels:
		name         =  field['name'].encode("utf-8")
		channel      =  field['id']
		displaychannelnumber = (name + ' (' +channel+'):\n' )
		AllMyChannels.append(displaychannelnumber)
		#utils.log('findtvguidenotifications', 'displaychannelnumber= %s' % repr(displaychannelnumber))
	#utils.log('findtvguidenotifications', 'AllMyChannels= %s' % repr(AllMyChannels))
	return AllMyChannels

def findtvguidenotifications():
	TVguide= utils.TVguide()
	Recursive = RecursiveRecordings() ## Get all recursive recordings
	#guidenotifications= ADDON.getSetting('tvguidenotifications')
	for Guide in range(0, len(TVguide)):
		guide = TVguide[Guide][0]
		guideDB = TVguide[Guide][1]
		grabGuide(guide,guideDB)
		findrecursiverecordingsinGuide(guide,guideDB,Recursive)
	
	# Show menuentry when finished OK - but not when run in the background
	name= 'Grab from TV Guide finished!'
	utils.log('findtvguidenotifications', name)
	liz=xbmcgui.ListItem(name)
	try:
		xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url='',listitem = liz, isFolder = True) 
		utils.log('findtvguidenotifications', 'Finished in foreground with menu item')
	except:
		pass
		utils.log('findtvguidenotifications', 'Finished in background - no menu item')

def RecursiveRecordings():
	conn = recordings.getConnection()
	c = conn.cursor()
	#c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE name LIKE '%Recursive:%' and NOT LIKE '%COLOR orange%' COLLATE NOCASE")  # Find all active recursive recordings
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE name LIKE ? COLLATE NOCASE",['%'+RECURSIVEMARKER+'%'])  # Find all active recursive recordings RECURSIVEMARKER
	recordingsE = c.fetchall()
	# Put recursive recordings changed last - first
	recordingsC = sorted(recordingsE, key=itemgetter(2), reverse=True)
	utils.log('Recursive recordings',repr(recordingsC))
	return recordingsC

def findrecursiverecordingsinGuide(guide,EPG_DB,Recursive):
	if ADDON.getSetting('DebugRecording') == 'false':
		try:
			findrecursiverecordingsinGuideCode(guide,EPG_DB,Recursive)
		except:
			pass
			utils.log('findrecursiverecordingsinGuide EXECUTION FAILED', 'guide= %s' % guide)
	else:
		findrecursiverecordingsinGuideCode(guide,EPG_DB,Recursive)		

def findrecursiverecordingsinGuideCode(guide,EPG_DB,Recursive):			
	#utils.log('findrecursiverecordingsinGuideCode', 'guide= %s' % guide)
	ADDONguide = xbmcaddon.Addon(id=guide)

	NTVchannels = MyChannels()
	#SearchRecursiveIn: 0=Only selected channel|1=First 25 Cannels|2=First 50 Channels|3=All My Channels
	SearchRecursiveIn= int(ADDON.getSetting('SearchRecursiveIn'))
	#utils.log('findtvguidenotificationsGuide', 'MyNTVchannels= %s' % repr(NTVchannels))
	
	conv   = sqlite3.connect(os.path.join(dbPath, RECORDS_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
	conv.execute('PRAGMA foreign_keys = ON')
	##conv.row_factory = sqlite3.Row
	conv.text_factory = str
	b = conv.cursor()
	b.execute("CREATE TABLE IF NOT EXISTS channels(id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (id, source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")

	dbPathEPG = xbmc.translatePath(ADDONguide.getAddonInfo('profile'))
	#utils.log('findrecursiverecordingsinGuide', 'dbPath= %s' % dbPathEPG)
	if not os.path.exists(dbPathEPG):
		#utils.log('findrecursiverecordingsinGuide', 'os.mkdir(dbPath) where dbPath= %s' % dbPathEPG)
		os.mkdir(dbPathEPG)

	conn   = sqlite3.connect(os.path.join(dbPathEPG, EPG_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
	conn.execute('PRAGMA foreign_keys = ON')
	conn.row_factory = sqlite3.Row
	conn.text_factory = str
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS programs (channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, image_large TEXT, image_small TEXT, source TEXT, updates_id INTEGER, PRIMARY KEY (channel, updates_id), FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	c.execute("CREATE TABLE IF NOT EXISTS programsForHumans (channel TEXT, title TEXT, start_date TEXT, end_date TEXT, description TEXT, image_large TEXT, image_small TEXT, source TEXT, updates_id INTEGER, PRIMARY KEY (channel, updates_id), FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	c.execute("CREATE TABLE IF NOT EXISTS channels (id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY(id,source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	conn.commit()

	for index in range(0, len(Recursive)):
		#utils.log('findrecursiverecordingsinGuide', 'index= %s' % index)
		#utils.log('findrecursiverecordingsinGuide', 'Recursive[index][1]= %s' % repr(Recursive[index][1].replace(RECURSIVEMARKER, '').strip()))
		cat= Recursive[index][0]
		#utils.log('findrecursiverecordingsinGuide', 'cat= %s' % repr(cat))
		# Find channel name in TV Guide 1. saved conversion 2. name as used i NTV
		b.execute("SELECT * FROM channels WHERE id=? and source=?", [cat,guide])
		channelconvert = b.fetchall()
		#utils.log('findrecursiverecordingsinGuide', 'channelconvert= %s' % repr(channelconvert))
		if len(channelconvert) == 1:
			channel= channelconvert[0][1]
		else:
			channel= recordings.ChannelName(cat)
		#utils.log('findrecursiverecordingsinGuide', 'channel= %s' % repr(channel))
		# Find id from TV Guide channel name
		#c.execute("SELECT * FROM channels")
		#channelconvert = c.fetchall()
		#utils.log('findrecursiverecordingsinGuide', 'channelconvert= %s' % repr(channelconvert))
		c.execute("SELECT * FROM channels WHERE title=? COLLATE NOCASE", [channel])
		channelconvert = c.fetchall()
		#utils.log('findrecursiverecordingsinGuide', 'channelconvert= %s' % repr(channelconvert))
		try:
			channel= channelconvert[0][0]
		except:
			pass
			channel= 0
		#utils.log('findrecursiverecordingsinGuide', 'channel= %s' % repr(channel))
		#c.execute("SELECT * FROM programs WHERE title LIKE ? AND channel=? COLLATE NOCASE", ['%'+(Recursive[index][1].replace(RECURSIVEMARKER, '').strip())+'%',channel])
		recursivechannel= channel
		c.execute("SELECT * FROM programs WHERE title LIKE ? COLLATE NOCASE", ['%'+(Recursive[index][1].replace(RECURSIVEMARKER, '').strip())+'%'])
		notifications = c.fetchall()
		#utils.log('findrecursiverecordingsinGuide', 'notifications= %s' % repr(notifications))
		#utils.log('findrecursiverecordingsinGuide', 'len(notifications)= %s' % repr(len(notifications)))
		if len(notifications) > 0:
			for indexN in range(0, len(notifications)): 
				channel= notifications[indexN][0]
				program= notifications[indexN][1]
				#utils.log('findrecursiverecordingsinGuide', 'indexN= %s' % repr(indexN))
				#utils.log('findrecursiverecordingsinGuide', 'cat= %s' % repr(cat))
				#utils.log('findrecursiverecordingsinGuide', 'channel= %s' % repr(channel))
				#utils.log('findrecursiverecordingsinGuide', 'program= %s' % repr(program))
				c.execute("SELECT DISTINCT id, title, logo, stream_url, source, visible, weight FROM channels WHERE id=?",  [channel])
				channeldata= c.fetchall()
				#utils.log('findrecursiverecordingsinGuide', 'channeldata= %s' % repr(channeldata))
				if len(channeldata) > 0:
					#utils.log('findrecursiverecordingsinGuide', 'channel.weight= channeldata[0][6]= %s' % repr(channeldata[0][6]))
					if (SearchRecursiveIn==1 and channeldata[0][6] > 25) or (SearchRecursiveIn==2 and channeldata[0][6] > 50) :  ### channel.weight
						#utils.log('findrecursiverecordingsinGuide', 'channel.weight> 25 or 50')
						nonsense=''
					else:
						now = datetime.datetime.now()
						#utils.log('findrecursiverecordingsinGuide', 'now= %s' % repr(now))
						#utils.log('findrecursiverecordingsinGuide', 'SearchRecursiveIn= %s' % repr(SearchRecursiveIn))
						if SearchRecursiveIn==0:
							cy= c.execute("SELECT * FROM programs WHERE channel=? AND title=? AND start_date >= ?",  [recursivechannel, program, now]) ### Recursive Only on channel in record
						elif SearchRecursiveIn==1:
							#cx= c.execute("SELECT * FROM channels WHERE weight<?",  ['25']) ### Recursive first 25 visible ###################################
							#programs= cx.fetchall()
							#utils.log('findrecursiverecordingsinGuide', '25 programs= %s' % repr(programs))
							#cy= cx.execute("SELECT * FROM programs WHERE title=? AND start_date >= ?",  [program, now]) ### Recursive first 25 ###################################
							cy= c.execute(
			    "SELECT DISTINCT p.*, c.weight FROM channels c, programs p WHERE c.weight < 25 AND p.channel = c.id AND p.title = ? AND p.start_date >= ?",
			    [program, now])
							###cy= cx.execute('SELECT p.*, (SELECT 1 FROM notifications n WHERE n.channel=p.channel AND n.program_title=p.title AND n.source=p.source) AS notification_scheduled FROM programs p WHERE p.channel IN (\'' + ('\',\''.join(channelMap.keys())) + '\') AND p.source=? AND p.end_date > ? AND p.start_date < ?', [self.source.KEY, startTime, endTime])
						elif SearchRecursiveIn==2:
							cy= c.execute(
			    "SELECT DISTINCT p.*, c.weight FROM channels c, programs p WHERE c.weight < 50 AND p.channel = c.id AND p.title = ? AND p.start_date >= ?",
			    [program, now])
						else:
							cy= c.execute("SELECT * FROM programs WHERE title=? AND start_date >= ?",  [program, now])  ##### All programs ######
						#cy= c.execute("SELECT * FROM programs WHERE title=?",  [program])  ########### No Date - Test #########
						programs= cy.fetchall()
						#utils.log('findrecursiverecordingsinGuide', 'programs= %s' % repr(programs))
						NTVchannelSelect= NTVchannels
						for prog in range(0, len(programs)):
							try:
								cweight= programs[prog][9]
								#utils.log('findrecursiverecordingsinGuide', 'cweight= %s' % repr(cweight))
							except:
								pass
							pchannel= programs[prog][0]
							#utils.log('findrecursiverecordingsinGuide', 'pchannel= %s' % repr(pchannel))
							ptitle= programs[prog][1]
							#utils.log('findrecursiverecordingsinGuide', 'ptitle= %s' % repr(ptitle))
							pstart_date= programs[prog][2]
							pend_date= programs[prog][3]
							pdescription= programs[prog][4]
							#utils.log('findrecursiverecordingsinGuide', 'channeldata[0][1]= %s' % (repr(channeldata[0][1])))
							cat= recordings.CatFromChannelName(channeldata[0][1])
							#utils.log('findrecursiverecordingsinGuide', 'cat= %s' % (repr(cat)))
							if cat == '0':  ## Channel from TVguide not found ##
								b.execute("SELECT * FROM channels WHERE title=? and source=?", [channeldata[0][1],guide])
								channelconvert = b.fetchall()
								if len(channelconvert) == 0:
									SelectedChannel = xbmcgui.Dialog().select(guide + ': Select Channel for: ' + channeldata[0][1] + ' - ' + channeldata[0][0] + ' - ' + ptitle, NTVchannelSelect)
									#utils.log('findrecursiverecordingsinGuide', 'SelectedChannel= %s' % (repr(SelectedChannel)))
									if SelectedChannel <> -1:
										try:
											id = NTVchannelSelect[SelectedChannel].split('(')[1].split(')')[0]
											if int(id) > 0:
												b.execute("INSERT OR REPLACE INTO channels(id, title, logo, stream_url, source, visible, weight) VALUES(?, ?, ?, ?, ?, ?, ?)", [id, channeldata[0][1], '', '', guide, 'True', id])

												cat = id
										except:
											pass
									conv.commit()
								else:
									cat = channelconvert[0][0]
							now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
							pdescription = pdescription + '. . Created: ' + now +' Recursive from ' + guide + ' - ' + channeldata[0][1] + ' - ' + channeldata[0][0] + ' - ' + ptitle
							#utils.log('findrecursiverecordingsinGuide', 'cat= %s' % repr(cat))
							if int(cat) > 0:
								recordings.schedule(cat, pstart_date + datetime.timedelta(hours = TimeZoneOffset), pend_date + datetime.timedelta(hours = TimeZoneOffset), 'CcCc' + program, pdescription)
								# Set notification in TV Guide channeldata[0][0], program, ADDON.getAddonInfo('name')
								try:
									c.execute("SELECT * FROM notifications WHERE channel = ? AND program_title = ? AND source = ?",  [channeldata[0][0], program, channeldata[0][4]])
									notify =  c.fetchall()
									if len(notify) == 0:  ## Only insert if not already there
										c.execute("INSERT OR REPLACE INTO notifications (channel, program_title, source) VALUES(?, ?, ?)", [channeldata[0][0], program, channeldata[0][4]])
								except:
									pass
	utils.log('findtvguidenotifications','Transfer programs to programsForHumans')
	now = datetime.datetime.now()
	# Transfer programs to programsForHumans
	#utils.log('findtvguidenotifications','channels= %s' % (repr(programs[prog][0])))
	c.execute("SELECT * FROM channels WHERE visible")
	channels= c.fetchall()
	utils.log('findtvguidenotifications','channels= %s' % (repr(channels)))
	for chan in range(0, len(channels)):
		if channels[chan][1] == channels[chan][0]:
			humanchannel= channels[chan][0]
		else:
			humanchannel= channels[chan][1] + ' (' + channels[chan][0] + ')'
		c.execute("SELECT * FROM programs WHERE start_date >= ? AND channel=?",  [now,channels[chan][0]]) 
		programs= c.fetchall()
		###utils.log('findtvguidenotifications','programs= %s' % (repr(programs)))
		for prog in range(0, len(programs)):
			#utils.log('findtvguidenotifications','channels= %s' % (repr(channels)))
			#utils.log('findtvguidenotifications','channels[0][0]= %s, channels[0][1]= %s, egual= %s' % (repr(channels[0][1]), repr(channels[0][0]), repr(channels[0][1] == channels[0][0])))
			
			c.execute("SELECT * FROM programsForHumans WHERE channel=? AND title=? AND start_date=? AND end_date=? AND description=? AND source=?", [humanchannel, programs[prog][1],str(programs[prog][2]),str(programs[prog][3]),programs[prog][4],programs[prog][7]])
			programsForHumans =  c.fetchall()
			#utils.log('findtvguidenotifications','len(programsForHumans)= %s' % repr(len(programsForHumans)))
			if len(programsForHumans) == 0:  ## Only insert if not already there
				c.execute("INSERT OR REPLACE INTO programsForHumans (channel, title, start_date, end_date, description, image_large, image_small, source) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", [humanchannel, programs[prog][1],str(programs[prog][2]),str(programs[prog][3]),programs[prog][4],programs[prog][2],programs[prog][3],programs[prog][7]])
	conn.commit()
	c.close()
	b.close()
	
	#utils.log('findrecursiverecordingsinGuideCode', 'dbPath= %s' % dbPath)
	utils.log('findrecursiverecordingsinGuideCode EXECUTION Finished', 'guide= %s' % guide)

def adjusttvguide(conn,c,first):
	try: 
		sqlfilename= ADDON.getSetting('AdjustTVguideSqlFile')
		utils.log('adjusttvguide',repr(sqlfilename))
		sqlfile= open(sqlfilename,'r')
		line0 = sqlfile.readline()
		utils.log('adjusttvguide',repr(line0))
		if 'firstchannel=' in line0.lower():
			firstchannel= line0.lower().split('firstchannel=')[1].strip()
			if firstchannel != first.lower():
				line= sqlfile.readline().strip('\n')
				while line != '':
					utils.log('adjusttvguide',repr(line))
					c.execute(line)
					line= sqlfile.readline()
				utils.log('adjusttvguide','DROP TABLE programsForHumans')
				c.execute("DROP TABLE programsForHumans")
			else:
				utils.log('adjusttvguide','TV Guide already updated')
		else:
			utils.notificationbox('adjusttvguide: The sql file %s to adjust the TV Guide must start with: Firstchannel=' % repr(sqlfilename))
	except:
		pass
		utils.log('adjusttvguide','No Adjust TV GuideSQL file or not all lines executed!')
	conn.commit()	

def grabGuide(guide,EPG_DB):
	if ADDON.getSetting('DebugRecording') == 'false':
		try:
			grabGuideCode(guide,EPG_DB)
		except:
			pass
			utils.log('grabGuide EXECUTION FAILED', 'guide= %s' % guide)
	else:
		grabGuideCode(guide,EPG_DB)		


def grabGuideCode(guide,EPG_DB):		
	#utils.log('findtvguidenotifications', 'guide= %s' % guide)
	#try:
	ADDONguide = xbmcaddon.Addon(id=guide)

	dbPathEPG = xbmc.translatePath(ADDONguide.getAddonInfo('profile'))
	#utils.log('findtvguidenotifications', 'dbPath= %s' % dbPathEPG)
	if not os.path.exists(dbPathEPG):
		#utils.log('findtvguidenotifications', 'os.mkdir(dbPath) where dbPath= %s' % dbPathEPG)
		os.mkdir(dbPathEPG)
	if not os.path.exists(dbPathNTV):
		os.mkdir(dbPathNTV)

	sqlite3.register_adapter(datetime.datetime, adapt_datetime)
	sqlite3.register_converter('timestamp', convert_datetime)
	
	cNTV   = sqlite3.connect(os.path.join(dbPathNTV, CHANNEL_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
	cNTV.execute('PRAGMA foreign_keys = ON')
	cNTV.row_factory = sqlite3.Row
	cNTV.text_factory = str
	a = cNTV.cursor()
	a.execute("CREATE TABLE IF NOT EXISTS channels(id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (id, source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	cNTV.commit()
	
	conv   = sqlite3.connect(os.path.join(dbPath, RECORDS_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
	conv.execute('PRAGMA foreign_keys = ON')
	##conv.row_factory = sqlite3.Row
	conv.text_factory = str
	b = conv.cursor()
	b.execute("CREATE TABLE IF NOT EXISTS channels(id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY (id, source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	conv.commit()
	
	conn   = sqlite3.connect(os.path.join(dbPathEPG, EPG_DB), timeout = 10, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread = False, isolation_level=None)
	conn.execute('PRAGMA foreign_keys = ON')
	conn.row_factory = sqlite3.Row
	conn.text_factory = str
	c = conn.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS notifications (channel TEXT, program_title TEXT, source TEXT, FOREIGN KEY(channel, source) REFERENCES channels(id, source) ON DELETE CASCADE)")
	c.execute("CREATE TABLE IF NOT EXISTS programs (channel TEXT, title TEXT, start_date TIMESTAMP, end_date TIMESTAMP, description TEXT, image_large TEXT, image_small TEXT, source TEXT, updates_id INTEGER, PRIMARY KEY (id, updates_id), FOREIGN KEY(updates_id) REFERENCES updates(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	c.execute("CREATE TABLE IF NOT EXISTS channels (id TEXT, title TEXT, logo TEXT, stream_url TEXT, source TEXT, visible BOOLEAN, weight INTEGER, PRIMARY KEY(id,source), FOREIGN KEY(source) REFERENCES sources(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED)")
	conn.commit()
	
	## Adjust TV Guide
	#utils.log('findtvguidenotifications', 'SELECT * FROM channels WHERE weight=0')
	c.execute("SELECT * FROM channels WHERE weight=0")
	channels = c.fetchall()
	if len(channels) == 1:
		adjusttvguide(conn,c,channels[0][1])
	else:
		adjusttvguide(conn,c,'missing channel 0 force update')
		
	c.execute("SELECT * FROM notifications")
	notifications = c.fetchall()
	utils.log('findtvguidenotifications', 'notifications= %s' % repr(notifications))
	#utils.log('findtvguidenotifications', 'len(notifications)= %s' % repr(len(notifications)))

	NTVchannels = MyChannels() #########################################
	#utils.log('findtvguidenotifications', 'MyNTVchannels= %s' % repr(NTVchannels))

	#if len(NTVchannels) < 2:   ## Only Euronews is not enough (2)
	#	from operator import itemgetter
	#	a.execute("SELECT * FROM channels WHERE id=ltrim(id,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') ") #### id must be number!
	#	NTVchannels = a.fetchall()
	#	#utils.log('findtvguidenotifications', 'NTVchannels(unsorted)= %s' % repr(NTVchannels))
	#	NTVchannels = sorted(NTVchannels, key=itemgetter(1))
	#	#utils.log('findtvguidenotifications', 'NTVchannels= %s' % repr(NTVchannels))

	for index in range(0, len(notifications)): 
		channel= notifications[index][0]
		program= notifications[index][1]
		#utils.log('findtvguidenotifications', 'channel= %s' % repr(channel))
		#utils.log('findtvguidenotifications', 'program= %s' % repr(program))
		c.execute("SELECT DISTINCT id, title, logo, stream_url, source, visible, weight FROM channels WHERE id=?",  [channel])
		channeldata= c.fetchall()
		#utils.log('findtvguidenotifications', 'channeldata= %s' % repr(channeldata))

		now = datetime.datetime.now()
		#utils.log('findtvguidenotifications', 'now= %s' % repr(now))
		c.execute("SELECT * FROM programs WHERE channel=? AND title=? AND start_date >= ?",  [channel, program, now])
		programs= c.fetchall()
		#utils.log('findtvguidenotifications', 'programs= %s' % repr(programs))
	
		'''
		channel= 'BBC 1 London'
		program= 'The Big Questions'
		channeldata= [(u'BBC 1 London', u'BBC One', u'http://wozboxtv.com/downloads/xmltv/logos/BBC%20One.png', None, u'xmltv', 1, 0)]
		now= datetime.datetime(2016, 2, 7, 10, 46, 51, 603477)
		programs= [(u'BBC 1 London', u'The Big Questions', datetime.datetime(2016, 2, 7, 11, 0), datetime.datetime(2016, 2, 7, 12, 0), u'Nicky Campbell presents moral and religious discussions on topical issues from King Edward VI School, Southampton.(n)', None, u'http://cdn.tvguide.co.uk/HighlightImages/Large/big_questions.jpg', u'xmltv', 1)]
		'''
	
		#NTVchannelSelect = []
		#for x in range (0,len(NTVchannels)):
		#	#try:
		#		#utils.log('findtvguidenotifications', 'NTVchannels[x]= %s' % (repr(NTVchannels[x])))
		#		#if isnumeric(str(NTVchannels[x])):
		#		NTVchannelSelect.append(NTVchannels[x])
		#		#utils.log('findtvguidenotifications', 'NTVchannelSelect= %s' % (repr(NTVchannelSelect)))
		#	#except:
		#	#	pass
		#utils.log('findtvguidenotifications', 'guide= %s and EPG_DB= %s' % (guide,EPG_DB))
		#utils.log('findtvguidenotifications', 'NTVchannelSelect= %s' % (repr(NTVchannelSelect)))
	
		NTVchannelSelect= NTVchannels
		for prog in range(0, len(programs)):
			pchannel= programs[prog][0]
			ptitle= programs[prog][1]
			pstart_date= programs[prog][2]
			pend_date= programs[prog][3]
			pdescription= programs[prog][4]
			#utils.log('findtvguidenotifications', 'channeldata[0][1]= %s' % (repr(channeldata[0][1])))
			cat= recordings.CatFromChannelName(channeldata[0][1])
			#utils.log('findtvguidenotifications', 'cat= %s' % (repr(cat)))
			if cat == '0':  ## Channel from TVguide not found ##
				b.execute("SELECT * FROM channels WHERE title=? and source=?", [channeldata[0][1],guide])
				channelconvert = b.fetchall()
				if len(channelconvert) == 0:
					utils.log('findtvguidenotifications', 'Waiting for Select Channel for  %s' % (repr(guide + ': Select Channel for: ' + channeldata[0][1] + ' - ' + channeldata[0][0] + ' - ' + ptitle)))
					SelectedChannel = xbmcgui.Dialog().select(guide + ': Select Channel for: ' + channeldata[0][1] + ' - ' + channeldata[0][0] + ' - ' + ptitle, NTVchannelSelect)
					utils.log('findtvguidenotifications', 'SelectedChannel= %s' % (repr(SelectedChannel)))
					if SelectedChannel <> -1:
						try:
							id = NTVchannelSelect[SelectedChannel].split('(')[1].split(')')[0]
							if int(id) > 0:
								b.execute("INSERT OR REPLACE INTO channels(id, title, logo, stream_url, source, visible, weight) VALUES(?, ?, ?, ?, ?, ?, ?)", [id, channeldata[0][1], '', '', guide, 'True', id])
								cat = id
						except:
							pass
					conv.commit()
				else:
					cat = channelconvert[0][0]
			now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
			pdescription = pdescription + '. . Created: ' + now + ' Notification from ' + guide + ' - ' + channeldata[0][1] + ' - ' + channeldata[0][0] + ' - ' + ptitle
			#utils.log('findtvguidenotifications', 'cat= %s' % repr(cat))
			if int(cat) > 0:
				recordings.schedule(cat, pstart_date + datetime.timedelta(hours = TimeZoneOffset), pend_date + datetime.timedelta(hours = TimeZoneOffset), program, pdescription)
		
	c.close()
	b.close()
	utils.log('grabGuide', 'FINISHED!')
	#except:
	#	pass
	#	utils.log('grabGuide', 'FAILED!')

######################################################################
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
	#utils.log('findrecursivetvguide.py RUNNING RecursiveRecordingsPlanned','cat= %s, SearchAllFavorites= %s' % (repr(cat), repr(SearchAllFavorites)))
	ADDON.setSetting('RecursiveSearch','true')
	
	conn = recordings.getConnection()
	c = conn.cursor()
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE name LIKE '%Recursive:%' COLLATE NOCASE")  # Find all recursive recordings
	recordingsE = c.fetchall()
	# Put recursive recordings changed last - first
	recordingsC = sorted(recordingsE, key=itemgetter(2), reverse=True)
	#utils.log('findrecursivetvguide.py: Recursive recordings',repr(recordingsC))
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
	#utils.log('findrecursivetvguide.py: Recursive recordings',repr(recordingsC))
	for field in recordingsC:
		time='[COLOR yellow](%s) - [/COLOR]'%(startDate.strftime('%H:%M'))
		recordnameT = recordings.latin1_to_ascii(recordname)
		startDateT = recordings.parseDate(startDate)
		if (newname.upper() in recordnameT.upper()) and (nowT < (startDateT + datetime.timedelta(hours = TimeZoneOffset))):
			recordings.schedule(cat, startDate + datetime.timedelta(hours = TimeZoneOffset), endDate + datetime.timedelta(hours = TimeZoneOffset), recordname, description)


