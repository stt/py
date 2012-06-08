#!/usr/bin/env python
"""
 msender - Utility to handle large emailing jobs
 (c)2011,2012 <samuli.tuomola@ixonos.com>

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

 NOTE:
 -Tested on python 2.6-2.7
 -Calculate sleep time keeping in mind the rate limits configured for
  the SMTP server (in postfix smtpd_client_message_rate_limit)
"""
import os, sys, smtplib, email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

relay = os.getenv('SMTPHOST') or 'smtpout.dmz'

# unbuffered in case we're being piped to tee
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

class MSender:
	def __init__(self, template, tvars, relay):
		"""Initialize and validate recipient list."""
		self.template = template
		self.vards = []
		self.relay = relay
		self.debug = False
		self.server = smtplib.SMTP()
		self.mailcounter = 0
		self.conntimer = 0
		self.mails_per_connection = 50
		# send to multiple recipients, only available without template keywords, also disables
		# the To-header, check the limit from sysadmin (smtpd_recipient_limit in postfix)
		self.rcpts_per_mail = None

		# prefer quoted-printable content-encoding over the default base64
		email.charset.CHARSETS['utf-8'] = (email.charset.QP, email.charset.QP, 'utf-8')

		# split tab-separated key-value pairs
		for i,line in enumerate(tvars):
			try:
				self.vards.append( dict([v.split('=',1) for v in line.split('\t')]) )
			except Exception as e:
				print '\n!! Invalid input on line %i, expected tab-separated key-value pairs !!\n' % i
				raise e
		# validate
		for var in self.vards:
			if not var.has_key('rcpt'):
				raise Exception('Input line missing rcpt: '+str(var))
			if '@' not in var['rcpt']:
				raise Exception('Does not look like an email address: '+var['rcpt'])
			if self.rcpts_per_mail and len(var) > 1:
				#print 'WARNING: sending emails one by one, because mail message uses template keywords'
				self.rcpts_per_mail = None

	def format(self, vard):
		"""Format a message with given dictionary."""
		try:
			return self.template.format(**vard)
		except KeyError as e:
			print >>sys.stderr, "Error: Template expected to be provided", e, """
				\rTo get regular curlybraces give them twice, i.e. {{text}}.
			"""
			sys.exit(5)

	def verify_connection(self):
		"""Test the connection, if it's been dropped, reconnect."""
		try:
			if self.mails_per_connection and self.mailcounter >= self.mails_per_connection:
				self.server.quit()

			self.server.noop()
		except Exception as e:
			self.server = smtplib.SMTP(self.relay)
			if self.debug: self.server.set_debuglevel(1)
			self.mailcounter = 0

	def send(self, fromAddr, rcptAddr, subject, text):
		"""Send a plaintext email."""
		msg = MIMEMultipart("alternative")
		msg.set_charset("utf-8")
		msg["Subject"] = subject
		msg["From"] = fromAddr
		if not isinstance(rcptAddr, list):
			msg["To"] = rcptAddr
		msg.attach(MIMEText(text, "plain", "utf-8"))
		#msg.attach(MIMEText(html, "html", "utf-8"))

		self.verify_connection()
		if not isinstance(rcptAddr, list):
			rcptAddr = [rcptAddr]
		self.server.sendmail(fromAddr, rcptAddr, msg.as_string())
		self.mailcounter += 1

	def close(self):
		if self.server:
			self.server.quit()

def usage(error="", ret=0):
	if error: print >>sys.stderr, 'Error:', error, '\n'
	print """Usage: msender [-dfrslt] [key=val..]
	-d  Enable debug
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

def timedesc(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return "%dh %02dm %02ds" % (h, m, s)

if __name__ == "__main__":
	import getopt

	if len(sys.argv) < 3: usage()

	try:
		opts, args = getopt.getopt(sys.argv[1:], "df:s:l:t:w:")
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

	msend = MSender(tmpl, lst, relay)
	msend.debug = opts.has_key('-d')

	exampletext = msend.format(msend.vards[0])
	print 'Example of email to be sent to',
	print msend.vards[0]['rcpt'] if len(lst)==1 else '%i addresses'%len(lst)

	persec = 1/wait
	if msend.rcpts_per_mail > 0:
		print 'Sending mails in batches of %i, %.2f batches/s (wait time %.2fs), runtime approx %s' % \
			(msend.rcpts_per_mail, 1/wait, wait, timedesc(len(lst)/msend.rcpts_per_mail/persec))
	else:
		print 'Sending %.2f mails/s (wait time %.2fs), runtime approx %s' % \
			(persec, wait, timedesc(len(lst)/persec))

	if len(lst) > 10 and msend.debug:
		print '\nWARNING: debugging is enabled and sending more than 10 emails'

	print '=='*10, '\n', exampletext
	answer = raw_input('Using server %s.. are you sure (y/n)? ' % relay)

	if answer.strip() == 'y':
		import time
		print '\n', time.strftime("[%H:%M:%S]"), 'Started'

		# batch sending
		if msend.rcpts_per_mail > 0:
			for pos in range(0, len(msend.vards), msend.rcpts_per_mail):
				rcpts = [e['rcpt'] for e in msend.vards[pos:pos+msend.rcpts_per_mail]]

				print time.strftime("[%H:%M:%S]"), 'Sending to', rcpts
				try:
					msend.send(opts['-f'], rcpts, opts['-s'], msend.template)
					time.sleep(wait)
				except Exception as ex:
					print 'Error:',str(ex)
					if raw_input('Continue (y/n)? ').strip() != 'y':
						raise ex
						sys.exit(4)

		# individual sending
		else:
			for i,d in enumerate(msend.vards):
				print time.strftime("[%H:%M:%S]"), 'Sending to %i/%i,' % (i,len(lst)), d['rcpt']
				try:
					msend.send(opts['-f'], d['rcpt'], opts['-s'], msend.format(d))
					time.sleep(wait)
				except Exception as ex:
					print 'Error:',str(ex)
					if raw_input('Continue (y/n)? ').strip() != 'y':
						sys.exit(4)

		msend.close()
		print time.strftime("[%H:%M:%S]"), 'Finished'

	else:
		print 'Canceled'

