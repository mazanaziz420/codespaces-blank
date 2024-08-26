from mailjet_rest import Client
from config import Config

mailjet = Client(auth=(Config.MAILJET_API_KEY, Config.MAILJET_SECRET_KEY), version='v3.1')

def send_verification_email(email, verification_code, is_signup=True):
    if is_signup:
        subject = "Verification Code for Your EvePlan.pk Account"
        html_part = f'''
            <div style="text-align: center;">
                <p>Thank you for signing up. Please use the verification code below to activate your account:</p>
                <div style="font-size: 24px; font-weight: bold; padding: 20px; background: linear-gradient(135deg, blue, purple); color: white;">
                    {verification_code}
                </div>
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
        '''
    else:
        subject = "Password Reset Verification Code"
        html_part = f'''
            <div style="text-align: center;">
                <p>You requested to reset your password. Please use the verification code below to proceed:</p>
                <div style="font-size: 24px; font-weight: bold; padding: 20px; background: linear-gradient(135deg, blue, purple); color: white;">
                    {verification_code}
                </div>
                <p>If you didn't request this code, please ignore this email.</p>
            </div>
        '''
    
    data = {
        'Messages': [
            {
                "From": {
                    "Email": "Mazanaziz420@gmail.com",
                    "Name": "EvePlan.pk"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": "You"
                    }
                ],
                "Subject": subject,
                "TextPart": "Greetings from EvePlan!",
                "HTMLPart": html_part
            }
        ]
    }

    try:
        mailjet.send.create(data=data)
    except Exception as e:
        print(f"Failed to send email to {email}: {str(e)}")
