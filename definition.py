#!/usr/bin/python
# -*- coding: utf-8 -*-

# 0= NTV.mx, 1= WOZBOX www.wozboxtv.com, 2=www.myindian.tv, 3=www.wliptv.com
# Copy the addon folder to the name of the id to copy addon to, update addon.xml and add the jpg and png icons to be used with the addon then make a zip file and install from zip!

referral= 1           ##########################<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

import xbmcaddon,xbmc

if referral==0:
	ADDON = xbmcaddon.Addon(id='plugin.video.ntv')
	BASEURL = 'http://www.ntv.mx'
	REGISTRATION = 'http://ntv.mx/?r=Kodi&c=2&a=0&p=9'
	
elif referral==1:
	ADDON = xbmcaddon.Addon(id='plugin.video.wozboxntv')
	BASEURL = 'http://www.ntv.mx'
	REGISTRATION = 'wozboxtv.com/registration'
	
elif referral==2:
	ADDON = xbmcaddon.Addon(id='plugin.video.myindian')
	BASEURL = 'http://www.myindian.tv'
	REGISTRATION = 'http://www.myindian.tv'
	
elif referral==3:
	ADDON = xbmcaddon.Addon(id='plugin.video.wliptv')
	BASEURL = 'http://www.wliptv.com'
	REGISTRATION = 'http://www.wliptv.com'
	
else:
	ADDON = xbmcaddon.Addon(id='plugin.video.wozboxntv')
	BASEURL = 'http://www.ntv.mx'
	REGISTRATION = 'wozboxtv.com/registration'

ADDON.setSetting('my_referral_link',str(referral))
xbmc.log('definition.py in %s with referral= %s' % (ADDON.getAddonInfo('name'), str(referral)))

def getADDON():
	return ADDON

def getBASEURL():
	return BASEURL	
	
def getREGISTRATION():
	return REGISTRATION	
