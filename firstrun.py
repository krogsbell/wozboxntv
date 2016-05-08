#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
import net
import recordings,utils
from datetime import datetime, timedelta

utils.log('firstrun.py','Start')
net=net.Net()
#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
cookie_path = os.path.join(datapath, 'cookies')
cookie_jar = os.path.join(cookie_path, "ntv.lwp")
UA="NTV-XBMC-HLS-" + ADDON.getAddonInfo('version') 


from hashlib import md5    

def LOGIN():
	utils.log('firstrun.py','LOGIN')
	loginurl = definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=3&a=4'
	username =ADDON.getSetting('user')
	password =md5(ADDON.getSetting('pass')).hexdigest()

	data     = {'email': username,
											'psw2': password,
											'rmbme': 'on'}
	headers  = {'Host':definition.getBASEURL().replace('http://',''),
											'Origin':definition.getBASEURL(),
											'Referer':definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=3&a=0','User-Agent' : UA}
											
	html = net.http_POST(loginurl, data, headers).content
	#if os.path.exists(cookie_path) == False:
	#		os.makedirs(cookie_path)
	#net.save_cookies(cookie_jar)
	#ADDON.setSetting('firstrun','true')
        
#def EXIT():
#        xbmc.log('firstrun.py: EXIT')
#        xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
#        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
#            
#def AUTH():
#	xbmc.log('firstrun.py: AUTH')
#        try:
#            os.remove(cookie_jar)
#        except:
#            pass
        username =ADDON.getSetting('user')
        password =md5(ADDON.getSetting('pass')).hexdigest()
        url = definition.getBASEURL() + '/?' + recordings.referral() + 'c=3&a=4&email=%s&psw2=%s&rmbme=on'%(username,password)
        html = net.http_GET(url).content
        if 'success' in html and '@' in username:
		## 3.4.6  LOGIN()
		if os.path.exists(cookie_path) == False:
			os.makedirs(cookie_path)
		net.save_cookies(cookie_jar)
		ADDON.setSetting('ga_time',str(datetime.today()+ timedelta(hours=6)).split('.')[0])
		ADDON.setSetting('firstrun','true')
        else:
            dialog = xbmcgui.Dialog()
            winput=re.compile('"message":"(.+?)"').findall(html)
            if dialog.yesno(ADDON.getAddonInfo('name'), winput[0],'', 'Please Try Again'):
                SIGNIN()
            else:
                EXIT()
def EXIT():
        xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
            
countries=os.path.join(ADDON.getAddonInfo('path'), 'countries.json')

def OPEN_URL(url):
    req = urllib2.Request(url, headers={'User-Agent' : UA}) 
    con = urllib2.urlopen( req )
    link= con.read()
    return link
    
    
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
        
def GetCountryID():
        f   = open(countries, "r")
        a = f.read()
        f.close()
        match=re.compile('"id": (.+?),"name": "(.+?)","code_phone": (.+?)]').findall(a)
        countryIDselect=[]
        nameselect=[]
        for countryID,name,code in match:
            nameselect.append(name+' (+'+code+')')
            countryIDselect.append(countryID)
        return countryIDselect[xbmcgui.Dialog().select('Please Country Code', nameselect)]
    
def SIGNIN():
    utils.log('firstrun.py','SIGNIN')
    email=Search('Email')
    ADDON.setSetting('user',email)
    password=Search('Password')
    ADDON.setSetting('pass',password)
    ## 3.4.6AUTH()    
    LOGIN()

def Launch():        
	utils.log('firstrun.py','Launch')
	username= ADDON.getSetting('user')
	utils.log('firstrun.py','username= %s' % username)
	if not '@' in username:
		dialog = xbmcgui.Dialog()
		if dialog.yesno(ADDON.getAddonInfo('name'), 'Do you Wish To Register','', "Or Sign In",'Register','Sign In'):
	
			SIGNIN()
	
		else:
			ref = recordings.referralLink()
			if ref == '0' or ref =='1' or ref =='2':
				dialog.ok(ADDON.getAddonInfo('name'), 'Please register for ' + ADDON.getAddonInfo('name') + ' at ' + definition.getREGISTRATION(),'After registering check your email to verify account','Then come back and sign in.')
			else:
				firstname=Search('First Name')
				surname=Search('Surname')
				email=Search('Email')
				password=Search('Password')
				country_id=GetCountryID()
				phone=Numeric('Phone Number')
				url=definition.getBASEURL() + '/index.php?' + recordings.referral()+ 'c=1&a=1&xbmc=1&r=xbmc&accdata={"email":"%s","firstname":"%s","lastname":"%s","psw":"%s","cntid":"%s","phnnm":"%s"}'%(email,firstname,surname,password,country_id,phone)
				link=OPEN_URL(url)
				if 'success' in link:
					dialog.ok(ADDON.getAddonInfo('name'), 'Thank You For Registering','Please Open Your Email Client', 'And Verify Your Email Address')
					ADDON.setSetting('user',email)
					ADDON.setSetting('pass',password)
					ADDON.setSetting('firstrun','true')
				else:
					winput=re.compile('"message":"(.+?)"').findall(link)
					if dialog.yesno(ADDON.getAddonInfo('name'), winput[0],'', 'Exit And Restart Again'):
						Launch()
					else:
						EXIT()


Launch()                
