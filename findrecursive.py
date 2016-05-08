#!/usr/bin/python
# -*- coding: utf-8 -*-
#print "findrecursive.py"
import xbmcplugin,xbmcgui,xbmcaddon,xbmc
#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
import urllib,urllib2,sys,re,os
import datetime
import time
import utils
import net
from hashlib import md5  
import json
import glob
import recordings
import locking
#print "findrecursive.py1"
def deleteFile(file):
    tries    = 0
    maxTries = 10
    while os.path.exists(file) and tries < maxTries:
        try:
            os.remove(file)
            #print 'findrecursivetimed.py: Deleted os.remove(file)= %s' % repr(file)
            break
        except:
            xbmc.sleep(50)
            tries = tries + 1

def RecursiveRecordingsPlanned(SearchAllFavorites):
	#import recordings
	import utils
	global AccessError
	AccessError = []
	#print "findrecursive.py4"
	# SearchRecursiveIn 0= Only Selected Channel, 1= Favorite Channels and 2= All My Channels
	cat = ADDON.getSetting('SearchRecursiveIn')
	print 'findrecursive.py RecursiveRecordingsPlanned: cat= %s, SearchAllFavorites= %s' % (repr(cat), repr(SearchAllFavorites))
	if locking.isAnyRecordLocked():
		locking.scanUnlockAll()
		return
	elif  locking.isAnyScanLocked():
		return
	else:
		locking.scanLock(SearchAllFavorites)
	if not locking.isScanLocked(SearchAllFavorites):
		return
	print 'findrecursive.py RUNNING RecursiveRecordingsPlanned: cat= %s, SearchAllFavorites= %s' % (repr(cat), repr(SearchAllFavorites))
	ADDON.setSetting('RecursiveSearch','true')
	if int(cat)>0 or ((not SearchAllFavorites == 'NotAllFavorites')and(not SearchAllFavorites == 'Once')and(not SearchAllFavorites == 'Hour')):
		# find all channels i favorite view
		# cat = '-1' # DUMMY -1 Favorites, -2 My Channels
		#print "findrecursive.py5"
		net.set_cookies(cookie_jar)
		imageUrl=definition.getBASEURL() + '/res/content/tv/'
		now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
		url='&mwAction=category&xbmc=1&mwData={"id":"-%s","time":"%s","type":"tv"}'%(cat,now)
		link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
		data = json.loads(link)
		channels=data['contents']
		#print 'findrecursive.py6 cat= %s, CHANNELS= %s' % (cat,str(repr(channels)))
		offset= int(data['offset'])
		from operator import itemgetter
		#Sort channels by name!
		channels = sorted(channels, key=itemgetter('name'))
		uniques=[]
		for field in channels:
			#endTime      =  field['time_to']
			name         =  field['name'].encode("utf-8")
			channel      =  field['id']
			#whatsup      =  field['whatsup'].encode("utf-8")
			#description  =  field['descr'].encode("utf-8")
			#r=re.compile("(.+?)-(.+?)-(.+?) (.+?):(.+?):(.+?)")
			#matchend     =  r.search(endTime)
			#endyear      =  matchend.group(1)
			#endmonth     =  matchend.group(2)
			#endday       =  matchend.group(3)
			#endhour      =  matchend.group(4)
			#endminute    =  matchend.group(5)
			#endDate  =  datetime.datetime(int(endyear),int(endmonth),int(endday),int(endhour),int(endminute)) + datetime.timedelta(seconds = offset)
			#print "findrecursive.py6"
			if channel not in uniques:
				#print "findrecursive.py7"
				uniques.append(channel)
			
			#if ADDON.getSetting('tvguide')=='true':
			#    name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
			#addDir(name,'url',200,imageUrl+recordings.icon(channel)+'.png',channel,'',description,now,endDate,whatsup)
		#setView('movies', 'channels-view')         
		#print 'findrecursive.py8 favorite channels= %s' % repr(uniques)
		
	#print "findrecursive.py9"
	offset=0
	conn = recordings.getConnection()
	c = conn.cursor()
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc")
	recordingsE = c.fetchall()
	from operator import itemgetter
	# Put recursive recordings changed last - first
	recordingsC = sorted(recordingsE, key=itemgetter(2), reverse=True)
	#print "findrecursive.py10"
	for index in range(0, len(recordingsC)):
		if locking.isAnyRecordLocked():
			locking.scanUnlockAll()
			ADDON.setSetting('RecursiveSearch','false')
			return
		if not locking.isScanLocked(SearchAllFavorites):
			ADDON.setSetting('RecursiveSearch','false')
			return
		#print 'findrecursive.py11: idx=%s sdt=%s edt=%s nam=%s' %(repr(index),repr(recordings.parseDate(recordingsC[index][2])),repr(recordings.parseDate(recordingsC[index][3])),repr(recordingsC[index][1]))
		if isinstance(recordings.parseDate(recordingsC[index][2]), datetime.date) and isinstance(recordings.parseDate(recordingsC[index][3]), datetime.date) and 'Recursive:' in recordingsC[index][1]:
			#print "findrecursive.py12"
			if int(ADDON.getSetting('SearchRecursiveIn')) > 0 or ((not SearchAllFavorites == 'NotAllFavorites')and(not SearchAllFavorites == 'Once')and(not SearchAllFavorites == 'Hour')):
				#print "findrecursive.py13"
				if not recordingsC[index][0] in uniques:
					findrecursiveinplaychannel(recordingsC[index][0],recordingsC[index][1],index) # Allways search channel in record
					if ADDON.getSetting('NotifyOnSearch')=='true' and not '[COLOR orange]' in recordingsC[index][1]:
						utils.notification('Find%s [COLOR green]complete in own channel[/COLOR]' % recordingsC[index][1])
				for cat in uniques:
					#print "findrecursive.py14"
					findrecursiveinplaychannel(cat,recordingsC[index][1],index)
				if ADDON.getSetting('NotifyOnSearch')=='true' and not '[COLOR orange]' in recordingsC[index][1]:
					#print "findrecursive.py15"
					utils.notification('Find%s [COLOR green]complete[/COLOR]' % recordingsC[index][1])
			else:
				#print "findrecursive.py16"
				findrecursiveinplaychannel(recordingsC[index][0],recordingsC[index][1],index)
				if ADDON.getSetting('NotifyOnSearch')=='true' and not '[COLOR orange]' in recordingsC[index][1]:
					#print "findrecursive.py17"
					utils.notification('Find%s [COLOR green]complete[/COLOR] in selected channel: %s' % (recordingsC[index][1], recordingsC[index][0]))
	#print "findrecursive.py18"
	try:
		conn.commit()
		#print 'recordings.py conn.commit OK'
	except:
		pass
		#print 'recordings.py conn.commit failed!'
	c.close()
	#print "findrecursive.py"
	#xbmc.executebuiltin("Container.Refresh")
	if ADDON.getSetting('NotifyOnSearch')=='true':
		#print "findrecursive.py19"
		utils.notification('Find all recursives [COLOR green]complete[/COLOR]')
	#print "findrecursive.py20"
	locking.scanUnlockAll()
	ADDON.setSetting('RecursiveSearch','false')
	return

