import email
import imaplib
import os
import sys
from datetime import datetime, timedelta

detach_dir = '.'
attach_dir = 'adjuntos'
from_date = datetime.today() + timedelta(days=-4)
from_subject = 'atconline@redenlace.com.bo'
    
if attach_dir not in os.listdir(detach_dir):
    os.mkdir(attach_dir)
try:
    imapSession = imaplib.IMAP4_SSL('mail.epsas.com')
    typ, accountDetails = imapSession.login('garciafr@epsas.com', '*********')
    imapSession.select('INBOX')
    typ, data = imapSession.search(None,'(SINCE "' + from_date.strftime("%d-%b-%Y")+ '" FROM "' + from_subject + '")')

    print('Procesando correos desde el ' + from_date.strftime("%Y-%m-%d"))
    for msgId in data[0].split():
        typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
        mail = email.message_from_string(messageParts[0][1].decode('utf-8'))
        date_object = datetime.strptime(mail['Date'], "%a, %d %b %Y %H:%M:%S %z") + timedelta(days=-1)

        path_date = os.path.join(date_object.strftime("%Y%m%d"))
        if path_date not in os.listdir(os.path.join(detach_dir, attach_dir)):
            os.mkdir(os.path.join(detach_dir, attach_dir,path_date))

        for part in mail.walk():
            fileName = part.get_filename()
            if bool(fileName):
                filePath = os.path.join(detach_dir, attach_dir, path_date, fileName)
                if not os.path.isfile(filePath):
                    fp = open(filePath, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
                    print('Creado: ' + filePath)
                else:
                    print('Existe: ' + filePath)
    imapSession.close()
    imapSession.logout()
except Exception:
    print(sys.exc_info())