# Import smtplib dla the actual sending function
zaimportuj smtplib

# Here are the email package modules we'll need
z email.mime.image zaimportuj MIMEImage
z email.mime.multipart zaimportuj MIMEMultipart

COMMASPACE = ', '

# Create the container (outer) email message.
msg = MIMEMultipart()
msg['Subject'] = 'Our family reunion'
# me == the sender's email address
# family = the list of all recipients' email addresses
msg['From'] = me
msg['To'] = COMMASPACE.join(family)
msg.preamble = 'Our family reunion'

# Assume we know that the image files are all w PNG format
dla file w pngfiles:
    # Open the files w binary mode.  Let the MIMEImage klasa automatically
    # guess the specific image type.
    przy open(file, 'rb') jako fp:
        img = MIMEImage(fp.read())
    msg.attach(img)

# Send the email via our own SMTP server.
s = smtplib.SMTP('localhost')
s.send_message(msg)
s.quit()
