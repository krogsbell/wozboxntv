#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
import time
from datetime import datetime, timedelta
import calendar
import net
import json
import locking,utils
import recordings
import glob
import definition

ADDON      = definition.getADDON()
xbmc.log('default.py in %s' % ADDON.getAddonInfo('name'))

streamtype = ADDON.getSetting('streamtype')
if streamtype == '0':
    STREAMTYPE = 'NTV-XBMC-HLS-'
elif streamtype == '1':
    STREAMTYPE = 'NTV-XBMC-'

UA=STREAMTYPE + ADDON.getAddonInfo('version') 
#print  "UA=STREAMTYPE + ADDON.getAddonInfo('version')= " + str(repr(UA))
net=net.Net()

def OPEN_URL(url):
    #print 'OPEN_URL: %s' % repr(url)
    req = urllib2.Request(url, headers={'User-Agent' : UA} ) 
    con = urllib2.urlopen( req )
    link= con.read()
    return link

recordPath = xbmc.translatePath(os.path.join(ADDON.getSetting('record_path')))
try:
	recordDisplayPath = xbmc.translatePath(os.path.join(ADDON.getSetting('record_display_path')))
except:
	pass
if not os.path.exists(recordDisplayPath):
	recordDisplayPath = recordPath
	ADDON.setSetting('record_display_path',recordDisplayPath)
imageUrl=definition.getBASEURL() +'/res/content/tv/'
CatUrl=definition.getBASEURL() +'/res/content/categories/'    
site=definition.getBASEURL() +'/index.php?' + recordings.referral()+ 'c=6&a=0'
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookie_path = os.path.join(datapath, 'cookies')
cookie_jar = os.path.join(cookie_path, "ntv.lwp")
from hashlib import md5    


def LOGIN():
        utils.log('default.py','LOGIN')
        restoreXml=recordings.restoreLastSetupXml()
        utils.log('default.py','LOGIN restoreXml= %s' % repr(restoreXml))
        loginurl = definition.getBASEURL() +'/index.php?' + recordings.referral() + 'c=3&a=4'
        username    =ADDON.getSetting('user')
        utils.log('default.py','LOGIN username= %s' % repr(username))
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
		    ADDON.setSetting('ga_time',str(datetime.today()+ timedelta(hours=6)).split('.')[0])
            
            
def AUTH():
        utils.log('default.py','AUTH')
        try:
            os.remove(cookie_jar)
        except:
            pass
        username =ADDON.getSetting('user')
        password =md5(ADDON.getSetting('pass')).hexdigest()
        utils.log('default.py','username= %s, password= %s' % (repr(username),repr(password)))
        if not '@' in username:
        	utils.log('default.py','firstrun.Launch()')
        	import firstrun
        url = definition.getBASEURL() +'/?' + recordings.referral() + 'c=3&a=4&email=%s&psw2=%s&rmbme=on'%(username,password)
        utils.log('default.py','url= %s' % repr(url))
        html = net.http_GET(url, headers={'User-Agent' :UA}).content
        utils.log('default.py','html= %s' % repr(html))
        if 'success' in html and '@' in username:
            LOGIN()
            ADDON.setSetting('firstrun','true')
        else:
            utils.log('default.py','firstrun.Launch(1)')
            import firstrun
            
def parse_date(dateString):
    import time
    return datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))


def sessionExpired():

    expiry=ADDON.getSetting('ga_time')


    now        = datetime.today()
 
    
    prev = parse_date(expiry)


    return (now > prev)            
            
def CATEGORIES():
	## 3.4.6 AUTH()
	if sessionExpired():  ## 3.4.7
        	print 'LOGIN'  ## 3.4.7
        	LOGIN()  ## 3.4.7
    	else:            ## 3.4.7
        	print 'Cookie In Date'  ## 3.4.7
	if ADDON.getSetting('enable_record')=='true':
		addDir('Recordings','url',6,'','','','')
		addDir('Planned Recordings','url',3,'','','','')
		addDir('Restore Planned Recordings','url',104,'','','','')
	addDir('My Account','url',8,'','','','')
	net.set_cookies(cookie_jar)
	link = net.http_GET(site+'&mwAction=categories&mwData=tv', headers={'User-Agent' : UA}).content
	data = json.loads(link)
	for field in data:
		cat= str(field['id'])
		name= field['name'].encode("utf-8")
		iconimage= field['icon'].encode("utf-8")
		addDir(name,'url',2,CatUrl+recordings.icon(cat)+'.png',cat,'','')
	setView('movies', 'main-view')         
        
