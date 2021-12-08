
from django.core.mail import EmailMessage, send_mail
from decouple import config



class Utils:

    @staticmethod
    def send_email(data):
        msg = EmailMessage(
            subject=data["subject"],
            body=data["body"],
            from_email=config('host_email'),
            to=data["recepient"],
        )
        msg.content_subtype = "html"
        msg.send()



import threading

class EmailThread(threading.Thread):

    def __init__(self, subject, body, recipient_list):
        # super().__init__(daemon=True)
        self.subject = subject
        self.recipient_list = recipient_list
        self.body = body
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.body, config('host_email'), self.recipient_list)
        msg.content_subtype = "html"
        msg.send()


def send_html_mail(subject, body, recipient_list):
    # print(subject)
    # print(body)
    # print(recipient_list)
    EmailThread(subject, body, recipient_list).start()
