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

def send_booking_request_notification_to_provider(provider_email, venue_name, customer_name, booking_date_range):
    """Notify the venue provider about a new booking request."""
    subject = f"New Booking Request for {venue_name}"
    html_part = f'''
        <div style="text-align: center;">
            <p>Dear Venue Provider,</p>
            <p>You have received a new booking request for your venue, <strong>{venue_name}</strong>.</p>
            <p>Customer Name: <strong>{customer_name}</strong></p>
            <p>Requested Dates: <strong>{', '.join(booking_date_range)}</strong></p>
            <p>Please review and accept or reject the booking request in your dashboard.</p>
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
                        "Email": provider_email,
                        "Name": "Venue Provider"
                    }
                ],
                "Subject": subject,
                "TextPart": "New Booking Request Notification",
                "HTMLPart": html_part
            }
        ]
    }
    try:
        mailjet.send.create(data=data)
    except Exception as e:
        print(f"Failed to send notification to provider {provider_email}: {str(e)}")

def send_booking_status_notification_to_customer(customer_email, venue_name, status):
    """Notify the customer about the booking status update."""
    subject = f"Your Booking Request for {venue_name} is {status}"
    html_part = f'''
        <div style="text-align: center;">
            <p>Dear Customer,</p>
            <p>Your booking request for <strong>{venue_name}</strong> has been <strong>{status}</strong>.</p>
            <p>If you have any questions, feel free to contact us.</p>
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
                        "Email": customer_email,
                        "Name": "Customer"
                    }
                ],
                "Subject": subject,
                "TextPart": "Booking Status Update",
                "HTMLPart": html_part
            }
        ]
    }
    try:
        mailjet.send.create(data=data)
    except Exception as e:
        print(f"Failed to send notification to customer {customer_email}: {str(e)}")

def send_hire_notification(staff_email, hirer_name, hirer_type, requested_dates):
    """Notify staff about a new hire request."""
    subject = "New Hire Request"
    html_part = f"""
    <div>
        <p>Hello,</p>
        <p>You have received a new hire request from <strong>{hirer_name}</strong> ({hirer_type}).</p>
        <p>Requested Dates: {', '.join(requested_dates)}</p>
        <p>Please log in to your dashboard to accept or reject this request.</p>
    </div>
    """
    data = {
        'Messages': [{
            "From": {"Email": "Mazanaziz420@gmail.com", "Name": "EvePlan.pk"},
            "To": [{"Email": staff_email, "Name": "Staff"}],
            "Subject": subject,
            "HTMLPart": html_part
        }]
    }
    try:
        mailjet.send.create(data=data)
    except Exception as e:
        print(f"Failed to send hire notification to {staff_email}: {str(e)}")

def send_hire_status_notification(hirer_email, staff_name, status, requested_dates):
    """Notify hirer about the hire request status update."""
    subject = f"Your Hire Request has been {status}"
    html_part = f"""
    <div>
        <p>Hello,</p>
        <p>Your hire request for <strong>{staff_name}</strong> has been <strong>{status}</strong>.</p>
        <p>Requested Dates: {', '.join(requested_dates)}</p>
    </div>
    """
    data = {
        'Messages': [{
            "From": {"Email": "Mazanaziz420@gmail.com", "Name": "EvePlan.pk"},
            "To": [{"Email": hirer_email, "Name": "Hirer"}],
            "Subject": subject,
            "HTMLPart": html_part
        }]
    }
    try:
        mailjet.send.create(data=data)
    except Exception as e:
        print(f"Failed to send hire status notification to {hirer_email}: {str(e)}")