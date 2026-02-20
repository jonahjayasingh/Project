import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
def get_font(font_size=30, bold=False):
    try:
        font_path = "certificategenrator/static/font/timesbd.ttf" if bold else "certificategenrator/static/font/times.ttf"
        return ImageFont.truetype(font_path, font_size)
    except:
        return ImageFont.truetype("FreeSerifBold.ttf" if bold else "FreeSerif.ttf", font_size)

def get_bond_certificate(data, template_path="certificategenrator/static/bond_certificate.jpg"):
    # Clean and construct filename
    name_clean = data["name"].strip().replace(" ", "_")
    training_clean = data["course_name"].strip().replace(" ", "_")
    training_clean = training_clean.replace("/", "_")
    output_filename = f"{name_clean}_{training_clean}.pdf"
    output_path = f"certificategenrator/static/media/certificates/{output_filename}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    font_regular = get_font(25, bold=False)
    font_bold = get_font(25, bold=True)

    name = data["name"]
    duration = data["date_range"]
    training = data["course_name"]
    project = data["project_title"]
    try:
        date = data["completed_date"].strftime("%d-%m-%Y")
    except:
        date = datetime.strptime(data["completed_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
    certificate_id = data["certificate_id"]
    start_str, end_str = duration.split(" to ")

    # Convert and reformat each date
    start_rev = datetime.strptime(start_str, "%Y-%m-%d").strftime("%d-%m-%Y")
    end_rev = datetime.strptime(end_str, "%Y-%m-%d").strftime("%d-%m-%Y")

    # Reassembled reversed duration
    duration = f"{start_rev} to {end_rev}"

    draw.text((200, 350), f"Date : {date}", font=font_regular, fill="black")
    draw.text((1100, 350), f"{certificate_id}", font=font_regular, fill="black")

    # Center name between x=400 and x=940
    bbox = draw.textbbox((0, 0), name, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 400 + (940 - 400) // 2
    x = center_x - text_width // 2
    draw.text((x, 610), name, font=font_bold, fill="black")

    # Center duration between 520 and 1000
    bbox = draw.textbbox((0, 0), duration, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 520 + (1000 - 520) // 2
    x = center_x - text_width // 2
    draw.text((x, 680), duration, font=font_regular, fill="black")

    # Center training between 440 and 1180
    bbox = draw.textbbox((0, 0), training, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 440 + (1180 - 440) // 2
    x = center_x - text_width // 2
    draw.text((x, 750), training, font=font_bold, fill="black")

    # Center project between 210 and 1120
    bbox = draw.textbbox((0, 0), project, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 210 + (1120 - 210) // 2
    x = center_x - text_width // 2
    draw.text((x, 825), f'"{project}"', font=font_bold, fill="black")
    #
    # Center signature name between 310 and 750
    bbox = draw.textbbox((0, 0), name, font=font_bold)
    text_width = bbox[2] - bbox[0]
    center_x = 310 + (750 - 310) // 2
    x = center_x - text_width // 2
    draw.text((x, 1000), name, font=font_bold, fill="black")

    img.save(output_path, "PDF", resolution=100.0)


    return output_filename
