import imaplib, serial, struct, time

ser = serial.Serial('arduino_port_number',9600)
obj = imaplib.IMAP4_SSL('imap.gmail.com')
obj.login('Your_email_address','Your_password')

while 1:      #loop till eternity
	obj.select()
	val = len(obj.search(None,'UnSeen')[1][0].split())
	print "%s unread messages." %val    #the number of unread messages
	ser.write(str(val))      #write to serial port
	time.sleep(60)    #sleeps for 1 minute and then re-checks for new emails.
