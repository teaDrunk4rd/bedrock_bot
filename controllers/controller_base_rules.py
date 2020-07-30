from config import Config
from db.models.user import User
from db.db import db


def send_buttons(vk, event, message, buttons=None):
    user = db.get_user(event.user_id)
    db.update(user, {User.path: ''})
    vk.send(event.user_id, message, buttons)


def insult(vk, event, message, buttons=None):
    user = db.get_user(event.user_id)
    if event.user_id not in Config.admin_ids:
        db.update(user, {User.apologies_count: User.apologies_count + 1})
    vk.send(event.user_id, message, buttons)  # TODO: декоратор для этого?


def demand_apology(vk, event, messages_with_ranges):
    user = db.session.query(User).filter(User.user_id == event.user_id).first()
    if event.user_id not in Config.admin_ids and user:
        messages = next(iter([
            msg['messages'] for msg in messages_with_ranges
            if type(msg['range']) is range and user.apologies_count in msg['range'] or type(msg['range']) is str
        ]))
        vk.send(event.user_id, messages)


def get_apology(vk, event, message, buttons=None):
    user = db.session.query(User).filter(User.user_id == event.user_id)
    if user.first():
        db.update(user, {User.apologies_count: 0})
        vk.send(event.user_id, message, buttons)
