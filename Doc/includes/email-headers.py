# Import the email modules we'll need
z email.parser zaimportuj Parser

# If the e-mail headers are w a file, uncomment these two lines:
# przy open(messagefile) jako fp:
#     headers = Parser().parse(fp)

#  Or dla parsing headers w a string, use:
headers = Parser().parsestr('From: <user@example.com>\n'
        'To: <someone_inaczej@example.com>\n'
        'Subject: Test message\n'
        '\n'
        'Body would go here\n')

#  Now the header items can be accessed jako a dictionary:
print('To: %s' % headers['to'])
print('From: %s' % headers['from'])
print('Subject: %s' % headers['subject'])