def CHANNELS(name,cat):
	#print 'default.py CHANNELS(name= %s, cat= %s)' % (repr(name),repr(cat))
	net.set_cookies(cookie_jar)
	imageUrl=definition.getBASEURL() +'/res/content/tv/'
	now= datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    	## 3.4.6 now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    	url='&mwAction=category&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
	#print 'default.py YYYY site+url= %s%s'  % (site,url)
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	#print 'default.py YYYY Channels link= %s' % str(repr(link))
	data = json.loads(link)
	channels=data['contents']
	#print 'default.py cat= %s, CHANNELS= %s' % (cat,str(repr(channels)))
	offset= int(data['offset'])
	# Krogsbell 2014-09-18 3 lines
	from operator import itemgetter
	#Sort channels by name or id/cat if record debug!
	if ADDON.getSetting('SortAlphabetically')=='true':
		if ADDON.getSetting('DebugRecording')=='XXtrue':  # Just show sorted by name and not ID
			channels = sorted(channels, key=itemgetter('id'))
		else:
			channels = sorted(channels, key=itemgetter('name'))
	BASE=data['base_url']
	print 'BASE= %s' % repr(BASE)
	print 'imageUrl= %s' % repr(imageUrl)
	uniques=[]
	genreselect=[]
	if not 'Favorites' in name:
		if ADDON.getSetting('genre')=='true':
			for field in channels:
				genre      =  field['genre']
				if genre.title() not in uniques:
					uniques.append(genre.title())
			uniques = sorted(uniques)
			_GENRE_= uniques[xbmcgui.Dialog().select('Select Genre', uniques)]
			for field in channels:
				#iconimage=BASE+field['icon'] # NTV original 3.4.4
				genre      =  field['genre']
				endTime      =  field['time_to']
				name         =  field['name'].encode("utf-8")
				channel      =  field['id']
				whatsup      =  field['whatsup'].encode("utf-8")
				displaychannelnumber = (name + ' (' +channel+'):\n' )
				description  =  (displaychannelnumber + field['descr']).encode("utf-8")
				#if iconimage == 'http://www.ntv.mx/res/content/tv/ntvlogo.png':
					#iconimage= recordings.imageUrlicon(BASE,channel,'.png')
				iconimage= recordings.getIcon(name,channel)
				if ADDON.getSetting('enable_record')=='true':
					THETIME=time.strptime(endTime, '%Y-%m-%d %H:%M:%S')
					endDate  =  datetime(*THETIME[:6])+ timedelta(seconds = offset)
				else:
					endDate  = ''
				if ADDON.getSetting('tvguide')=='true':
					if not endDate  == '' and recordings.getRecordingsActive(endDate,endDate): #################################################################
						name='%s - [COLOR red]%s[/COLOR]'%(name,whatsup)
					else:
						name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
					#name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
				if _GENRE_.lower() == genre.lower():
					addDir(name,'url',200,iconimage,channel,'',description,now,endDate,whatsup)
				setView('movies', 'channels-view')
				#name=field['genre']
				#url=field['genre_id']
				#if name not in uniques:
				#	uniques.append(name)
				#	addDir(name.title(),'url',5,'',cat,'','')
				#setView('movies', 'main-view')  
		else:
			for field in channels:
				#iconimage=BASE+field['icon']
				endTime      =  field['time_to']
				name         =  field['name'].encode("utf-8")
				channel      =  field['id']
				whatsup      =  field['whatsup'].encode("utf-8")
				displaychannelnumber = (name + ' (' +channel+'):\n' )
				description  =  (displaychannelnumber + field['descr']).encode("utf-8")
				#description  =  field['descr'].encode("utf-8")
				#if iconimage == 'http://www.ntv.mx/res/content/tv/ntvlogo.png':
					#iconimage= recordings.imageUrlicon(BASE,channel,'.png')
				iconimage= recordings.getIcon(name,channel)
				if ADDON.getSetting('enable_record')=='true':
					THETIME=time.strptime(endTime, '%Y-%m-%d %H:%M:%S')
					#endDate  =  datetime.datetime(*THETIME[:6])+ datetime.timedelta(seconds = offset)
					endDate  =  datetime(*THETIME[:6])+ timedelta(seconds = offset)
				else:
					endDate  = ''
				if ADDON.getSetting('tvguide')=='true':
					if not endDate  == '' and recordings.getRecordingsActive(endDate,endDate): #################################################################
						name='%s - [COLOR red]%s[/COLOR]'%(name,whatsup)
					else:
						name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
				addDir(name,'url',200,iconimage,channel,'',description,now,endDate,whatsup)
				setView('movies', 'channels-view')   
			#for field in channels:
			#	endTime      =  field['time_to']
			#	name         =  field['name'].encode("utf-8")
			#	channel      =  field['id']
			#	whatsup      =  field['whatsup'].encode("utf-8")
			#	description  =  field['descr'].encode("utf-8")
			#	r=re.compile("(.+?)-(.+?)-(.+?) (.+?):(.+?):(.+?)")
			#	matchend     =  r.search(endTime)
			#	endyear      =  matchend.group(1)
			#	endmonth     =  matchend.group(2)
			#	endday       =  matchend.group(3)
			#	endhour      =  matchend.group(4)
			#	endminute    =  matchend.group(5)

			#	endDate  =  datetime.datetime(int(endyear),int(endmonth),int(endday),int(endhour),int(endminute)) + datetime.timedelta(seconds = offset)

				
			#	if ADDON.getSetting('tvguide')=='true':
			#		if ADDON.getSetting('DebugRecording')=='true':
			#			name='%s (%s) - [COLOR yellow]%s[/COLOR]'%(str(channel),name,whatsup)
			#		else:
			#			name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
			#	newiconurl= recordings.imageUrlicon(imageUrl,channel,'.png')
			#	addDir(name,'url',200,newiconurl,channel,'',description,now,endDate,whatsup)
			#setView('movies', 'channels-view')         
	else:

		for field in channels:
			#iconimage=BASE+field['icon']
			endTime      =  field['time_to']
			name         =  field['name'].encode("utf-8")
			channel      =  field['id']
			whatsup      =  field['whatsup'].encode("utf-8")
			displaychannelnumber = (name + ' (' +channel+'):\n' )
			description  =  (displaychannelnumber + field['descr']).encode("utf-8")
			#description  =  field['descr'].encode("utf-8")
			#if iconimage == 'http://www.ntv.mx/res/content/tv/ntvlogo.png':
				#iconimage= recordings.imageUrlicon(BASE,channel,'.png')
			iconimage= recordings.getIcon(name,channel)
			if ADDON.getSetting('enable_record')=='true':
				THETIME=time.strptime(endTime, '%Y-%m-%d %H:%M:%S')
				endDate  =  datetime(*THETIME[:6])+ timedelta(seconds = offset)
			else:
				endDate  = ''
			if ADDON.getSetting('tvguide')=='true':
				if not endDate  == '' and recordings.getRecordingsActive(endDate,endDate): #################################################################
					name='%s - [COLOR red]%s[/COLOR]'%(name,whatsup)
				else:
					name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)				
			addDir(name,'url',200,iconimage,channel,'',description,now,endDate,whatsup)
			setView('movies', 'channels-view')       
			#endTime      =  field['time_to']
			#name         =  field['name'].encode("utf-8")
			#channel      =  field['id']
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

			
			#if ADDON.getSetting('DebugRecording')=='true':
			#	name='%s (%s) - [COLOR yellow]%s[/COLOR]'%(str(channel),name,whatsup)
			#else:
			#	name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
			#newiconurl= recordings.imageUrlicon(imageUrl,channel,'.png')
			#addDir(name,'url',200,newiconurl,channel,'',description,now,endDate,whatsup)
		#setView('movies', 'channels-view')         
			
def MyChannels():
	cat='-2'
	net.set_cookies(cookie_jar)
	now= datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
	url='&mwAction=category&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	data = json.loads(link)
	channels=data['contents']
	from operator import itemgetter
	#Sort channels by name or id/cat
	if ADDON.getSetting('SortAlphabetically')=='true':
		channels = sorted(channels, key=itemgetter('id'))
	else:
		channels = sorted(channels, key=itemgetter('name'))
	AllMyChannels=[]
	
	for field in channels:
		name         =  field['name'].encode("utf-8")
		channel      =  field['id']
		displaychannelnumber = (name + ' (' +channel+'):\n' )
		AllMyChannels.append(displaychannelnumber)
	return AllMyChannels
		

def GENRE(name,cat):
    _GENRE_=name.lower()
    #now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    now= datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    ## 3.4.6 now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    
    net.set_cookies(cookie_jar)
    url='&mwAction=category&xbmc=2&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
    link = net.http_GET(site+url, headers={'User-Agent' : UA }).content
    data = json.loads(link)
    channels=data['contents']
    # Krogsbell 2014-09-18 3 lines
    from operator import itemgetter
    #Sort channels by name!
    if ADDON.getSetting('SortAlphabetically')=='true':
         channels = sorted(channels, key=itemgetter('name'))
    uniques=[]
    
    offset= int(data['offset'])
    for field in channels:
        genre      =  field['genre']
        endTime      =  field['time_to']
        name         =  field['name'].encode("utf-8")
        channel      =  field['id']
        whatsup      =  field['whatsup'].encode("utf-8")
        displaychannelnumber = (name + ' (' +channel+'):\n' )
	description  =  (displaychannelnumber + field['descr']).encode("utf-8")
        #description  =  field['descr'].encode("utf-8")
        r=re.compile("(.+?)-(.+?)-(.+?) (.+?):(.+?):(.+?)")
        matchend     =  r.search(endTime)
        endyear      =  matchend.group(1)
        endmonth     =  matchend.group(2)
        endday       =  matchend.group(3)
        endhour      =  matchend.group(4)
        endminute    =  matchend.group(5)

        endDate  =  datetime(int(endyear),int(endmonth),int(endday),int(endhour),int(endminute)) + timedelta(seconds = offset)

        
        if ADDON.getSetting('tvguide')=='true':
		if not endDate  == '' and recordings.getRecordingsActive(endDate,endDate): #################################################################
			name='%s - [COLOR red]%s[/COLOR]'%(name,whatsup)
		else:
			name='%s - [COLOR yellow]%s[/COLOR]'%(name,whatsup)
        if genre.lower() == _GENRE_:
            #newiconurl= recordings.imageUrlicon(imageUrl,channel,'.png')
            newiconurl= recordings.getIcon(name,channel)
            addDir(name,'url',200,newiconurl,channel,'',description,now,endDate,whatsup)
    setView('movies', 'channels-view')         
            
