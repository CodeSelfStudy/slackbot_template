"""Fun with Slackbots."""

import re
import os
import json
import requests
from random import randint

from bender.signals import event_received, message_received

WUNDERGROUND_API_KEY = os.environ['WUNDERGROUND_API_KEY']


@event_received.connect
def echo(sender, **kwargs):
    """Logs events to the console."""
    print(kwargs['event']._raw)
    return True


@message_received.connect
def my_name(sender, **kwargs):
    """Responds to 'some text here'."""
    try:
        event = kwargs['event']

        if re.search('some text here', event.text, re.IGNORECASE):
            sender.slack_client.send_message('That\'s my name. :grin:', event.channel)
    except:
        pass


@message_received.connect
def weather(sender, **kwargs):
    """Posts the weather report by US zip code.

    Usage: weather(12345)
    """
    try:
        event = kwargs['event']

        regex = re.compile('weather\((\d{5})\)')
        w = regex.search(event.text)
        if w is not None:
            zipcode = w.groups()[0]
            q = 'http://api.wunderground.com/api/{key}/geolookup/q/{zipcode}.json'.format(
                key=WUNDERGROUND_API_KEY,
                zipcode=zipcode
            )
            res = json.loads(requests.get(q).text)
            weather_path = res['location']['requesturl'].split('/')
            state = weather_path[-2]
            city = weather_path[-1]
            weather_url = 'http://api.wunderground.com/api/{key}/forecast/q/{state}/{city}.json'.format(
                    key=WUNDERGROUND_API_KEY,
                    state=state,
                    city=city
            )
            weather_data = json.loads(requests.get(weather_url).text)
            # Uncomment the next line to view JSON
            # print(weather_data)
            forecast_title = weather_data['forecast']['txt_forecast']['forecastday'][0]['title']
            fcttext = weather_data['forecast']['txt_forecast']['forecastday'][0]['fcttext']
            forecast_icon = weather_data['forecast']['txt_forecast']['forecastday'][0]['icon_url']
            output = '*{}:* {} \n{}'.format(forecast_title, fcttext, forecast_icon)
            sender.slack_client.send_message(output, event.channel)
    except:
        pass


@message_received.connect
def cowsay(sender, **kwargs):
    """Cowsay API integration."""
    try:
        event = kwargs['event']

        regex = re.compile('cowsay\((.*)\)')
        m = regex.search(event.text)
        if m is not None:
            text = m.groups()[0].replace(' ', '%20')
            q = 'http://cowsay.morecode.org/say?message={}&format=text'.format(text)
            output = requests.get(q).text
            sender.slack_client.send_message(output, event.channel)
    except:
        pass


@message_received.connect
def process_message(sender, **kwargs):
    """Sends commands to the command_router if prefixed with `!`."""
    try:
        event = kwargs['event']
        if event.text.startswith('!'):
            command_router(event.text[1:], sender, event.channel)

    except:
        pass

def do_something(sender, channel):
    """Displays some text."""
    try:
        output = """Some text here

        Sit libero temporibus eaque odit deserunt nesciunt? Ipsum fugit odio sunt cupiditate hic numquam suscipit. Mollitia architecto iure nobis earum voluptatibus. Aliquam laboriosam perspiciatis ratione amet quisquam Nobis laboriosam maiores.

        Elit neque provident exercitationem nobis ducimus corrupti! Nemo cupiditate et expedita cum asperiores Explicabo quaerat corporis dolores iure quis? Eaque impedit voluptate quis id tempora. Illum doloremque odio facilis temporibus?
        """
        sender.slack_client.send_message(output, channel)
    except:
        pass

def command_router(command, sender, channel):
    """Routes commands."""
    commands = {
        'importthis': do_something
    }

    command_fn = commands.get(command)
    if command_fn:
        command_fn(sender, channel)
