# -*- coding: utf-8 -*-

import os
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont


TICKET_TEMPLATE_PATH = os.path.normpath('files/template.png')
TICKET_FONT_PATH = os.path.normpath('files/Roboto-Medium.ttf')
DATE_OFFSET = (290, 80)
NAME_OFFSET = (30, 250)
MAIL_OFFSET = (30, 280)
DEPARTURE_OFFSET = (290, 120)
DESTINATION_OFFSET = (290, 160)
PASSENGERS_OFFSET = (290, 200)
BLACK = (0, 0, 0, 255)
AVATAR_SIZE = 150


def generate_ticket(name, mail, date, departure, destination, passengers):
    """
    Генерация билета
    """
    template = Image.open(TICKET_TEMPLATE_PATH).convert('RGBA')
    font = ImageFont.truetype(TICKET_FONT_PATH, 18)
    draw = ImageDraw.Draw(template)

    draw.text(DATE_OFFSET, 'Дата вылета: ' + date, font=font, fill=BLACK)
    draw.text(NAME_OFFSET, 'Имя: ' + name, font=font, fill=BLACK)
    draw.text(MAIL_OFFSET, 'Email: ' + mail, font=font, fill=BLACK)
    draw.text(DEPARTURE_OFFSET, 'Откуда: ' + departure, font=font, fill=BLACK)
    draw.text(DESTINATION_OFFSET, 'Куда: ' + destination, font=font, fill=BLACK)
    draw.text(PASSENGERS_OFFSET, 'Пассажиров: ' + passengers, font=font, fill=BLACK)

    url = f'https://api.adorable.io/avatars/{AVATAR_SIZE}/{mail}'
    response = requests.get(url=url)
    avatar_file_like = BytesIO(response.content)
    avatar = Image.open(avatar_file_like)
    template.paste(avatar, (30, 80))

    temp_file = BytesIO()
    template.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file