def MYACCOUNT():
    username    =ADDON.getSetting('user')
    addDir('Email: %s' % username,'url',14,'','','','')
    addDir('Past settings.xml','url',15,'','','','')
    #addDir('Buy Subscription','url',11,'','','','')
    addDir('My Subscriptions','url',9,'','','','')
    addDir('Past Orders','url',10,'','','','')
        
def SUBS():
    net.set_cookies(cookie_jar)
    link = net.http_GET(definition.getBASEURL() +'/?' + recordings.referral() + 'c=1&a=18', headers={'User-Agent' : UA}).content
    data = json.loads(link)
    body = data['body']
    for field in body:
        title= field['title']
        platform= field['platforms'].encode("utf-8")
        status= field['status'].encode("utf-8")
        time_left= field['time_left'].encode("utf-8")
        name='%s-%s-(%s)[COLOR yellow] %s[/COLOR] '%(title,platform,time_left,status)
        addDir_STOP(name,'url','','','','')
    setView('movies', 'main-view') 
    
def ORDERS():
    net.set_cookies(cookie_jar)
    link = net.http_GET(definition.getBASEURL() +'/?' + recordings.referral() + 'c=1&a=19', headers={'User-Agent' : UA}).content.encode('ascii', 'ignore')
    data = json.loads(link)
    body = data['body']
    for field in body:
        id= field['id'].encode("utf-8")
        price_total= field['price_total'].encode("utf-8")
        created= field['created'].encode("utf-8")
        status= field['status'].encode("utf-8")
        updated= field['updated'].encode("utf-8")
        name='%s-(%s)[COLOR yellow] %s-(%s)[/COLOR] '%(price_total, created, status, updated)
        addDir_STOP(name,'url','','','','')
    setView('movies', 'main-view') 

def Search(name):
		search_entered = ''
		keyboard = xbmc.Keyboard(search_entered, 'Please Enter '+str(name))
		keyboard.doModal()
		if keyboard.isConfirmed():
			search_entered = keyboard.getText()
			if search_entered == None:
				return False          
		return search_entered  
		
def Numeric(name):
		dialog = xbmcgui.Dialog()
		keyboard=dialog.numeric(0, 'Please Enter '+str(name))
		return keyboard  

def ADD_FAV(cat):
	net.set_cookies(cookie_jar)
	url='&mwAction=favorite&mwData={"id":"%s","type":"tv"}'%cat
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	#print 'NTV Krogsbell default.py ADD_FAV site+url= %s, headers={User-Agent : %s}' % (str(repr(site+url)),str(repr(UA)))
	#print 'NTV Krogsbell default.py ADD_FAV link= %s' % str(repr(link))
	return

def TVGUIDE(name,cat):
	try:
		name.split(' -')[0]
	except:
		pass
	net.set_cookies(cookie_jar)
	#now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
	## 3.4.7
    	now= datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    	## 3.4.6 now= datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S').replace(' ','%20')
    	url='&mwAction=content&xbmc=1&mwData={"id":"%s","time":"%s","type":"tv"}'%(cat,now)
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	data = json.loads(link)
	offset= int(data['offset'])
	guide=data['guide']
	channelname= recordings.ChannelName(cat)
	displaychannelnumber = (channelname + ' (' +cat+'):\n' ).encode("utf-8")
	newiconurl= recordings.getIcon(channelname,cat) 
	for field in guide:
		r=re.compile("(.+?)-(.+?)-(.+?) (.+?):(.+?):(.+?)")
		startTime= field['time']
		endTime= field['time_to']
		name= field['name'].encode("utf-8")
		recordname= field['name'].encode("utf-8")
		description= (channelname + ' (' +cat+'):\n' + field['description']).encode("utf-8")
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
		startDate= datetime(int(year),int(month),int(day),int(hour),int(minute)) + timedelta(seconds = offset)
		endDate= datetime(int(endyear),int(endmonth),int(endday),int(endhour),int(endminute)) + timedelta(seconds = offset)
		time='[COLOR yellow](%s) - [/COLOR]'%(startDate.strftime('%H:%M'))
		#utils.log('default.py TVGUIDE',repr(recordings.getRecordingsActive(startDate,endDate)))
		activerecording= recordings.getRecordingsActive(startDate,endDate)
		#if not activerecording == []:
		#	utils.log('activerecording',repr(activerecording[0]))
		if activerecording == []: 
			addDir(time+name,'url',200,newiconurl,cat,startDate,description,startDate,endDate,recordname)
		elif recordings.latin1_to_ascii(name) in activerecording[0]: 
			addDir(time+'[COLOR green]' + name + '[/COLOR]','url',200,newiconurl,cat,startDate,description,startDate,endDate,recordname)
		else:
			addDir(time+'[COLOR red]' + name + '[/COLOR]','url',200,newiconurl,cat,startDate,description,startDate,endDate,recordname)
	setView('movies', 'tvguide-view')

def RecordingsPlanned():
	import recordings
	import utils
	offset=0
	c = recordings.getConnection().cursor()
	#c.execute("SELECT * FROM recordings_adc WHERE end=?", [endDate])
	# SELECT * FROM COMPANY WHERE AGE >= 25 OR SALARY >= 65000;
	## 3.4.6cutoffdate = (datetime.datetime.today() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
	cutoffdate = (datetime.today() - timedelta(days = 1)).strftime('%Y-%m-%d')
	# 5) Retrieve all IDs of entries between that are older than 1 day and 12 hrs
	#c.execute("SELECT {idf} FROM {tn} WHERE DATE('now') - {dc} >= 1 AND DATE('now') - {tc} >= 12".\
	#    format(idf=id_field, tn=table_name, dc=date_col, tc=time_col))
	#all_1day12hrs_entries = c.fetchall()
	#c.execute("SELECT * FROM recordings_adc WHERE (DATETIME('now') - end) = 0 ")
	#all_1day12hrs_entries = c.fetchall()
	#print 'default.py: cutoffdate= %s' % repr(cutoffdate)
	#print 'default.py: SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE start > %s' % cutoffdate
	#c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE start > %s  AND name NOT CONTAINS 'Recursive' " % cutoffdate )
	c.execute("SELECT * FROM recordings_adc WHERE end>? AND name NOT LIKE '%Recursive:%'", [cutoffdate])
	#c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc")
	recordingsC = c.fetchall()
	from operator import itemgetter
	
	#Sort Planned Recordings by start date!
	recordingsD = sorted(recordingsC, key=itemgetter(2))
	# print 'default.py: RecordingsPlanned recordingsD= %s' % repr(recordingsD)
	for index in range(0, len(recordingsD)):
		if not 'Recursive:' in recordingsD[index][1]:
			showRecording(recordingsD,index)
	# Put recursive recordings last
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc WHERE name LIKE '%Recursive:%'")
	recordingsC = c.fetchall()
	recordingsD = sorted(recordingsC, key=itemgetter(1))  # Sort by channel
	recordingsE = sorted(recordingsD, key=itemgetter(6))  # Sort by channel
	# recordingsE = sorted(recordingsC, key=itemgetter(2), reverse=True) # sort by last modified
	# print 'default.py: RecordingsPlanned recordingsE= %s' % repr(recordingsE)
	for index in range(0, len(recordingsE)):
		if 'Recursive:' in recordingsE[index][1]:
			showRecording(recordingsE,index)
	setView('movies', 'recordingsplanned-view')
	try: c.commit()
	except:
		pass
		#print 'recordings.py commit failed!'
	c.close()

