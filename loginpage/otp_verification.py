import os
import secrets
import string
import smtplib

from google.cloud import firestore
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

load_dotenv()


# Firestore database
def firestore_database():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("FIRESTORE_KEY_PATH")
    # Initialize Firestore client
    db = firestore.Client()
    return db


# Generate OTP
def generate_otp():
    characters = string.digits  # Uppercase letters and digits '0' to '9'
    otp = ''.join(secrets.choice(characters) for _ in range(6))
    return otp


# Send OTP to email
def send_otp_to_email(email, otp):
    outlook_email = os.getenv('EMAIL_HOST')
    outlook_password = os.getenv('EMAIL_PASSWORD')
    outlook_smtp_server = os.getenv('EMAIL_SERVER')
    outlook_smtp_port = int(os.getenv('EMAIL_PORT'))
    sender_name = "SustainaSoil"

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = f'{sender_name} <{outlook_email}>'  # Format: "Name <email>"
    message["To"] = email
    message["Subject"] = "Your OTP Verification | SustainaSoil"
    email_name = email.split('@')[0]

    # HTML content for the email body
    html = f"""
    <html>
    <head>
        <title>OTP Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .header {{
                background-color: #ffffff;
                text-align: center;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .header img {{
                max-width: 500px;
                height: auto;
            }}
            .content-area {{
                background-color: #ffffff;
                margin: 20px;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(9, 8, 8, 0.1);
            }}
            h2 {{
                color: #32281B;
            }}
            h3 {{
                font-size: 24px;
                color: #5A6B47;
                margin-bottom: 10px;
            }}
            p {{
                color: #5A6B47;
                font-size: 20px;
            }}
            .signature {{
                text-align: right;
                font-style: italic;
                color: #5A6B47;
            }}
            .logo {{
                margin-bottom: 20px;
            }}
            .app {{
                color: #32281B;
            }}
        </style>
    </head>
    <body>
        <div>
            <div class="header">
                <img src="https://res.cloudinary.com/duku3q6xf/image/upload/v1702918482/Logo_bzzvjs.png"
                    alt="Logo" class="logo">
            </div>
            <div class="content-area">
                <h2>Hi, {email_name}</h2>
                <p>Thank you for registering with <strong class="app">SustainaSoil.</strong>  To ensure the security of your
                    account, we kindly request you to verify your email address by entering the OTP (One-Time Password)
                    provided below:</p>
                <h3>Your OTP: {otp}</h3>
                <p>If you have any questions or need further assistance, please feel free to contact our customer support
                    team.</p>
                <p>Thank you for choosing <strong class="app">SustainaSoil.</strong> </p>
                <p class="signature"><span class="app">Sincerely,</span> <br> SustainaSoil Lead Team</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Attach HTML content to the email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(outlook_smtp_server, outlook_smtp_port) as server:
            server.starttls()
            server.login(outlook_email, outlook_password)
            server.sendmail(outlook_email, email, message.as_string())
        print("OTP sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


# Congrats email
def send_congrats_email(email):
    outlook_email = os.getenv('EMAIL_HOST')
    outlook_password = os.getenv('EMAIL_PASSWORD')
    outlook_smtp_server = os.getenv('EMAIL_SERVER')
    outlook_smtp_port = int(os.getenv('EMAIL_PORT'))
    sender_name = "SustainaSoil"

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = f'{sender_name} <{outlook_email}>'  # Format: "Name <email>"
    message["To"] = email
    message["Subject"] = "Welcome to SustainaSoil!"
    email_name = email.split('@')[0]

    # HTML content for the email body
    html = f"""
        <html>
        <head>
            <title>OTP Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .header {{
                    background-color: #ffffff;
                    text-align: center;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header img {{
                    max-width: 500px;
                    height: auto;
                }}
                .content-area {{
                    background-color: #ffffff;
                    margin: 20px;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(9, 8, 8, 0.1);
                }}
                h2 {{
                    color: #32281B;
                }}
                h3 {{
                    font-size: 24px;
                    color: #5A6B47;
                    margin-bottom: 10px;
                }}
                p {{
                    color: #5A6B47;
                    font-size: 20px;
                }}
                .signature {{
                    text-align: right;
                    font-style: italic;
                    color: #5A6B47;
                }}
                .logo {{
                    margin-bottom: 20px;
                }}
                .app {{
                    color: #32281B;
                }}
            </style>
        </head>
        <body>
            <div>
                <div class="header">
                    <img src="https://res.cloudinary.com/duku3q6xf/image/upload/v1702918482/Logo_bzzvjs.png"
                        alt="Logo" class="logo">
                </div>
                <div class="content-area">
                    <h2>Hi, {email_name}</h2>
                    <p>Congratulations! Your account registration with <strong class="app">SustainaSoil</strong> has been completed successfully. We're thrilled to welcome you to our community dedicated to sustainable soil practices.</p>
                    <p>Thank you for choosing <strong class="app">SustainaSoil</strong>. Your commitment to improving soil health is admirable, and we're excited to have you on board.</p>
                    <p>If you have any questions or need further assistance, please feel free to contact our customer support team.</p>
                    <p>Once again, welcome to <strong class="app">SustainaSoil</strong>! We look forward to embarking on this sustainability journey together.</p>
                    <p class="signature"><span class="app">Sincerely,</span><br>SustainaSoil Lead Team</p>
                </div>
            </div>
        </body>
        </html>
        """

    # Attach HTML content to the email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(outlook_smtp_server, outlook_smtp_port) as server:
            server.starttls()
            server.login(outlook_email, outlook_password)
            server.sendmail(outlook_email, email, message.as_string())
        print("OTP sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


# Send OTP to Database
def send_the_otp_to_database(email, token):
    db = firestore_database()
    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    otp = generate_otp()

    # Complete the otp_set dictionary
    otp_set = {
        'token': token,
        'email': email,
        'otp': otp,
        'date_added': current_datetime
    }

    # Create a reference to the collection
    collection_ref = db.collection('otp_verification')

    # Add a document to the collection
    doc_ref = collection_ref.document()
    doc_ref.set(otp_set)

    # Return a JSON response
    print('OTP added successfully')
    send_otp_to_email(email, otp)


# Generate token
def generate_token(length=50):
    alphabet = string.ascii_letters + string.digits  # You can include other characters if needed
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token


# Delete session
def del_session(request):
    del request.session['redirect_email']
    del request.session['redirect_token']
    del request.session['redirect_first_name']
    del request.session['redirect_last_name']
    del request.session['redirect_password']


def send_link_change_password_to_email(email, session_token):
    outlook_email = os.getenv('EMAIL_HOST')
    outlook_password = os.getenv('EMAIL_PASSWORD')
    outlook_smtp_server = os.getenv('EMAIL_SERVER')
    outlook_smtp_port = int(os.getenv('EMAIL_PORT'))
    sender_name = "SustainaSoil"

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = f'{sender_name} <{outlook_email}>'  # Format: "Name <email>"
    message["To"] = email
    message["Subject"] = "Change Password | SustainaSoil"
    email_name = email.split('@')[0]

    # HTML content for the email body
    html = f"""
        <html>
        <head>
            <title>OTP Verification</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .header {{
                    background-color: #ffffff;
                    text-align: center;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header img {{
                    max-width: 500px;
                    height: auto;
                }}
                .content-area {{
                    background-color: #ffffff;
                    margin: 20px;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(9, 8, 8, 0.1);
                }}
                h2 {{
                    color: #32281B;
                }}
                h3 {{
                    font-size: 24px;
                    color: #5A6B47;
                    margin-bottom: 10px;
                }}
                p {{
                    color: #5A6B47;
                    font-size: 20px;
                }}
                .signature {{
                    text-align: right;
                    font-style: italic;
                    color: #5A6B47;
                }}
                .logo {{
                    margin-bottom: 20px;
                }}
                .app {{
                    color: #32281B;
                }}
                a.link-data {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #F4F4F4;
                    color: #32281B;
                    font-size: 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s, color 0.3s;
                }}
                .link-data:hover {{
                    background-color: #5A6B47;
                    color: #FFFFFF;
                }}  
            </style>
        </head>
        <body>
            <div>
                <div class="header">
                    <img src="https://res.cloudinary.com/duku3q6xf/image/upload/v1702918482/Logo_bzzvjs.png"
                        alt="Logo" class="logo">
                </div>
                <div class="content-area">
                    <h2>Hi, {email_name}</h2>
                    <p>We received a request to reset your password. If you did not make this request, please ignore this email.</p>
                    <p>Click the button below to reset your password:</p>
                    <a class="link-data" href="http://localhost:8000/change/{session_token}" target="_blank" >Change Password</a>
                    <p class="signature"><span class="app">Sincerely,</span> <br> SustainaSoil Lead Team</p>
                </div>
            </div>
        </body>
        </html>
        """

    # Attach HTML content to the email
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(outlook_smtp_server, outlook_smtp_port) as server:
            server.starttls()
            server.login(outlook_email, outlook_password)
            server.sendmail(outlook_email, email, message.as_string())
        print("Forgot Password link sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# <a href="https://sustainasoil.herokuapp.com/change/?token={request.session['redirect_token']}">https://sustainasoil.herokuapp.com/change/?token={request.session['redirect_token']}</a>
