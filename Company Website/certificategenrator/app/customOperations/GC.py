import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime,date

def get_font(font_size=30, bold=False):
    try:
        font_path = 'certificategenrator/static/font/Poppins-SemiBold.ttf' if bold else 'certificategenrator/static/font/Poppins-Regular.ttf'
        return ImageFont.truetype(font_path, font_size)
    except:
        return ImageFont.truetype("FreeSerifBold.ttf" if bold else "FreeSerif.ttf", font_size)

def generate_certificate(data, template_path="certificategenrator/static/certificate.jpeg"):
    # Clean and construct filename
    name_clean = data["name"].strip().replace(" ", "_")

    training_clean = data["course_name"].strip().replace("/", "_")
    training_clean = training_clean.replace(" ", "_")
    output_filename = f"{name_clean}_{training_clean}.pdf"
    output_path = f"certificategenrator/static/media/certificates/{output_filename}"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    font_regular = get_font(35, bold=False)
    font_bold = get_font(35, bold=True)


    name = data["name"]
    duration = data["duration"]
    course_name = data["course_name"]
    completed_date = data["completed_date"]
    if isinstance(completed_date, str):
        completed_date = datetime.strptime(completed_date, "%Y-%m-%d")
    elif isinstance(completed_date, date):
        completed_date = datetime.combine(completed_date, datetime.min.time())
    completed_date = completed_date.strftime("%d %B, %Y")
    certificate_id = data["certificate_id"]

    draw.text((550, 920), f"{completed_date}", font=font_regular, fill="black")
    draw.text((380, 880), f"{certificate_id}", font=font_regular, fill="black")

    # Center name between x=400 and x=940
    bbox = draw.textbbox((0, 0), name, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 830 + (1480 - 830) // 2
    x = center_x - text_width // 2
    draw.text((x, 500), name, font=font_bold, fill="black")

    # Center duration between 520 and 1000
    bbox = draw.textbbox((0, 0), duration, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 880 + (1230 - 880) // 2
    x = center_x - text_width // 2
    draw.text((x, 580), duration, font=font_bold, fill="black")

    # Center training between 440 and 1180
    bbox = draw.textbbox((0, 0), course_name, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 450 + (1080 - 450) // 2
    x = center_x - text_width // 2
    draw.text((x, 650), course_name, font=font_bold, fill="black")

    # Center signature name between 310 and 750
    bbox = draw.textbbox((0, 0), name, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 550 + (1200 - 550) // 2
    x = center_x - text_width // 2
    draw.text((x, 750), name, font=font_bold, fill="black")

    img.save(output_path, "PDF", resolution=100.0)
    return output_path.split("/")[-1]


