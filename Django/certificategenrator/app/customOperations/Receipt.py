import os
from PIL import Image, ImageDraw, ImageFont
from num2words import num2words

def generate_receipt(data, input_path="certificategenrator/static/Receipt.png", output_path=None):
    course_name = data["course_name"].replace("/", "_")

    if output_path is None:
        filename = f"{data['name'].replace(' ', '')}_{course_name.replace(' ', '')}_{data['student_id']}.pdf"
        output_dir = "certificategenrator/static/media/receipt"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

    try:
        img = Image.open(input_path)
        draw = ImageDraw.Draw(img)

        font_config = {
            'bold': {'name': 'certificategenrator/static/font/arialbd.ttf', 'size': 90, 'fallback': 'certificategenrator/static/font/arial.ttf'},
            'regular': {'name': 'certificategenrator/static/font/arial.ttf', 'size': 60, 'fallback': None}
        }

        fields = [
            {'text': data['name'], 'font': font_config['regular'], 'position': (750, 740)},
            {'text': data['course_name'], 'font': font_config['regular'], 'position': (350, 870)},
            {'text': str(data['rupees']), 'font': font_config['bold'], 'position': (200, 1170)},
            {'text': " ".join([x.capitalize() for x in num2words(data['rupees']).split(" ")]), 'font': font_config['regular'], 'position': (420, 1000)},
            {'text': data["date"], 'font': font_config['regular'], 'position': (1620, 540), 'font_size': 40},
            {'text': data["reg_no"], 'font': font_config['regular'], 'position': (230, 630)},
        ]

        for field in fields:
            font_size = field.get('font_size', field['font']['size'])
            try:
                font = ImageFont.truetype(field['font']['name'], font_size)
            except IOError:
                fallback = field['font'].get('fallback')
                if fallback:
                    font = ImageFont.truetype(fallback, font_size)
                else:
                    font = ImageFont.load_default()

            x, y = field['position']
            draw.text((x, y), field['text'], font=font, fill='black')
        if os.path.exists(output_path):
            os.remove(output_path)
        img.save(output_path)
        return filename

    except Exception as e:
        return False