def RecordingsPlannedDebug():
	import recordings
	import utils
	offset=0
	c = recordings.getConnection().cursor()
	c.execute("SELECT DISTINCT cat, name, start, end, alarmname, description, playchannel FROM recordings_adc")
	recordingsC = c.fetchall()
	from operator import itemgetter
	
	#Sort Planned Recordings by start date!
	recordingsD = sorted(recordingsC, key=itemgetter(2))
	#RecordingsPlannedDebugIcons(recordingsD)
	for index in range(0, len(recordingsD)):
		if not 'Recursive:' in recordingsD[index][1]:
			showRecordingDebug(recordingsD,index)
	# Put recursive recordings last
	recordingsD = sorted(recordingsC, key=itemgetter(1))  # Sort by channel
	recordingsE = sorted(recordingsD, key=itemgetter(6))  # Sort by channel
	# recordingsE = sorted(recordingsC, key=itemgetter(2), reverse=True) # sort by last modified
	for index in range(0, len(recordingsE)):
		if 'Recursive:' in recordingsE[index][1]:
			showRecordingDebug(recordingsE,index)
	setView('movies', 'recordingsplanned-view')
	try: c.commit()
	except:
		pass
		#print 'recordings.py commit failed!'
	c.close()
	
def RecordingsPlannedDebugIcons(recordingsD):
	import recordings
	import utils

	for index in range(0, 10):
		showRecordingDebug(recordingsD,str(index))
		#print 'showRecordingDebug index= %s' % str(index)
	setView('movies', 'recordingsplanned-view')

