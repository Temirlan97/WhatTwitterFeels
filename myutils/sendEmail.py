import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import readKeyfile
import log

#################################
# STORING PROCESSED TWEETS					
#################################
 

def notifyViaEmail(subject, body):
	credentials = readKeyfile.readOutValues("mailconfigs.txt")
	try:
		fromaddr = credentials['fromaddr']
		toaddr = credentials['toaddr']
		msg = MIMEMultipart()
		msg['From'] = fromaddr
		msg['To'] = toaddr
		msg['Subject'] = subject
		msg.attach(MIMEText(body, 'plain'))
		server = smtplib.SMTP(credentials['smtphost'], credentials['smtpport'])
		server.starttls()
		server.login(fromaddr, credentials['emailpass'])
		text = msg.as_string()
		server.sendmail(fromaddr, toaddr, text)
		server.quit()
		log.infoLog("Sent out notification to " + toaddr)
	except smtplib.SMTPException as error:
		log.errorLog(error)