def findrecursiveinplaychannel(cat,title,index):
	global AccessError
	if locking.isAnyRecordLocked():
		locking.scanUnlockAll()
		return
	if '[COLOR orange]' in title:
		print 'findrecursiveinplaychannel DISABLED: %s' % repr(title)  # Put message in LOG
		return
	if not cat in AccessError:
		url      = definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=6&a=0&mwAction=content&xbmc=1&mwData={"id":%s,"type":"tv"}' % cat
		link     = net.http_GET(url,headers={"User-Agent":"NTV-XBMC-" + ADDON.getAddonInfo('version')}).content
		data     = json.loads(link)
		try:
			rtmp     = data['src']
		except:
			pass
			AccessError.append(cat)
			#utils.notification('Find%s [COLOR red]Access Error[/COLOR] cats= %s' % (title,repr(AccessError)))
		#print 'findrecursive.py cat= %s, AccessError= %s' % (repr(cat), repr(AccessError))
		if not cat in AccessError:
			name = title
			try:
				name = name.split('Recursive:')[1]
			except:
				pass
			newname = recordings.latin1_to_ascii(name)
			newname = newname.strip()
			net.set_cookies(cookie_jar)
			now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
			url='&mwAction=content&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
			link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
			data = json.loads(link)
			offset= int(data['offset'])
			guide=data['guide']
			nowT= recordings.parseDate(datetime.datetime.today())
			for field in guide:
				r=re.compile("(.+?)-(.+?)-(.+?) (.+?):(.+?):(.+?)")
				startTime= field['time']
				endTime= field['time_to']
				name= field['name'].encode("utf-8")
				recordname= field['name'].encode("utf-8")
				description= field['description'].encode("utf-8")
				match = r.search(startTime)
				matchend = r.search(endTime)
				year = match.group(1)
				month = match.group(2)
				day = match.group(3)
				hour = match.group(4)
				minute = match.group(5)
				endyear = matchend.group(1)
				endmonth = matchend.group(2)
				endday = matchend.group(3)
				endhour = matchend.group(4)
				endminute = matchend.group(5)
				startDate= datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)) + datetime.timedelta(seconds = offset)
				endDate= datetime.datetime(int(endyear),int(endmonth),int(endday),int(endhour),int(endminute)) + datetime.timedelta(seconds = offset)
				time='[COLOR yellow](%s) - [/COLOR]'%(startDate.strftime('%H:%M'))
				recordnameT = recordings.latin1_to_ascii(recordname)
				startDateT = recordings.parseDate(startDate)
				#print 'now= %s' % repr(nowT)
				#print 'startDateT= %s' % repr(startDateT)
				#print 'cat= %s, newname= %s, recordnameT= %s' % (repr(cat), repr(newname), repr(recordnameT))
				if (newname.upper() in recordnameT.upper()) and (nowT < startDateT):
					#print "findrecursive.py21"
					recordings.schedule(cat, startDate, endDate, recordname, description)
#print "findrecursive.py22"
#PLUGIN='plugin.video.wozboxntv'
#ADDON = xbmcaddon.Addon(id=PLUGIN)

streamtype = ADDON.getSetting('streamtype')
if streamtype == '0':
    STREAMTYPE = 'NTV-XBMC-HLS-'
elif streamtype == '1':
    STREAMTYPE = 'NTV-XBMC-'

UA=STREAMTYPE + ADDON.getAddonInfo('version') 
net=net.Net()
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookie_path = os.path.join(datapath, 'cookies')
loginurl = definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=3&a=0'
username    =ADDON.getSetting('user')
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
imageUrl=definition.getBASEURL() + '/res/content/tv/'
CatUrl=definition.getBASEURL() + '/res/content/categories/'    
site=definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=6&a=0'
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookie_path = os.path.join(datapath, 'cookies')
cookie_jar = os.path.join(cookie_path, "ntv.lwp")
