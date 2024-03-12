import smtplib
import os

# sender = os.environ.get('SenderMail')
# password = os.environ.get('SenderPass')
# receiver = os.environ.get('Receiver')


class Messenger():
    def send_message(self, name:str, email: str, subject: str, message: str):
        # with smtplib.SMTP('smtp.gmail.com') as connection:
        #     connection.starttls()
        #     connection.login(sender,password)
        #     connection.sendmail(from_addr=sender, to_addrs=receiver, msg=f'Subject: {subject} from {name}\n\n {message}\n Contact: {email}')
        #     connection.close()
        print(name, email, subject, message)