from ast import literal_eval
from buttons import Buttons


def any_in(values, message):
    return type(values) is list and any([val for val in values if val in message])


def check_payload(event, key):
    if type(key) is dict:  # is button
        key = Buttons.get_key(key)
    return hasattr(event, 'payload') and literal_eval(event.payload).get('command') == key


def get_button(label, color, payload=''):
    return {
        'action': {
            'type': 'text',
            'payload': payload,
            'label': label
        },
        'color': color
    }


def get_command(key, args=None):
    vk_command = {
        'command': key
    }
    if args:
        vk_command.update({'args': args})
    return vk_command
