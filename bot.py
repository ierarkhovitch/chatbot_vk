# -*- coding: utf-8 -*-

import requests
from pony.orm import db_session
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import random
import vk_api
import handlers
from models import UserState, Registration

try:
    import settings
except ImportError:
    exit("Need copy settings.py.default settings.py and set token")

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",
                                                  datefmt="%d-%m-%Y %H:%M:%S"))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",
                                                datefmt="%d-%m-%Y %H:%M"))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    """
    Сценарий регистрации на конференцию "Skillbox Conf" через vk.com.
    Use python 3.8

    Поддерживает ответы на вопосы про дату, место проведения и сценарий регистрации:
    - спрашиваем имя
    - спрашиваем email
    - говорим об успешной регистрации
    Если шаг не пройден, задаем уточняющий ворос пока шаг не будет пройден.
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(vk=self.vk, group_id=self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        """Запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception("Ошибка обработки события")

    @db_session
    def on_event(self, event):
        """
        Отправляет текстовое сообщение обратно
        :param event: VkBotMessageEvent object
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.debug(f"Нет возможности обаботать событие: {event.type}")
            return

        user_id = str(event.object['message']['peer_id'])
        text = event.object['message']['text']
        state = UserState.get(user_id=user_id)

        if state is not None:
            self.continue_scenario(text, state, user_id)
        else:
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        self.send_text(intent['answer'], user_id)
                    else:
                        self.start_scenario(user_id, intent['scenario'], text)
                    break
            else:
                self.send_text(settings.DEFAULT_ANSWER, user_id)

    def send_text(self, text_to_send, user_id):
        """
        :param text_to_send: текст отправки сообщения
        :param user_id: id пользователя
        """
        self.api.messages.send(message=text_to_send,
                               random_id=random.getrandbits(64),
                               peer_id=user_id)

    def send_image(self, image, user_id):
        """
        :param image: билет
        :param user_id: id пользователя
        """
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)

        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.api.messages.send(attachment=attachment,
                               random_id=random.getrandbits(64),
                               peer_id=user_id)

    def send_step(self, step, user_id, text, context, text_to_send):
        """
        :param step: следующий шаг
        :param user_id: id пользователя
        :param text: сообщение пользователя
        :param context: данные пользователся
        :param text_to_send: текст отправки сообщения
        """
        if 'image' in step:
            handler = getattr(handlers, step['image'])
            image = handler(text, context.context)
            self.send_image(image, user_id)
            self.send_text(text_to_send, user_id)
            context.delete()
        else:
            self.send_text(text_to_send, user_id)

    def start_scenario(self, user_id, scenario_name, text):
        """
        :param user_id: id пользователя
        :param scenario_name: имя сценария
        :return: текст ответа
        """
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.send_step(step, user_id, text, context={}, text_to_send=text_to_send)
        UserState(user_id=user_id, scenario_name=scenario_name, step_name=first_step, context={})

    def city_handler(self, state, steps, step):
        """
        :param state:  параметры пользователя
        :param steps: все шаги
        :param step: текущий шаг
        :return: текст отправки сообщения
        """
        if not state.context['destination'] in settings.LIST_OF_FLIGHTS[0][state.context['departure']]:
            text_to_send = "Между городами нет рейсов.\n\n" \
                           "Для бронирования вам необходимо написать мне с просьбой о бронировании"
            state.delete()
        else:
            state.step_name = step['next_step']
            text_to_send = steps[state.step_name]['text']
        return text_to_send

    def date_handler(self, response_from_the_handler, state, steps, step):
        """
        :param response_from_the_handler: ответ от обработчика
        :param state: параметры пользователя
        :param steps: все шаги
        :param step: текущий шаг
        :return: текст отправки сообщения
        """
        if isinstance(response_from_the_handler, list):
            text_to_send = "На заданную дату нет рейса, выберите номер даты из ближайших к заданной дате:\n"
            for number, date in enumerate(response_from_the_handler):
                text_to_send += f"{number}: {date}\n"
            state.step_name = step['next_step']
        elif response_from_the_handler:
            state.step_name = 'step7'
            next_step = steps['step7']
            text_to_send = next_step['text'].format(**state.context)
        else:
            text_to_send = step['failure_text'].format(**state.context)
        return text_to_send

    def finish_scenario(self, state):
        Registration(name=state.context['name'], email=state.context['email'],
                     date=state.context['date'],
                     departure=state.context['departure'],
                     destination=state.context['destination'], passengers=state.context['passengers'],
                     comment=state.context['comment'], mobile=state.context['mobile'])
        log.info("Выполнена бронь! Отправление {departure}, прибытие {destination}, дата {date}"
                 .format(**state.context))

    def continue_scenario(self, text, state, user_id):
        """
        :param user_id: id пользователя
        :param text: сообщение пользователя
        :return: текст ответа
        """
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        response_from_the_handler = handler(text=text, context=state.context)
        next_step = steps[step['next_step']]
        if response_from_the_handler:
            text_to_send = next_step['text'].format(**state.context)
            if step['handler'] == 'handle_city' and 'destination' in state.context:
                text_to_send = self.city_handler(state, steps, step)
            elif step['next_step'] == 'step6':
                text_to_send = self.date_handler(response_from_the_handler, state, steps, step)
            elif next_step['next_step']:
                state.step_name = step['next_step']
            else:
                self.finish_scenario(state)
        else:
            if isinstance(response_from_the_handler, list) and len(response_from_the_handler) == 0:
                text_to_send = "Ближайшик рейсов к заданной дате нет!"
            elif step['handler'] == 'confirmation' and 'confirmation' in state.context:
                text_to_send = "Для бронирования вам необходимо написать мне с просьбой о бронировании"
                state.delete()
            else:
                text_to_send = step['failure_text'].format(**state.context)
        self.send_step(next_step, user_id, text, state, text_to_send)


if __name__ == "__main__":
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
