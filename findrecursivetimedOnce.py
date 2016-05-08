#!/usr/bin/python
# -*- coding: utf-8 -*-
#print "findrecursivetimedOnce.py"
import xbmcplugin,xbmcgui,xbmcaddon,xbmc
import urllib,urllib2,sys,re,os
import datetime
import time
import utils
import net
from hashlib import md5  
import json
import recordings, glob
import findrecursive
import locking

#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
if not locking.isAnyRecordLocked(): 
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
	findrecursive.RecursiveRecordingsPlanned('Once')
	#xbmc.executebuiltin("Container.Refresh")

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

lockDescription = '*Stop Recording*.flv'
recordingLock = os.path.join(ADDON.getSetting('record_path'),lockDescription)
LockFiles = glob.glob(recordingLock)
#print 'findrecursivetimed.py: recordingLock= %s' % (repr(LockFiles))
# delete lock files
for file in LockFiles:
	#print 'findrecursivetimed.py: delete file= %s' %repr(file)
	deleteFile(file)
