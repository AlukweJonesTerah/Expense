import os
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from smtplib import SMTPException
import logging
import threading
# from django.contrib.auth.models import User
logger = logging.getLogger(__name__)

class EmailThread(threading.Thread):
    def __int__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)

def send_email(email_subject, email_body, recipient_email):
    try:
    
        EMAIL_HOST = os.environ.get("EMAIL_HOST")
        EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
        EMAIL_USE_TLS = True
        DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
        EMAIL_PORT = 587
        EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
        
        # Connect to the SMTP server
        connection = None
        try:
            connection = get_connection(
                host=EMAIL_HOST,
                port=EMAIL_PORT,
                username=EMAIL_HOST_USER,
                password=EMAIL_HOST_PASSWORD,
                use_tls=EMAIL_USE_TLS
            )
            connection.open()
        except SMTPException as e:
            # Other logic here
            print(f"SMTP Connection Error: {e}")
        except Exception as e:
            # Other logic here
            print(f"An error occurred: {e}")

            
        if connection:
            try:
                email = EmailMessage(
                    email_subject,
                    email_body,
                    EMAIL_HOST_USER,
                    DEFAULT_FROM_EMAIL,
                    [recipient_email],
                    connection=connection,
                )
                # email.send(fail_silently=False)
                # Create an EmailThread instance and start the thread to send the email
                email_thread = EmailThread(email)
                email_thread.start()
            except Exception as e:
                # Other logic here
                print(f"Email sending error: {e}")
                
            # Close connection
            connection.close()
    except SMTPException as e:
        logger.error(f"SMTP Exception: {e}")
        print(f"SMTP Exception: {e}")
    except Exception as e:
        logger.error(f"An error occured: {e}")
        print(f"An error occured: {e}")
    finally:
        if connection:
            connection.close()