from io import BytesIO

import requests
from PIL import Image

from generate_ticket import generate_ticket

ticket_file = generate_ticket('Дмитрий', 'test@testovitch.com', '27-09-2020', 'Москва', 'Берлин', '5')
# ticket_file = ticket_file.read()
ticket_file = Image.open(ticket_file)

# response = requests.get(url=f'https://api.adorable.io/avatars/150/test@testovitch.com')
# avatar_file_like = BytesIO(response.content)
# avatar = Image.open(avatar_file_like)
with open('ticket_file.png', 'wb') as f:
    ticket_file.save(f, 'png')