def showRecording(recordingsC,index):
		import recordings
		now = recordings.parseDate(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
		ignoreRecording = False
	#for index in range(0, len(recordingsC)): 
		cat         = recordingsC[index][0]
		#name        = recordings.latin1_to_ascii (recordingsC[index][1].encode("utf-8"))
		name        = recordingsC[index][1]
		startDate   = recordings.parseDate(recordingsC[index][2])
		endDate     = recordings.parseDate(recordingsC[index][3])
		alarmname   = recordingsC[index][4]
		description = recordingsC[index][5]
		playchannel = recordingsC[index][6]
		try:
			#timeShowStart= str(startDate).split(':')[0] + ":" + str(startDate).split(':')[1]
			timeShowStart=str(startDate).split(' ')[0] + ' (' + (str(startDate).split(' ')[1]).split(':')[0] + ":" + (str(startDate).split(' ')[1]).split(':')[1] 
		except:
			pass
			#print 'default.py: ERROR in startDate= %s' % repr(startDate)
			ignoreRecording = True
			startDate = now
			timeShowStart = now
		try:
			timeShowEnd=(str(endDate).split(' ')[1]).split(':')[0] + ":" + (str(endDate).split(' ')[1]).split(':')[1] +')'
		except:
			pass
			#print 'default.py: ERROR in endDate= %s' % repr(endDate)
			ignoreRecording = True
			endDate = now
			timeShowEnd = now
		nowY = now.strftime('%Y-')
		nowYM = now.strftime('%Y-%m-')
		nowYMD = now.strftime('%Y-%m-%d ')
		time='[COLOR yellow]%s - %s - [/COLOR]'%(timeShowStart.replace(nowYMD,'').replace(nowYM,'').replace(nowY,''),timeShowEnd)
		timeOld='%s - %s - '%(timeShowStart.replace(nowYMD,'').replace(nowYM,'').replace(nowY,''),timeShowEnd)
		displaychannelnumber = playchannel + ' (' +cat+ '):\n'
		displaychannelnumberold = playchannel + '(' +cat+ '):'
		displaydescription = description.replace(displaychannelnumber,'').replace(displaychannelnumberold,'').lstrip()
		if ('Recursive:' in name):
			timeRecursive = '%s - '%(timeShowStart)
			#nameRecursive = str(name.replace(':','xxx',1))
			#nameRecursive = str(playchannel) + ' - ' + str(nameRecursive.split('xxx')[1])
			nameRecursive = str(name.replace('Recursive:','',1))
			nameRecursive = str(playchannel) + ' - ' + nameRecursive
			if len(displaydescription) > 0:
				descriptionstrip =  (str(displaydescription).replace('[COLOR green]Example description of channel to record: [/COLOR]','')).lstrip()
				description = '[COLOR green]Example description of channel to record: [/COLOR]\n' + descriptionstrip
		recordname=name
		#now = recordings.parseDate(now)
		now = recordings.parseDate(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
		startDate = recordings.parseDate(startDate)
		endDate = recordings.parseDate(endDate)
		#print 'endDateTest =  endDate= %s + datetime.timedelta(days = 1)' % repr(endDate)
		endDateTest =  endDate + timedelta(days = 1) # Number of previous days to show in view
		#print 'endDateTest = %s  endDate + datetime.timedelta(days = 1)' % repr(endDateTest)
		#newiconurl= recordings.imageUrlicon(imageUrl,cat,'.png')
		newiconurl= recordings.getIcon(name,cat)
		displaydescription = displaychannelnumber + description.replace(displaychannelnumber,'').replace(displaychannelnumberold,'').lstrip().replace('. ','.\n')
		if (not ignoreRecording and ((recordings.parseDate(endDateTest) > recordings.parseDate(datetime.today().strftime('%Y-%m-%d'))) or ('Recursive:' in name))):
			if (startDate < now and now < endDate) and (not ('Recursive:' in name)):
				#http://www.dk4.dk/templates/dk4/images/dk4Logo.png
				#addDir(time+'[COLOR red]'+name+'[/COLOR]','url',200,'http://www.dk4.dk/templates/dk4/images/dk4Logo.png',cat,startDate,playchannel + ': ' + description,startDate,endDate,recordname)
				addDir(time+'[COLOR red]'+name+'[/COLOR]','url',200,newiconurl,cat,startDate,displaydescription,startDate,endDate,recordname)
			else:
				if (endDate < now) or ('Recursive:' in name):
					if ('Recursive:' in name):
						addDir("Recursive " + str(cat) + ": " + nameRecursive,'url',200,newiconurl,cat,startDate,displaydescription,startDate,endDate,recordname)
					else:
						addDir(timeOld+name,'url',200,newiconurl,cat,startDate,displaydescription,startDate,endDate,recordname)
				else:
					addDir(time+name,'url',200,newiconurl,cat,startDate,displaydescription,startDate,endDate,recordname)
			#setView('movies', 'recordingsplanned-view')

def showRecordingDebug(recordingsC,index):
		import recordings
		now = recordings.parseDate(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

	#for index in range(0, len(recordingsC)): 
		cat         = recordingsC[index][0]
		name        = recordingsC[index][1].encode("utf-8")
		startDate   = recordingsC[index][2]
		endDate     = recordingsC[index][3]
		alarmname   = recordingsC[index][4]
		description = recordingsC[index][5]
		playchannel = recordingsC[index][6]
		#cat            = str(index)
		#name        = str(index)
		#startDate   = now
		#endDate     = now
		#alarmname   = str(index)
		#description = str(index)
		#playchannel = str(index)		#description = '\nind=%s \ncat=%s \nnam=%s \nsta=%s \nend=%s \nala=%s \npla=%s' %(repr(index),repr(cat),repr(name),repr(startDate),repr(endDate),repr(alarmname),repr(playchannel))
		#print str(index)
		#print imageUrl+cat+'.png'
		#newiconurl= recordings.imageUrlicon(imageUrl,cat,'.png')
		newiconurl= recordings.getIcon(name,cat)
		try:
			#print repr(OPEN_URL(imageUrl+cat+'.png')) 
			addDir('[COLOR red]'+name+'[/COLOR]','url',200,newiconurl,cat,startDate,playchannel + ': '  + repr(startDate) + ' - ' + repr(startDate) + ' # ' + description,startDate,endDate,name)
		except:
			pass
		#setView('movies', 'recordingsplanned-view')

def PLAY_STREAM(name,url,iconimage,cat):
	#print 'default.py PLAY_STREAM(name,url,iconimage,cat) %s %s %s %s' % (repr(name), repr(url), repr(iconimage), repr(cat))
	LastPlayedStreamname = ADDON.getSetting('LastPlayedStreamname')
	LastPlayedStreamurl = ADDON.getSetting('LastPlayedStreamurl')
	LastPlayedStreamiconimage = ADDON.getSetting('LastPlayedStreamiconimage')
	LastPlayedStreamcat = ADDON.getSetting('LastPlayedStreamcat')
	if cat != 0:
		ADDON.setSetting('LastPlayedStreamname', name)
		ADDON.setSetting('LastPlayedStreamurl', url)
		ADDON.setSetting('LastPlayedStreamiconimage', iconimage)
		ADDON.setSetting('LastPlayedStreamcat', cat)
		PlayDefaultStream = False
	else:
		name = LastPlayedStreamname
		url = LastPlayedStreamurl
		iconimage = LastPlayedStreamiconimage
		cat = LastPlayedStreamcat
		PlayDefaultStream = True
	#startD = recordings.parseDate(datetime.now())
	startD = recordings.parseDate(datetime.now())
	endD = startD
	utils.log('default.py','PlayDefaultStream= %s' % repr(PlayDefaultStream))
	if PlayDefaultStream:
		recordingsActive = []
	else:
		recordingsActive = []
		recordingsActiveAll = recordings.getRecordingsActive(startD,endD)
		utils.log('default.py','recordingsActiveAll= %s' % repr(recordingsActiveAll))
		for x in recordingsActiveAll:
			utils.log('default.py','x= %s' % repr(x))
			if not '[COLOR orange]' in x:
				utils.log('default.py','recordingsActive= %s' % repr(recordingsActive))
				recordingsActive.append(x)
				utils.log('default.py','recordingsActive= %s' % repr(recordingsActive))
	if (recordingsActive != []) and locking.isAnyRecordLocked():
		utils.notification('OVERLAPPING Recordings NOT allowed: %s' % str(recordingsActive))
		#if (repr(recordingsActive) != "[]"):
		lockcause = repr(locking.RecordsLocked())
		#else:
		#	lockcause = repr(recordingsActive)
		dialog = xbmcgui.Dialog()
		if dialog.yesno(ADDON.getAddonInfo('name'), "[COLOR red]Stop recording?[/COLOR]", repr(recordingsActive), "What Do You Want To Do","[COLOR red]Stop recording[/COLOR]","[COLOR green]Ignore[/COLOR]"):
			return
	#print 'default.py: locking.recordUnlockAll()'
	locking.recordUnlockAll()
	# Test locking and unlock
	testX = 'TEST'
	locking.recordLock(testX)
	if locking.isRecordLocked(testX):
		locking.recordUnlock(testX)
	else:
		recordingLock = os.path.join(ADDON.getAddonInfo('path'),'rtmpdump', 'recordingLock') +  testX + '.txt'
		utils.notification('Record Locking fails at %s' % str(recordingLock))
	try:
		_name=name.split(' -')[0].replace('[/COLOR]','').replace('[COLOR yellow]','')
		playername=name.split('- ')[1].replace('[/COLOR]','').replace('[COLOR yellow]','')
	except:
		_name=name.replace('[/COLOR]','')
		playername=name.replace('[/COLOR]','')
	net.set_cookies(cookie_jar)
	url = '&mwAction=content&xbmc=1&mwData={"id":%s,"type":"tv"}'%cat
	link = net.http_GET(site+url, headers={'User-Agent' : UA}).content
	if '"allown":false' in link:
		try:
			match=re.compile('"message":"(.+?)"').findall(link)
			dialog = xbmcgui.Dialog()
			dialog.ok(ADDON.getAddonInfo('name'), '', match[0].replace('\/','/'))
		except:
			dialog = xbmcgui.Dialog()
			dialog.ok(ADDON.getAddonInfo('name'), '', 'Please Sign Up To Watch The Streams')
	else:
		match=re.compile('"src":"(.+?)","type":"rtmp"').findall(link)
		if match:
			url=match[0].replace('\/','/')
			# NOT in 3.4.1 rtmp=match[0].replace('\/','/')
			# NOT in 3.4.1 playpath=rtmp.split('live/')[1]
			# NOT in 3.4.1 app='live?'+rtmp.split('?')[1]
			# NOT in 3.4.1 url='%s swfUrl=http://ntv.mx/inc/strobe/StrobeMediaPlayback.swf app=%s playPath=%s pageUrl=http://ntv.mx/?c=2&a=0&p=50 timeout=10'%(rtmp,app,playpath)
		else:
			match=re.compile('"src":"(.+?)","type":"hls"').findall(link)
			hls=match[0].replace('\/','/')
			url=hls
		liz=xbmcgui.ListItem(playername, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
		liz.setInfo( type="Video", infoLabels={ "Title": playername} )
		liz.setProperty("IsPlayable","true")
		liz.setPath(url)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

def EXIT():
	recordings.backupSetupxml()
	if locking.isAnyRecordLocked():
		locking.recordUnlockAll()
	if locking.isAnyScanLocked():
		locking.scanUnlockAll()
	recordings.backupDataBase()
	recordings.stopAllRecordings()
	xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
	xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
        
def Record(recordname, uri, playpath,app):
	script   = os.path.join(ADDON.getAddonInfo('path'), 'recorduri.py')
	nameAlarm = 'record-dr-bonanza-video' + recordname
	try:
		if playpath == None:
			print 'No playpath'
		else:
			uri = uri + ' playpath=' + playpath
			print 'With playpath: uri= %s' % uri
	except:
		pass
	try:
		if app == None:
			print 'No app'
		else:
			uri = uri + ' app=' + app
			print 'With app: uri= %s' % uri
	except:
		pass
	cmd = 'AlarmClock(%s,RunScript(%s,%s,%s),00:00:00,silent)' % (recordname, script, uri,recordname)
	print 'default.py: cmd= %s' % cmd
	xbmc.executebuiltin(cmd)  # Active
	
def Recordffmpeg(recordname, uri, playpath,app):
	script   = os.path.join(ADDON.getAddonInfo('path'), 'recorduriffmpeg.py')
	nameAlarm = 'record-drnu-video'  + recordname
	try:
		if playpath == None:
			print 'No playpath'
		else:
			uri = uri + ' playpath=' + playpath
			print 'With playpath: uri= %s' % uri
	except:
		pass
	try:
		if app == None:
			print 'No app'
		else:
			uri = uri + ' app=' + app
			print 'With app: uri= %s' % uri
	except:
		pass
	cmd = 'AlarmClock(%s,RunScript(%s,%s,%s),00:00:00,silent)' % (recordname, script, uri,recordname)
	print 'default.py: cmd= %s' % cmd
	xbmc.executebuiltin(cmd)  # Active
def scheduleRecording(cat, startDate, endDate, recordname, description):

    recordings.add(cat, startDate, endDate, recordname, description)

def delRecording(cat, startDate, endDate, recordname):
    import recordings
    recordings.delRecordingPlanned(cat, startDate, endDate, recordname)
    
def modifyRecording(cat, startDate, endDate, recordname, description):
    import recordings
    recordings.modifyRecordingPlanned(cat, startDate, endDate, recordname, description)

def DOWNLOADS():
	import glob
	path = recordDisplayPath

	files =  glob.glob(os.path.join(path, '*'))
	#print 'DOWNLOADS: files= %s' % repr(files)
	files1 = sorted(files, reverse=False)
	for infile in files1:
		if os.path.isdir(infile):
			name = infile.replace(recordPath,'')
			liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			liz.setInfo( type="Folder", infoLabels={ "Title": str(name)})
			liz.setProperty("IsPlayable","false")
			contextMenu = []
			contextMenu.append(('Delete Folder (if empty)', 'XBMC.RunPlugin(%s?mode=103&url=%s)'% (sys.argv[0], infile)))
			liz.addContextMenuItems(contextMenu,replaceItems=True)
			xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url=infile,listitem = liz, isFolder = True)
		else:
			if not infile[-4:].lower()=='.zip' and not infile[-4:].lower()=='.txt':
				name = infile.replace(recordPath,'').replace('.flv','')
				liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage="DefaultVideo.png")
				liz.setInfo( type="Video", infoLabels={ "Title": str(name)})
				liz.setProperty("IsPlayable","true")
				contextMenu = []
				contextMenu.append(('Delete', 'XBMC.RunPlugin(%s?mode=102&url=%s)'% (sys.argv[0], infile)))
				liz.addContextMenuItems(contextMenu,replaceItems=True)
				xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url=infile,listitem = liz, isFolder = False)
	setView('movies', 'main-view')

def DataBases():
	path = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	files =  glob.glob(os.path.join(path, '*'))
	#print 'DOWNLOADS: files= %s' % repr(files)
	files1 = sorted(files, reverse=True)
	#print 'DOWNLOADS: files1= %s' % repr(files1)
	index = 0
	for infile in files1:
		if index < 50:
			index += 1
			try:
				#print infile
				#print infile[-3:]
				#print infile[-3:].lower()
				if infile[-3:].lower()=='.db':
					name = infile.replace(path,'').replace('.db','')
					liz=xbmcgui.ListItem(name, iconImage="DefaultFile.png", thumbnailImage="DefaultFile.png")
					liz.setInfo( type="File", infoLabels={ "Title": str(name)})
					liz.setProperty("IsPlayable","false")
					contextMenu = []
					activeDB = recordings.RECORDS_DB.split('.')[0]
					#print activeDB
					if not name == activeDB: 
						contextMenu.append(('Restore Backup', 'XBMC.RunPlugin(%s?mode=105&url=%s)'% (sys.argv[0], infile)))
						contextMenu.append(('Delete', 'XBMC.RunPlugin(%s?mode=102&url=%s)'% (sys.argv[0], infile)))
						liz.addContextMenuItems(contextMenu,replaceItems=True)
						xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url=infile,listitem = liz, isFolder = False)
			except:
				pass
				#print 'Failed: %s' % repr(infile)
	setView('movies', 'main-view')

