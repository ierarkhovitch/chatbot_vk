# -*- coding: utf-8 -*-

GROUP_ID = '194123454'
TOKEN = 'fa16125f7caa878fcce5b1bd655692bb505af881287bea34c4e43864e418aaf75f846dd76e8d442a1d329'

LIST_OF_FLIGHTS = [
    {
        "Москва": {
            "Киев": ["02-09-2020", "04-09-2020", "09-09-2020", "11-09-2020", "14-09-2020", "18-09-2020",
                     "23-09-2020", "25-09-2020", "30-09-2020", "02-09-2020", "09-09-2020", "09-09-2020",
                     "14-09-2020", "16-09-2020", "21-09-2020", "23-09-2020", "28-09-2020", "30-09-2020"],
            "Берлин": ["05-09-2020", "09-09-2020", "09-09-2020", "11-09-2020", "13-09-2020", "15-09-2020",
                       "17-09-2020", "29-09-2020", "05-09-2020", "09-09-2020", "09-09-2020", "10-09-2020"],
            "Париж": ["10-09-2020", "20-09-2020", "10-09-2020", "20-09-2020", "10-09-2020", "20-09-2020"]
        },
        "Киев": {
            "Москва": ["01-09-2020", "03-09-2020", "09-09-2020", "10-09-2020", "15-09-2020", "17-09-2020",
                       "22-09-2020", "24-09-2020", "29-09-2020", "01-09-2020", "09-09-2020", "09-09-2020",
                       "13-09-2020", "15-09-2020", "20-09-2020", "22-09-2020", "27-09-2020", "29-09-2020"],
            "Берлин": ["31-05-2020", "02-09-2020", "05-09-2020", "09-09-2020", "09-09-2020", "09-09-2020",
                       "11-09-2020", "13-09-2020", "15-09-2020", "17-09-2020", "18-09-2020", "20-09-2020",
                       "25-09-2020", "30-09-2020", "09-09-2020", "09-09-2020", "09-09-2020", "11-09-2020"]
        },
        "Берлин": {
            "Москва": ["09-09-2020", "09-09-2020", "10-09-2020", "12-09-2020", "14-09-2020", "16-09-2020",
                       "18-09-2020", "30-09-2020", "09-09-2020", "09-09-2020", "09-09-2020", "11-09-2020"],
            "Киев": ["01-09-2020", "03-09-2020", "09-09-2020", "09-09-2020", "09-09-2020", "10-09-2020",
                     "12-09-2020", "14-09-2020", "16-09-2020", "18-09-2020", "19-09-2020", "21-09-2020",
                     "26-09-2020", "01-09-2020", "09-09-2020", "09-09-2020", "10-09-2020", "12-09-2020"],
            "Париж": ["31-05-2020", "02-09-2020", "05-09-2020", "09-09-2020", "09-09-2020", "09-09-2020",
                      "11-09-2020", "13-09-2020", "15-09-2020", "17-09-2020", "18-09-2020", "20-09-2020",
                      "25-09-2020", "30-09-2020", "09-09-2020", "09-09-2020", "09-09-2020", "11-09-2020"]
        },
        "Париж": {
            "Москва": ["11-09-2020", "21-09-2020", "11-09-2020", "21-09-2020", "11-09-2020", "21-09-2020"],
            "Берлин": ["01-09-2020", "03-09-2020", "09-09-2020", "09-09-2020", "09-09-2020", "10-09-2020",
                       "12-09-2020", "14-09-2020", "16-09-2020", "18-09-2020", "19-09-2020", "21-09-2020",
                       "26-09-2020", "01-09-2020", "09-09-2020", "09-09-2020", "10-09-2020", "12-09-2020"]
        },
    }
]

INTENTS = [
    {
        "name": "Приветствие",
        "tokens": {"привет", "здравству", "здоров", "hi", "hello"},
        "scenario": None,
        "answer": "Здравствуйте! Я помогу вам с бронированием билетов на самолёт в нужные для вас даты!"
    },
    {
        "name": "Помощь",
        "tokens": {"/help", "help", "помощь", "помоги", "памаги"},
        "scenario": None,
        "answer": "Я помогу вам в выборе и бронировнии билетов на авиарейсы. \n"
                  "Для бронирования вам необходимо написать мне с просьбой о бронировании"
    },
    {
        "name": "Бронирование",
        "tokens": {"/ticket", "ticket", "бронир", "бронь"},
        "scenario": 'ticket',
        "answer": None
    }
]

SCENARIOS = {
    'ticket': {
        "first_step": "step1",
        "steps": {
            "step1": {
                "text": "Введите своё имя.",
                "failure_text": f"Имя введено не корректно",
                "handler": "handle_name",
                "next_step": "step2"
            },
            "step2": {
                "text": "Введите свою почту.",
                "failure_text": f"Почта введена не корректно",
                "handler": "handle_email",
                "next_step": "step3"
            },
            "step3": {
                "text": "Укажите город отправления.",
                "failure_text": f"Город не найден! Города в которые есть рейсы:\n"
                                f"{', '.join([city for city in LIST_OF_FLIGHTS[0]])}",
                "handler": "handle_city",
                "next_step": "step4"
            },
            "step4": {
                "text": "Укажите город назначения.",
                "failure_text": f"Город не найден! Города в которые есть рейсы:\n"
                                f"{', '.join([city for city in LIST_OF_FLIGHTS[0]])}",
                "handler": "handle_city",
                "next_step": "step5"
            },
            "step5": {
                "text": "Укажите дату вылета в формате дд-мм-гггг. Пример: 21-05-2020\n"
                        "Введенная дата не должна быть раньше текущей даты",
                "failure_text": "Дата введена не корректно",
                "handler": "handle_date",
                "next_step": "step6"
            },
            "step6": {
                "text": "",
                "failure_text": "Не верно выбранная дата",
                "handler": "select_date_handler",
                "next_step": "step7"
            },
            "step7": {
                "text": "Выберете количество пассажиров. Количество пассажиров не должно превышать 5!",
                "failure_text": "Не верное количество",
                "handler": "passengers_handler",
                "next_step": "step8"
            },
            "step8": {
                "text": "Оставьте комментарий к бронированию.",
                "failure_text": "",
                "handler": "comment",
                "next_step": "step9"
            },
            "step9": {
                "text": "Подтвердите правильность данных (Да или Нет):\nГород отправления {departure}\n"
                        "Город назначения {destination}\nДата вылета {date}\nКоличество пассажиров {passengers}\n"
                        "Комментарий к бронированию:\n{comment}",
                "failure_text": "Необходимо написать <Да> или <Нет>",
                "handler": "confirmation",
                "next_step": "step10"
            },
            "step10": {
                "text": "Укажите номер личного телефона.",
                "failure_text": "Не верный формат номера",
                "handler": "mobile_number_handler",
                "next_step": "step11"
            },
            "step11": {
                "text": "Спасибо за бронирование!\n"
                        "В случае изменений в рейсе мы свяжемся с вами по указанному телефону!",
                "image": "generate_ticket_handler",
                "failure_text": None,
                "handler": None,
                "next_step": None
            }
        }
    }
}

DEFAULT_ANSWER = "Не знаю как на это ответить.\n" \
                 "Для подробной справки по работе чат-бота попросите помощи у меня или напишите /help"

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    host='',
    database='vk_chat_bot'
)
