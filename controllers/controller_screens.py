from buttons import Buttons
from db.db import db
from db.models.picture import Picture
from db.models.picture_status import PictureStatus
from db.models.user import User
from media_types import MediaTypes


def send_screen_button(vk, event, message, buttons=None):
    user = db.get_user(event.user_id)
    db.update(user, {User.path: Buttons.get_key(Buttons.send_screen)})
    vk.send(event.user_id, message, buttons)


def send_screen(vk, event):
    if event.attachments != {}:
        all_photos, photos_count = True, 0

        for i in range(10):
            if event.attachments.get(f'attach{i + 1}') is not None:
                if event.attachments.get(f'attach{i + 1}_type') == MediaTypes.photo:
                    db.add(Picture(event.user_id, PictureStatus.not_checked, event.attachments.get(f'attach{i + 1}'), event.message_id))
                    photos_count = photos_count + 1
                else:
                    all_photos = False
            else:
                break
        if all_photos and photos_count == 1:
            vk.send(event.user_id, 'отлично, отпишу после того как проверят твою фотокарточку')
        elif all_photos:
            vk.send(event.user_id, 'отлично, отпишу после того как проверят все твои фотокарточки')
        elif not all_photos and photos_count != 0:
            vk.send(event.user_id, 'в твоих вложениях есть что-то кроме скринов. скрины я возьму, остальное оставь себе')
        else:
            vk.send(event.user_id, 'я же просил скрины')
    else:
        vk.send(event.user_id, 'что-то не вижу картинки в твоем сообщении')


def check_screen_first(vk, event):
    vk.send(event.user_id, 'сейчас по очереди я буду скидывать тебе скрины. твоя задача - принимать или отклонять их.\n'
                           'если принимаешь, то +1 балл челу, если отклоняешь, то +0 баллов.\n'
                           'в сообщении я прикрепляю сам скрин, пересылаю сообщение от которого скрин был взят и '
                           'указываю список ссылок на предыдущиие скрины чела, чтобы ты мог сравнить их')
    check_screen(vk, event)


def check_screen(vk, event):  # TODO: улучшить, чтобы несколько админов могли проверять фото?
    pictures = db.session.query(Picture).filter(Picture.status_id == PictureStatus.not_checked).order_by(Picture.id).all()
    if any(pictures):
        picture = pictures[0]
        previous_photos = 'Previous photos links\n'
        vk.send(
            event.user_id, previous_photos,
            [[Buttons.screen_confirm, Buttons.screen_reject],
             [Buttons.to_main]],
            #picture.message_id,
            attachments=[f'photo-322270793_457251893']
        )
    else:
        vk.send(event.user_id, 'картинки закончились')
