# -*- coding: utf-8 -*-

import re
import datetime
import settings
from generate_ticket import generate_ticket

RE_NAME = re.compile(r"^[\w\-\s]{3,40}$")
RE_EMAIL = re.compile(r"\b[a-zA-Z0-9.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b")
RE_DATE = re.compile(r"[0-9]{2}\-[0-9]{2}\-[0-9]{4}")


def handle_name(text, context):
    match = re.match(RE_NAME, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matches = re.findall(RE_EMAIL, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


def handle_city(text, context):
    list_of_flights = settings.LIST_OF_FLIGHTS[0]
    direction = departure_or_destination(context)
    match = text.capitalize()
    for city in list_of_flights:
        if match.startswith(city[:-1]):
            context[direction] = city
            return True
    return False


def departure_or_destination(context):
    if 'departure' in context:
        return 'destination'
    else:
        return 'departure'


def handle_date(text, context):
    match = re.match(RE_DATE, text)
    if match:
        try:
            date_select = datetime.datetime.strptime(match.string, "%d-%m-%Y").date()
        except:
            return False
        if date_select > datetime.date.today():
            context['date'] = text
            return dispatcher(context)
    else:
        return False


def dispatcher(context):
    list_departure_day = []
    list_date = settings.LIST_OF_FLIGHTS[0][context['departure']][context['destination']]
    if context['date'] in list_date:
        return True
    else:
        date_select = datetime.datetime.strptime(context['date'], "%d-%m-%Y").date()
        date_today = datetime.date.today()
        min_list = []
        for date in list_date:
            day_of_departure = datetime.datetime.strptime(date, "%d-%m-%Y").date()
            if date_today < day_of_departure < date_select:
                min_list.append(day_of_departure.strftime("%d-%m-%Y"))
        i = 0
        for date in reversed(min_list):
            if i == 5:
                break
            else:
                list_departure_day.append(date)
                i += 1
        context['list_date'] = list_departure_day
        return list_departure_day


def passengers_handler(text, context):
    try:
        if 0 < int(text) < 6:
            context['passengers'] = text
            return True
    except:
        return False


def select_date_handler(text, context):
    try:
        context['date'] = context['list_date'][int(text)]
        return True
    except:
        return False


def comment(text, context):
    context['comment'] = text
    return True


def confirmation(text, context):
    if text.capitalize() == "Да":
        return True
    elif text.capitalize() == "Нет":
        context['confirmation'] = "Нет"
        return False
    else:
        return False


def mobile_number_handler(text, context):
    if text.isdigit():
        context['mobile'] = text
        return True
    else:
        return False


def generate_ticket_handler(text, context):
    return generate_ticket(name=context['name'], mail=context['email'], date=context['date'],
                           departure=context['departure'], destination=context['destination'],
                           passengers=context['passengers'])
