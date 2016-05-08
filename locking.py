#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmcaddon,xbmc,os,sys,datetime,re,glob

#ADDON      = xbmcaddon.Addon(id='plugin.video.wozboxntv')
import definition
ADDON      = definition.getADDON()
#print 'locking.py: sys.argv= %s' %(str(repr(sys.argv)))

datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
def adjustFileName(title):
	filetitle = title.replace('?', '')
	filetitle = filetitle.replace(':', ' -')
	filetitle = filetitle.replace('/', '')
	filetitle = filetitle.replace('+', '')
	filetitle = filetitle.replace('\\', '')
	filetitle = re.sub('[,:\\/*?\<>|"]+', '', filetitle)
	filetitle = " ".join(filetitle.split())  # Remove extra spaces from filename
	return filetitle
	
def recordLock(lockDescription):
	recordingLock = os.path.join(datapath, 'recordingLock') + adjustFileName(lockDescription) + '.txt'
	#print 'recordLock0: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
	if os.path.isfile(recordingLock) == False: 
		# create lock file
		LF = open(recordingLock, 'a')
		# Write to our text file the information we have provided and then goto next line in our file.
		LF.write(lockDescription + '\n')
		# Close our file so no further writing is posible.
		LF.close()
		ADDON.setSetting('StopRecording','Lock: ' + lockDescription)
		#print 'recordLock1: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
def deleteLockFile(recordingLock):
	tries    = 0
	maxTries = 10
	maxSleep = 50
	while os.path.exists(recordingLock) and tries < maxTries:
		try:
			os.remove(recordingLock)
			#print 'recordUnlock(before break, tries=%s)): recordingLock= %s' % (repr(tries), repr(recordingLock))
			ADDON.setSetting('StopRecording','unLock: ' + lockDescription)
			break
		except:
			xbmc.sleep(maxSleep)
			tries = tries + 1
def deleteOldLockFile(recordingLock,ageinhours):
	tries    = 0
	maxTries = 10
	maxSleep = 50
	while os.path.exists(recordingLock) and tries < maxTries:
		try:
			createdtime= os.stat(recordingLock).st_ctime
			now= datetime.datetime.today()
			if now > datetime.datetime.fromtimestamp(createdtime) +  datetime.timedelta(hours = ageinhours):
				os.remove(recordingLock)
			#print 'recordUnlock(before break, tries=%s)): recordingLock= %s' % (repr(tries), repr(recordingLock))
			ADDON.setSetting('StopRecording','unLock: ' + lockDescription)
			break
		except:
			xbmc.sleep(maxSleep)
			tries = tries + 1
def recordUnlock(lockDescription):
	recordingLock = os.path.join(datapath, 'recordingLock') + adjustFileName(lockDescription) + '.txt'
	#print 'recordUnlock: recordingLock= %s' % repr(recordingLock)
	ADDON.setSetting('StopRecording','Recording stopped: ' + lockDescription + ' ' + datetime.datetime.today().strftime('%H:%M'))
	# delete lock file
	deleteLockFile(recordingLock)
def recordUnlockAll():
	lockDescription = '*'
	recordingLock = os.path.join(datapath, 'recordingLock') + lockDescription + '.txt'
	LockFiles = glob.glob(recordingLock)
	#print 'recordUnlockAll: recordingLock= %s' % (repr(LockFiles))
	# delete lock files
	for file in LockFiles:
		#print 'locking.recordUnlockAll: delete file= %s' %repr(file)
		deleteLockFile(file)
def isRecordLocked(lockDescription):
	isAnyRecordLocked()
	recordingLock = os.path.join(datapath, 'recordingLock') + adjustFileName(lockDescription) + '.txt'
	#print 'isRecordLocked: recordingLock= %s' % repr(recordingLock)
	#print 'isRecordLocked0: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
	if os.path.isfile(recordingLock):  # release scanlock if more thae 1 hour old
		print 'locking.py: os.stat(recordingLock).st_ctime= %s' % repr(os.stat(recordingLock).st_ctime)
		createdtime= os.stat(recordingLock).st_ctime
		now= datetime.datetime.today()
		if now > datetime.datetime.fromtimestamp(createdtime) +  datetime.timedelta(hours = 3):
			recordUnlockAll()
	return os.path.isfile(recordingLock)
def isAnyRecordLocked():
	recordingLock = os.path.join(datapath, 'recordingLock') + '*.txt'
	#print 'isAnyRecordLocked: recordingLock= %s' % repr(recordingLock)
	#print 'isAnyRecordLocked0: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
	LockFiles = glob.glob(recordingLock)
	for file in LockFiles:
		deleteOldLockFile(file,4) #Delete files more than 4 hours old
	#print 'recordUnlockAll: recordingLock= %s' % (repr(LockFiles))
	#print 'recordUnlockAll: recordingLock= %s' % (repr((LockFiles and len(LockFiles) > 0)))
	return (LockFiles and len(LockFiles) > 0)
	
def RecordsLocked():
	recordingLock = os.path.join(datapath, 'recordingLock') + '*.txt'
	LockFiles = glob.glob(recordingLock)
	return LockFiles
	
def scanLock(lockDescription):
	recordingLock = os.path.join(datapath, 'scanLock') + adjustFileName(lockDescription) + '.txt'
	#print 'recordLock0: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
	if os.path.isfile(recordingLock) == False: 
		# create lock file
		LF = open(recordingLock, 'a')
		# Write to our text file the information we have provided and then goto next line in our file.
		LF.write(lockDescription + '\n')
		# Close our file so no further writing is posible.
		LF.close()
		ADDON.setSetting('StopScan','Lock: ' + lockDescription)
		#print 'recordLock1: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
def isScanLocked(lockDescription):
	isAnyScanLocked()
	recordingLock = os.path.join(datapath, 'scanLock') + adjustFileName(lockDescription) + '.txt'
	#print 'isRecordLocked: recordingLock= %s' % repr(recordingLock)
	#print 'isRecordLocked0: recordingLock= %s for %s' % (repr(os.path.isfile(recordingLock)), repr(recordingLock))
	return os.path.isfile(recordingLock)
def isAnyScanLocked():
	recordingLock = os.path.join(datapath, 'scanLock') + '*.txt'
	LockFiles = glob.glob(recordingLock)
	for file in LockFiles:
		deleteOldLockFile(file,2) #Delete files more than 2 hours old
	return (LockFiles and len(LockFiles) > 0)
def scanUnlockAll():
	lockDescription = '*'
	recordingLock = os.path.join(datapath, 'scanLock') + lockDescription + '.txt'
	LockFiles = glob.glob(recordingLock)
	#print 'recordUnlockAll: recordingLock= %s' % (repr(LockFiles))
	# delete lock files
	for file in LockFiles:
		#print 'locking.recordUnlockAll: delete file= %s' %repr(file)
		deleteLockFile(file)