def SetupxmlFiles():
	path = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	files =  glob.glob(os.path.join(path, '*'))
	defaultfile = os.path.join(path, recordings.SETTINGSXML)
	#print 'DOWNLOADS: files= %s' % repr(files)
	files1 = sorted(files, reverse=True)
	#print 'DOWNLOADS: files1= %s' % repr(files1)
	activeDB = recordings.SETTINGSXML.split('.')[0]+ ' - ' + utils.username(defaultfile) 
	index = 0
	for infile in files1:
		if index < 50:
			index += 1
			try:
				#print infile
				#print infile[-3:]
				#print infile[-3:].lower()
				if infile[-4:].lower()=='.xml':
					mail = utils.username(infile)
					name = infile.replace(path,'').replace('.xml','') + ' - ' + mail
					liz=xbmcgui.ListItem(name, iconImage="DefaultFile.png", thumbnailImage="DefaultFile.png")
					liz.setInfo( type="File", infoLabels={ "Title": str(name)})
					liz.setProperty("IsPlayable","false")
					contextMenu = []
					if not name == activeDB and '@' in mail: 
						contextMenu.append(('Restore settings.xml', 'XBMC.RunPlugin(%s?mode=106&url=%s)'% (sys.argv[0], infile)))
						contextMenu.append(('Delete', 'XBMC.RunPlugin(%s?mode=102&url=%s)'% (sys.argv[0], infile)))
						liz.addContextMenuItems(contextMenu,replaceItems=True)
						xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url=infile,listitem = liz, isFolder = False)
			except:
				pass
				#print 'Failed: %s' % repr(infile)
	setView('movies', 'main-view')


def deleteFile(file):
	tries    = 0
	maxTries = 10
	while os.path.exists(file) and tries < maxTries:
		try:
			print 'removeFile: %s' % file  # Put in LOG
			os.remove(file)
			break
		except:
			print 'Failed #= %d' % tries  # Put in LOG
			xbmc.sleep(500)
			tries = tries + 1

def deleteDir(file):
	tries    = 0
	maxTries = 10
	while os.path.exists(file) and tries < maxTries:
		try:
			print 'removeDir: %s' % file  # Put in LOG
			os.rmdir(file)
			break
		except:
			print 'Failed #= %d' % tries  # Put in LOG
			xbmc.sleep(500)
			tries = tries + 1
			
def get_params():
		param=[]
		#print 'default.py get_params= %s' % repr(sys.argv)
		paramstring=sys.argv[2]
		if len(paramstring)>=2:
				params=sys.argv[2]
				cleanedparams=params.replace('?','')
				if (params[len(params)-1]=='/'):
						params=params[0:len(params)-2]
				pairsofparams=cleanedparams.split('&')
				param={}
				for i in range(len(pairsofparams)):
						splitparams={}
						splitparams=pairsofparams[i].split('=')
						if (len(splitparams))==2:
								param[splitparams[0]]=splitparams[1]
								
		return param

