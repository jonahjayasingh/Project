import requests
import logging

logger = logging.getLogger(__name__)

WHATSAPP_SERVICE_URL = "http://localhost:3000/send-message"

def send_whatsapp_message(number, message, file_path=None):
    """
    Sends a WhatsApp message via the Node.js service.
    
    Args:
        number (str): The recipient's phone number.
        message (str): The text message to send.
        file_path (str, optional): Absolute path to a file to send.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        data = {
            "number": number,
            "message": message
        }
        if file_path:
            data["filePath"] = file_path
            
        response = requests.post(WHATSAPP_SERVICE_URL, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                logger.info(f"WhatsApp message sent to {number}")
                return True
            else:
                logger.error(f"WhatsApp service error: {result.get('message')}")
        else:
            logger.error(f"WhatsApp service failed with status {response.status_code}")
            
    except Exception as e:
        logger.error(f"Failed to connect to WhatsApp service: {str(e)}")
        
    return False

def confirm_booking_whatsapp(booking):
    """Specific helper for booking confirmation."""
    msg = (
        f"Hello {booking.patient.full_name},\n\n"
        f"Your booking for *{booking.test_name}* at *{booking.lab.lab_name}* "
        f"has been received for *{booking.booking_date}* at *{booking.time_slot.strftime('%I:%M %p')}*.\n\n"
        f"Please upload payment proof in your dashboard to confirm your appointment.\n\n"
        f"Thank you!"
    )
    return send_whatsapp_message(booking.patient.whatsapp_number, msg)

def send_result_whatsapp(booking):
    """Specific helper for sending lab results with file."""
    msg = (
        f"Hello {booking.patient.full_name},\n\n"
        f"Your test result for *{booking.test_name}* is now available.\n"
        f"We have attached the report with this message for your convenience.\n\n"
        f"Stay healthy!"
    )
    
    file_path = None
    if booking.report_file:
        file_path = booking.report_file.path
        
    return send_whatsapp_message(booking.patient.whatsapp_number, msg, file_path)

def send_welcome_whatsapp(patient):
    """Specific helper for welcoming new patients."""
    msg = (
        f"Welcome to LMS, *{patient.full_name}*!\n\n"
        f"Your account has been successfully created. You can now book tests and receive reports digitally.\n\n"
        f"Stay healthy!"
    )
    return send_whatsapp_message(patient.whatsapp_number, msg)

def send_status_update_whatsapp(booking):
    """Sends a notification based on the current booking status."""
    status_messages = {
        'Confirmed': (
            f"✅ *Booking Confirmed*\n\n"
            f"Hello {booking.patient.full_name},\n"
            f"Your booking for *{booking.test_name}* at *{booking.lab.lab_name}* has been confirmed.\n"
            f"Scheduled for: {booking.booking_date} at {booking.time_slot.strftime('%I:%M %p')}.\n\n"
            f"See you soon!"
        ),
        'Sample Collected': (
            f"💉 *Sample Collected*\n\n"
            f"Dear {booking.patient.full_name},\n"
            f"Your sample for *{booking.test_name}* has been successfully collected.\n"
            f"We will notify you once the results are ready.\n\n"
            f"Thank you!"
        ),
        'Processing': (
            f"🔬 *Processing in Progress*\n\n"
            f"Hello {booking.patient.full_name},\n"
            f"Your sample for *{booking.test_name}* is now being processed in our laboratory.\n"
            f"Expected results will be available shortly.\n"
        ),
        'Completed': (
            f"📄 *Report Ready*\n\n"
            f"Great news {booking.patient.full_name}!\n"
            f"Your test results for *{booking.test_name}* are now available.\n"
            f"You can view them on your dashboard or wait for the report file in a separate message.\n"
        ),
        'Cancelled': (
            f"⚠️ *Booking Cancelled*\n\n"
            f"Hello {booking.patient.full_name},\n"
            f"Your booking for *{booking.test_name}* has been cancelled.\n"
            f"If you didn't request this, please contact the lab directly.\n"
        )
    }
    
    msg = status_messages.get(booking.status)
    if msg:
        return send_whatsapp_message(booking.patient.whatsapp_number, msg)
    return False
