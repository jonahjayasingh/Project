from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

def generate_certificate_attended_pdf(name, event_name, cert_id):
    template_path = 'static/certificate.jpg'
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    # Fonts
    font_path_light = 'static/Fonts/poppins/Poppins-Light.ttf'
    font_path_bold = 'static/Fonts/poppins/Poppins-Bold.ttf'
    try:
        font_name = ImageFont.truetype(font_path_light, 80)
        font_event = ImageFont.truetype(font_path_light, 50)
        font_bold_title = ImageFont.truetype(font_path_bold, 100)
        font_bold_subtitle = ImageFont.truetype(font_path_bold, 50)
    except OSError:
        font_name = font_event = font_bold_title = font_bold_subtitle = ImageFont.load_default()

    # QR Code bottom-left
    qr_size = 180
    qr_margin = 60
    qr = qrcode.QRCode(
        version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2
    )
    qr.add_data(f"http://localhost:8000/coordinator/verify_certificate/{cert_id}/")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size))
    qr_x = qr_margin
    qr_y = image_height - qr_size - qr_margin
    image.paste(qr_img, (qr_x, qr_y))

    # Pixel positions for text
    positions = {
        "title": (image_width // 2, 300),
        "presented": (image_width // 2, 450),
        "name": (image_width // 2, 550),
        "description": (image_width // 2, 650),
        "event": (image_width // 2, 750)
    }

    # Helper to draw text centered horizontally
    def draw_centered(text, font, pos):
        bbox = draw.textbbox((0,0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = pos[0] - text_width / 2
        y = pos[1]
        draw.text((x, y), text, font=font, fill=(0,0,0))

    # Draw texts
    draw_centered("Certificate of Participation", font_bold_title, positions["title"])
    draw_centered("This certificate is presented to", font_bold_subtitle, positions["presented"])
    draw_centered(name, font_name, positions["name"])
    draw_centered("has successfully participated in", font_bold_subtitle, positions["description"])
    draw_centered(f"The event {event_name}", font_event, positions["event"])

    # Save PDF
    output_dir = 'media/certificates'
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'{name.replace(" ", "_")}_attended_certificate.pdf')
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(pdf_path, "PDF")
    return pdf_path.replace("media/", "")


def generate_certificate_passed_pdf(name, event_name, cert_id):
    template_path = 'static/certificate.jpg'
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size

    # Fonts
    font_path_light = 'static/Fonts/poppins/Poppins-Light.ttf'
    font_path_bold = 'static/Fonts/poppins/Poppins-Bold.ttf'
    try:
        font_name = ImageFont.truetype(font_path_light, 70)
        font_event = ImageFont.truetype(font_path_light, 50)
        font_bold_title = ImageFont.truetype(font_path_bold, 80)
        font_bold_subtitle = ImageFont.truetype(font_path_bold, 50)
    except OSError:
        font_name = font_event = font_bold_title = font_bold_subtitle = ImageFont.load_default()

    # QR Code bottom-left
    qr_size = 180
    qr_margin = 60
    qr = qrcode.QRCode(
        version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=2
    )
    qr.add_data(f"http://localhost:8000/coordinator/verify_certificate/{cert_id}/")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size))
    qr_x = qr_margin
    qr_y = image_height - qr_size - qr_margin
    image.paste(qr_img, (qr_x, qr_y))

    # Pixel positions for text
    positions = {
        "title": (image_width // 2, 300),
        "presented": (image_width // 2, 450),
        "name": (image_width // 2, 550),
        "description": (image_width // 2, 650),
        "event": (image_width // 2, 750),
        "event_name": (image_width // 2, 800)   
    }

    def draw_centered(text, font, pos):
        bbox = draw.textbbox((0,0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = pos[0] - text_width / 2
        y = pos[1]
        draw.text((x, y), text, font=font, fill=(0,0,0))

    draw_centered("Certificate of Achievement", font_bold_title, positions["title"])
    draw_centered("This certificate is awarded to", font_bold_subtitle, positions["presented"])
    draw_centered(name, font_name, positions["name"])
    draw_centered("has successfully completed the event", font_bold_subtitle, positions["description"])
    draw_centered(f"{event_name}", font_event, positions["event_name"])

    # Save PDF
    output_dir = 'media/certificates'
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'{name.replace(" ", "_")}_passed_certificate.pdf')
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(pdf_path, "PDF")
    return pdf_path.replace("media/", "")