def addDir(name,url,mode,iconimage,cat,date,description,startDate='',endDate='',recordname=''):
		u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&cat="+urllib.quote_plus(cat)+"&date="+urllib.quote_plus(str(date))+"&description="+urllib.quote_plus(recordings.latin1_to_ascii(description))+"&startDate="+urllib.quote_plus(str(startDate))+"&endDate="+urllib.quote_plus(str(endDate))+"&recordname="+urllib.quote_plus(recordings.latin1_to_ascii(recordname))  ##### Dates added urllib.quote_plus() Krogsbell 2016-03-11
		################ Suggested code to avoid: WARNING: CreateLoader - unsupported protocol(plugin) in plugin://plugin.video.wozboxntv/
		#url="http://www.sample-videos.com/video/mp4/480/big_buck_bunny_480p_10mb.mp4"

		#URI=url
		#item = xbmcgui.ListItem(title, thumbnailImage=image)

		#item.setInfo(type='video', infoLabels={'genre': 'genre', 'plot': 'desc' })
		#item.setProperty('IsPlayable', 'true')

		#xbmcplugin.addDirectoryItem(pluginhandle, URI, item, False)
		################
		ok=True
		liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
		liz.setInfo( type="Video", infoLabels={ "Title": name,"Plot":description} )
		try: # Find the mode on entry = the actual view '3' = Palnned Recordings
			view= sys.argv[2].split('mode=',1)[1].split('&')[0]
			#print view
		except:
			pass
			view= '0'
		TVguide= utils.TVguide()
		activetvguide= ADDON.getSetting('activetvguide')
		menu=[]
		#if ADDON.getSetting('enable_record')=='true':
		#	menu.append(('[COLOR red][B]RECORD...[/B][/COLOR]','XBMC.RunPlugin(%s?mode=2001&url=url&cat=%s&startDate=%s&endDate=%s&recordname=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)))))
		if mode==200 or mode==12:
			menu.append(('[COLOR yellow][B]TV Guide[/B][/COLOR]','XBMC.Container.Update(%s?name=None&mode=4&url=None&iconimage=None&cat=%s)'% (sys.argv[0],cat)))
			menu.append(('[COLOR red][B]Grab from %s[/B][/COLOR]'% (activetvguide),'XBMC.Container.Update(%s?name=None&mode=3000&url=None&iconimage=None&cat=%s)'% (sys.argv[0],cat)))
			if ADDON.getSetting('enable_record')=='true':
				if not name[0:9] =='Recursive':
					menu.append(('[COLOR red][B]RECORD[/B][/COLOR]','XBMC.RunPlugin(%s?mode=2001&url=url&cat=%s&startDate=%s&endDate=%s&recordname=%s&description=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)),urllib.quote_plus(recordings.latin1_to_ascii(description)))))
					menu.append(('[COLOR red][B]RECORD RECURSIVE[/B][/COLOR]','XBMC.RunPlugin(%s?mode=2005&url=url&cat=%s&startDate=%s&endDate=%s&recordname=%s&description=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)),urllib.quote_plus(recordings.latin1_to_ascii(description)))))
				if view == '3':
					menu.append(('[COLOR red][B]MODIFY RECORD[/B][/COLOR]','XBMC.RunPlugin(%s?mode=2003&url=url&cat=%s&startDate=%s&endDate=%s&recordname=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)))))
					menu.append(('[COLOR orange][B]DISABLE RECORD[/B][/COLOR]','XBMC.RunPlugin(%s?mode=2006&url=url&cat=%s&startDate=%s&endDate=%s&recordname=%s&description=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)),urllib.quote_plus(recordings.latin1_to_ascii(description)))))
					menu.append(('[COLOR red][B]DELETE RECORD[/B][/COLOR]','XBMC.RunPlugin(%s?mode=2002&url=url&cat=%s&startDate=%s&endDate=%s&recordname=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)))))
				if not view == '3':
					menu.append(('[COLOR red][B]Planned Recordings[/B][/COLOR]','XBMC.Container.Update(%s?name=None&mode=3&url=None&iconimage=None&cat=%s)'% (sys.argv[0],cat)))
				if ADDON.getSetting('DebugRecording')=='true':
					menu.append(('[COLOR green][B]Planned Recordings Debug[/B][/COLOR]','XBMC.Container.Update(%s?name=None&mode=13&url=None&iconimage=None&cat=%s)'% (sys.argv[0],cat)))
				menu.append(('[COLOR green][B]Recorded[/B][/COLOR]','XBMC.Container.Update(%s?name=None&mode=6&url=None&iconimage=None&cat=%s)'% (sys.argv[0],cat)))
			menu.append(('[COLOR orange][B]Toggle NTV Favourites[/B][/COLOR]','XBMC.RunPlugin(%s?name=None&mode=7&url=None&iconimage=None&cat=%s)'% (sys.argv[0],cat)))
			#try:
			#	if name[0:9] =='Recursive' and not locking.isAnyRecordLocked():
			#		menu.append(('[COLOR orange][B]Refresh Recursive[/B][/COLOR]','XBMC.RunPlugin(%s?name=None&mode=2007&url=None&iconimage=None&cat=%s&startDate=%s&endDate=%s&recordname=%s&description=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)),urllib.quote_plus(recordings.latin1_to_ascii(description)))))
			#except:
			#	pass
			menu.append(('[COLOR orange][B]Refresh[/B][/COLOR]','XBMC.RunPlugin(%s?name=None&mode=2004&url=None&iconimage=None&cat=%s&startDate=%s&endDate=%s&recordname=%s&description=%s)'% (sys.argv[0],urllib.quote_plus(cat),startDate,endDate,urllib.quote_plus(recordings.latin1_to_ascii(recordname)),urllib.quote_plus(recordings.latin1_to_ascii(description)))))
			if mode==200: ### NEW in 3.3.9
				liz.setProperty("IsPlayable","true")
			liz.addContextMenuItems(items=menu, replaceItems=True)
			ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
		else:
			ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
		return ok
        

def addDir_STOP(name,url,iconimage,cat,date,description,startDate='',endDate='',recordname=''):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&cat="+urllib.quote_plus(cat)+"&date="+str(date)+"&description="+urllib.quote_plus(description)+"&startDate="+str(startDate)+"&endDate="+str(endDate)+"&recordname="+recordings.latin1_to_ascii(recordname)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"Premiered":date,"Plot":description} )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return ok
        
def SetUserAndPasswordNew():
    dialog = xbmcgui.Dialog()
    ##Dialog.radiolist(text, height=None, width=None, list_height=None, choices=[], **kwargs)
    ##choices – an iterable of (tag, item, status) tuples where status specifies the initial selected/unselected state of each entry; can be True or False, 1 or 0, "on" or "off" (True, 1 and "on" meaning selected), or any case variation of these two strings. No more than one entry should be set to True.
    choises = []
    choises.append('krogsbell@gmail.com')
    choises.append('krogsbell2015@gmail.com')
    choises.append('newmail')
    #[['krogsbell':'krogsbell@gmail.com':'True']:['krogsbell2015':'krogsbell2015@gmail.com':'False']:['New mail':'newmail':'False']]
    selected = dialog.select(ADDON.getAddonInfo('name') + ' - Select a previous login:', choises ) ####################
    if selected == 'newmail':
    	email=Search('Email')
    else:
    	email = choises[selected]
    #email=Search('Email')
    utils.log('default.py','email= %s' % repr(email))
    email = str(email)
    utils.log('default.py','str(email)= %s' % repr(email))
    if not email == "":
    	password=Search('Password')
    	if not email == "" and not password == "":
    		ADDON.setSetting('user',email)
    		ADDON.setSetting('pass',password)
    		AUTH()
    		utils.notification('[COLOR green]Email and password updated[/COLOR]')
    MYACCOUNT()
    
def SetUserAndPassword():
    email=Search('Email')
    utils.log('default.py','email= %s' % repr(email))
    email = str(email)
    utils.log('default.py','str(email)= %s' % repr(email))
    if not email == "":
    	password=Search('Password')
    	if not email == "" and not password == "":
    		ADDON.setSetting('user',email)
    		ADDON.setSetting('pass',password)
    		AUTH()
    		utils.notification('[COLOR green]Email and password updated[/COLOR]')
    MYACCOUNT()
 
#below tells plugin about the views                
def setView(content, viewType):
        # set content type so library shows more views and info
        if content:
                xbmcplugin.setContent(int(sys.argv[1]), content)
        if ADDON.getSetting('auto-view') == 'true':#<<<----see here if auto-view is enabled(true) 
                xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )#<<<-----then get the view type


params=get_params()
xbmc.log( ADDON.getAddonInfo('name') + ' default.py: params= %s' % str(repr(params)))

url=None
name=None
mode=None
iconimage=None
date=None
description=None
cat=None
startDate=None
endDate=None
record=None
uri=None
playpath=None
app=None

try:
	url=urllib.unquote_plus(params["url"])  # URL
except:
	pass
try:
	#utils.log('default.py','URI= %s' % repr(params["uri"]))
	uri=urllib.unquote_plus(params["uri"])  # URI
except:
	pass
try:
	playpath=urllib.unquote_plus(params["playpath"])  # playpath
except:
	pass
try:
	app=urllib.unquote_plus(params["app"])  # app
except:
	pass
try:
	name=urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage=urllib.unquote_plus(params["iconimage"])
except:
	pass
try:        
	mode=int(params["mode"])
except:
	pass
try:
	cat=urllib.unquote_plus(params["cat"])
except:
	pass
try:
	date=str(params["date"])
except:
	pass
try:
	description=urllib.unquote_plus(params["description"])
except:
	pass
try:
	startDate=str(params["startDate"])
except:
	pass
try:
	endDate=str(params["endDate"])
except:
	pass
try:
	recordname=urllib.unquote_plus(params["recordname"])
except:
	pass

#these are the modes which tells the plugin where to go
if mode==None or url==None or len(url)<1:
	try:
		CATEGORIES()
	except:
		pass
		utils.notification('[COLOR red]Error in showing Categories[/COLOR] - [COLOR green]Check your internet connection![/COLOR]')

elif mode==2:
	CHANNELS(name,cat)

elif mode==3:
	RecordingsPlanned()

elif mode==4:
	TVGUIDE(name,cat)

elif mode==5:
	GENRE(name,cat)

elif mode==6:
	ADDON.setSetting('record_display_path',recordPath)
	DOWNLOADS()

elif mode==7:
	ADD_FAV(cat)
	xbmc.executebuiltin("Container.Refresh")

elif mode==8:
    MYACCOUNT()

elif mode==9:
    SUBS()

elif mode==10:
    ORDERS()

elif mode==11:
    BUYSUBS()

elif mode==12:
    PAYSUBS(cat)
    
elif mode==13:
	RecordingsPlannedDebug()
	
elif mode==14:
	SetUserAndPassword()
	
elif mode==15:
	SetupxmlFiles()
	        
elif mode==102:
	#print 'deleteFile(url= %s)' % repr(url)
	deleteFile(url)
	xbmc.executebuiltin("Container.Refresh")
elif mode==103:
	#print 'deleteDir(url)= %s <-- %s' % (repr(url), repr(recordPath))
	deleteDir(url)
	xbmc.executebuiltin("Container.Refresh")
elif mode==104:
	#recordPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	#ADDON.setSetting('record_display_path',recordPath)
	DataBases()
	#xbmc.executebuiltin("Container.Refresh")
elif mode==105:
	#recordPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	#print 'restoreBackupFile(url)= %s' % (repr(url))
	recordings.restoreBackupDataBase(url)

elif mode==106:
	#recordPath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
	#print 'restoreBackupFile(url)= %s' % (repr(url))
	recordings.restoreSetupXml(url)

elif mode==200:
	PLAY_STREAM(name,url,iconimage,cat)

elif mode==2009:  # Record or play link from FTVguide or TV Guide
	if ADDON.getSetting('RecordFromTVguide')=='true':
		try:
			recordduration = int(ADDON.getSetting('RecordFromTVguideDurationMinutes'))
		except:
			pass
			recordduration = 120
		if recordduration < 10: recordduration = 120
		now= datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		startDate =  (datetime.today() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
		endDate = (datetime.today() + timedelta(minutes=recordduration)).strftime('%Y-%m-%d %H:%M:%S')
		print 'scheduleRecording(cat= %s, startDate= %s, endDate= %s, name= %s, url= %s)' % (cat, startDate, endDate, name, url)
		scheduleRecording(cat, startDate, endDate, name, url)
	else:
		PLAY_STREAM(name,url,iconimage,cat)
elif mode==2010:  # Record link from dr bonanza
	print 'Record(name= %s, uri= %s,playpath= %s, app= %s)' % (name, uri, playpath, app)
	if ADDON.getSetting('RecordFromTVguide')=='true':
		Record(name, uri, playpath, app)
elif mode==2011:  # Record link from drnu/filmon
	print 'Record(name= %s, uri= %s,playpath= %s, app= %s)' % (name, uri, playpath, app)
	if ADDON.getSetting('RecordFromTVguide')=='true':
		Recordffmpeg(name, uri, playpath, app)
elif mode==2001:
	if not ('Recursive' in recordname):
		scheduleRecording(cat, startDate, endDate, recordname, description)
	xbmc.executebuiltin("Container.Refresh")
elif mode==2002:
	delRecording(cat, startDate, endDate, recordname)
	xbmc.executebuiltin("Container.Refresh")
elif mode==2003:
	modifyRecording(cat, startDate, endDate, recordname, description)
	xbmc.executebuiltin("Container.Refresh")
elif mode==2004:
	xbmc.executebuiltin("Container.Refresh")

elif mode==2005:
	if not ('Recursive' in recordname):
		scheduleRecording(cat, startDate, endDate, 'Recursive:' + recordname, description)
	xbmc.executebuiltin("Container.Refresh")

elif mode==2006:
	if not ('[COLOR orange]' in recordname):
		delRecording(cat, startDate, endDate, recordname)
		scheduleRecording(cat, startDate, endDate, '*' + recordname, description)
	xbmc.executebuiltin("Container.Refresh")
elif mode==2007:
	import findrecursive
	if ('Recursive' in recordname):
		locking.scanUnlockAll()
		findrecursive.RecursiveRecordingsPlanned('NotAllFavorites')
	xbmc.executebuiltin("Container.Refresh")
elif mode==3000:
	import findtvguidenotifications
	findtvguidenotifications.findtvguidenotifications()
	utils.log('findtvguidenotifications.py','Ended')
	
xbmcplugin.endOfDirectory(int(sys.argv[1]))
