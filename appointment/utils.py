import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def send_sms(api_key, message, sender_id, phone_number):
    """
    Send SMS using Arkesel API

    Args:
        api_key (str): Arkesel API key
        message (str): SMS message content
        sender_id (str): Sender ID (e.g., "HospitalApp")
        phone_number (str): Recipient phone number

    Returns:
        dict: API response containing status and details
    """
    base_url = f"https://sms.arkesel.com/sms/api?action=send-sms&api_key={api_key}&from={sender_id}"
    sms_url = base_url + f"&to={phone_number}&sms={message}"

    # Add use_case for Nigerian contacts as per API documentation
    if phone_number.startswith('+234') or phone_number.startswith('234'):
        sms_url += "&use_case=transactional"

    try:
        response = requests.get(sms_url, timeout=30)
        response_json = response.json()

        if response.status_code == 200:
            logger.info(f"SMS sent successfully to {phone_number}: {response_json}")
        else:
            logger.error(f"SMS failed to {phone_number}. Status: {response.status_code}, Response: {response_json}")

        return response_json

    except requests.exceptions.RequestException as e:
        logger.error(f"SMS request failed to {phone_number}: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    except ValueError as e:
        logger.error(f"Invalid JSON response from SMS API for {phone_number}: {str(e)}")
        return {'status': 'error', 'message': 'Invalid API response'}


def send_appointment_confirmation_sms(appointment):
    """
    Send appointment confirmation SMS to the patient

    Args:
        appointment: Appointment model instance

    Returns:
        dict: SMS API response
    """
    api_key = settings.ARKESSEL_API_KEY
    sender_id = settings.ARKESSEL_SENDER_ID

    # Format the message
    message = (
        f"Hello {appointment.full_name}, your appointment at {appointment.hospital.name} "
        f"with Dr. {appointment.doctor.name} is confirmed for {appointment.date} at {appointment.time}. "
        f"Please arrive 15 minutes early. Stay safe!"
    )

    # Ensure phone number has country code
    phone_number = appointment.phone
    if not phone_number.startswith('+'):
        # Assume Ghanaian numbers if no country code (since timezone is Africa/Accra)
        if phone_number.startswith('0'):
            phone_number = '+233' + phone_number[1:]
        else:
            phone_number = '+233' + phone_number

    return send_sms(api_key, message, sender_id, phone_number)


# Test function for SMS functionality
def test_sms_functionality():
    """
    Test function to verify SMS sending works correctly.
    Call this from Django shell: python manage.py shell -c "from appointment.utils import test_sms_functionality; test_sms_functionality()"
    """
    from django.conf import settings

    # Test data
    test_api_key = settings.ARKESSEL_API_KEY
    test_sender_id = settings.ARKESSEL_SENDER_ID
    test_phone = "+233501234567"  # Replace with a test phone number
    test_message = "Test SMS from Hospital Appointment System. This is a test message."

    print("Testing SMS functionality...")
    print(f"API Key: {test_api_key[:10]}...")  # Show first 10 chars for security
    print(f"Sender ID: {test_sender_id}")
    print(f"Phone: {test_phone}")
    print(f"Message: {test_message}")

    if test_api_key == 'your-api-key-here':
        print("⚠️  WARNING: Using placeholder API key. Please set ARKESSEL_API_KEY environment variable.")
        return False

    try:
        response = send_sms(test_api_key, test_message, test_sender_id, test_phone)
        print(f"SMS Response: {response}")

        if response.get('status') == 'success' or 'code' in response:
            print("✅ SMS sent successfully!")
            return True
        else:
            print("❌ SMS failed to send.")
            return False

    except Exception as e:
        print(f"❌ Error testing SMS: {str(e)}")
        return False