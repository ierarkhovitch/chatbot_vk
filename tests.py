# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent
from bot import Bot
import settings
from generate_ticket import generate_ticket


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):
    RAW_EVENT = {'type': 'message_new',
                 'object': {'message': {'date': 1588094404, 'from_id': 30158779, 'id': 376, 'out': 0,
                                        'peer_id': 30158779, 'text': 'Привет', 'conversation_message_id': 366,
                                        'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [],
                                        'is_hidden': False},
                            'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link',
                                                               'open_photo'],
                                            'keyboard': True, 'inline_keyboard': True, 'carousel': True, 'lang_id': 0}},
                 'group_id': 194123454, 'event_id': '1a7620e1107b033388e9848b7181deebcc7b6118'}
    USER = [{'first_name': 'Дмитрий'}]
    INPUTS = [
        "бот",
        "Привет",
        "помощь",
        "бронь",
        "Дмитрий",
        "test@testovitch.com",
        "Саратов",
        "Москва",
        "Прага",
        "Берлин",
        "20/06/2020",
        "28-09-2020",
        "7",
        "0",
        "10",
        "3",
        "Позвонить при успешном бронировании",
        "Не уверен",
        "Да",
        "8238761237812",
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.SCENARIOS['ticket']['steps']['step1']['text'],
        settings.SCENARIOS['ticket']['steps']['step2']['text'],
        settings.SCENARIOS['ticket']['steps']['step3']['text'],
        settings.SCENARIOS['ticket']['steps']['step3']['failure_text'],
        settings.SCENARIOS['ticket']['steps']['step4']['text'],
        settings.SCENARIOS['ticket']['steps']['step4']['failure_text'],
        settings.SCENARIOS['ticket']['steps']['step5']['text'],
        settings.SCENARIOS['ticket']['steps']['step5']['failure_text'],
        'На заданную дату нет рейса, выберите номер даты из ближайших к заданной дате:\n0: 10-09-2020\n1: 09-09-2020\n'
        '2: 09-09-2020\n3: 17-09-2020\n4: 15-09-2020\n',
        settings.SCENARIOS['ticket']['steps']['step6']['failure_text'],
        settings.SCENARIOS['ticket']['steps']['step7']['text'],
        settings.SCENARIOS['ticket']['steps']['step7']['failure_text'],
        settings.SCENARIOS['ticket']['steps']['step8']['text'],
        settings.SCENARIOS['ticket']['steps']['step9']['text'].format(departure='Москва', destination='Берлин',
                                                                      date='10-09-2020', passengers='3',
                                                                      comment='Позвонить при успешном бронировании'),
        settings.SCENARIOS['ticket']['steps']['step9']['failure_text'],
        settings.SCENARIOS['ticket']['steps']['step10']['text'],
        settings.SCENARIOS['ticket']['steps']['step11']['text']
    ]

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['message']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()
        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXPECTED_OUTPUTS

    def test_image_generation(self):
        with open('files/test@testovitch.png', 'rb') as avatar_file:
            avatar_mock = Mock()
            avatar_mock.content = avatar_file.read()

        with patch('requests.get', return_value=avatar_mock):
            ticket_file = generate_ticket('Дмитрий', 'test@testovitch.com', '27-09-2020', 'Москва', 'Берлин', '5')

        with open('files/ticket_example.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
            ticket_bytes = ticket_file.read()
            assert isinstance(ticket_bytes, bytes) and len(ticket_bytes) > len(expected_bytes) * 0.2

