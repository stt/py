"""
 msender - Utility to handle large emailing jobs
 (c)2011 <samuli.tuomola@ixonos.com>
"""
import os, sys, smtplib, email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

relay = os.getenv('SMTPHOST') or 'smtpout.dmz'

class msender:
	def __init__(self, template, tvars):
		self.template = template
		self.vards = []

		# split tab-separated key-value pairs
		for line in tvars:
			if '=' not in line: raise Exception('Invalid input: '+line)
			self.vards.append( dict([v.split('=',1) for v in line.split('\t')]) )
		# validate
		for var in self.vards:
		  if not var.has_key('rcpt'):
		    raise Exception('Input line missing rcpt: '+str(var))
		  if '@' not in var['rcpt']:
		    raise Exception('Does not look like an email address: '+var['rcpt'])

	def format(self, vard):
		try:
			return self.template.format(**vard)
		except KeyError as e:
			print >>sys.stderr, "Error: Template expected to be provided", e, """
				\rTo get regular curlybraces give them twice, i.e. {{text}}.
			"""
			sys.exit(5)

	def send(self, relay, fromAddr, rcptAddr, subject, text):
		""" todo: multiple mails in one connection """
		msg = MIMEMultipart("alternative")
		msg.set_charset("utf-8")
		msg["Subject"] = subject
		msg["From"] = fromAddr
		msg["To"] = rcptAddr
		msg.attach(MIMEText(text, "plain", "utf-8"))
		
		server = smtplib.SMTP(relay)
		try:
			server.sendmail(fromAddr, [rcptAddr], msg.as_string())
		finally:
			server.quit()

def usage(error="", ret=0):
	if error: print >>sys.stderr, 'Error:', error, '\n'
	print """Usage: msender [-frslt] [key=val..]
	-f  From address, required
	-s  Subject, required
	-l  A file containing tab-separated key=val pairs, where each line represents
	    email to be sent, and the key "rcpt" is the recipient address
	-t  Template file for the mail body, required. Surround variables with {}
	-w  Wait time between mails, default 0.5

Any extra arguments are considered key-value pairs when -l is not given,
in this case atleast rcpt= needs to be defined, e.g. 
	msender -f sender@example.com -t mail.txt -s Subject rcpt=test@example.com
	"""
	sys.exit(ret)
	
if __name__ == "__main__":
	import getopt

	if len(sys.argv) < 3: usage()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "f:s:l:t:w:")
		opts = dict(opts)
	except getopt.GetoptError, err:
		usage(str(err), 2)

	lst = tmpl = None
	wait = 0.5

	for o in opts:
		arg = opts[o]
		if o == '-l':
			# read list of recipients and template variables
			with open(arg) as fh:
				# ignore empty lines
				lst = [l.strip() for l in fh.readlines() if l.strip()]
		elif o == '-t':
			with open(arg) as fh:
				tmpl = fh.read()
		elif o == '-w':
			wait = float(arg)

	if not opts.has_key('-f') or not opts.has_key('-s') or not opts.has_key('-t'):
		usage("-f, -s and -t options are required", 3)
	if '@' not in opts['-f']:
		raise Exception('Does not look like an email address: '+opts['-f'])
	if lst is None:
		lst = ['\t'.join(args)]
		if len(args) < 1 or 'rcpt=' not in lst[0]:
			usage("Without -l at least rcpt=addr needs to be specified", 3)

	msend = msender(tmpl, lst)
	
	exampletext = msend.format(msend.vards[0])
	print 'Example of email to be sent to',
	print msend.vards[0]['rcpt'] if len(lst)==1 else '%i addresses'%len(lst)
	print '=='*10, '\n', exampletext
	answer = raw_input('Using server %s.. are you sure (y/n)? ' % relay)

	if(answer.strip() == 'y'):
		import time
		for d in msend.vards:
			print time.strftime("[%H:%M:%S]"), 'Sending to', d['rcpt']
			try:
				msend.send(relay, opts['-f'], d['rcpt'], opts['-s'], msend.format(d))
				time.sleep(wait)
			except Exception as ex:
				print 'Error:',str(ex)
				if raw_input('Continue (y/n)? ').strip() != 'y':
					sys.exit(4)
	else:
		print 'Canceled'

