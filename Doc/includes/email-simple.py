# Import smtplib dla the actual sending function
zaimportuj smtplib

# Import the email modules we'll need
z email.mime.text zaimportuj MIMEText

# Open a plain text file dla reading.  For this example, assume that
# the text file contains only ASCII characters.
przy open(textfile) jako fp:
    # Create a text/plain message
    msg = MIMEText(fp.read())

# me == the sender's email address
# you == the recipient's email address
msg['Subject'] = 'The contents of %s' % textfile
msg['From'] = me
msg['To'] = you

# Send the message via our own SMTP server.
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()
