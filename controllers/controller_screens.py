from buttons import Buttons
from config import Config
from controllers.controller import Controller
from db.db import db
from db.models.picture import Picture
from db.models.picture_status import PictureStatus
from db.models.user import User
from media_types import MediaTypes


class ControllerScreens(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.screen_check),
                'privilege': lambda vk, event: self.check_screen_first(vk, event)
            },
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.screen_confirm),
                'privilege': lambda vk, event: self.confirm_screen(vk, event)
            },
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.screen_reject),
                'privilege': lambda vk, event: self.reject_screen(vk, event)
            },

            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.send_screen),
                'main': lambda vk, event: self.send_screen_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.send_screen),
                'main': lambda vk, event: self.send_screen(vk, event)
            }
        ]

    @staticmethod
    def check_screen_first(vk, event):
        vk.send(event.user_id, 'сейчас по очереди я буду скидывать тебе скрины. твоя задача — принимать или отклонять их.\n'
                               'если принимаешь, то +1 балл челу, если отклоняешь, то +0 баллов.\n'
                               'в сообщении я прикрепляю сам скрин, пересылаю сообщение от которого скрин был взят и '
                               'указываю список ссылок на предыдущиие скрины чела, чтобы ты мог сравнить их')
        ControllerScreens.check_screen(vk, event)

    @staticmethod
    def check_screen(vk, event):  # TODO: улучшить, чтобы несколько админов могли проверять фото?
        pictures = db.session.query(Picture).filter(Picture.status_id == PictureStatus.not_checked).order_by(Picture.id).all()
        if any(pictures):
            picture = pictures[0]
            previous_photos = '\n'.join([
                photo.url for photo in
                db.session.query(Picture).filter(
                    Picture.user_id == picture.user_id, Picture.status_id != PictureStatus.not_checked).all()
            ])
            message = f'предыдущие фотокарточки:\n{previous_photos}' if previous_photos else f'этот новенький'
            message += f'\nтекущая фотокарточка:\n{picture.url}'
            vk.send(
                event.user_id, message,
                [[Buttons.screen_confirm, Buttons.screen_reject],
                 [Buttons.to_main]],
                picture.message_id,
            )
        else:
            vk.send(event.user_id, 'картинки закончились')

    @staticmethod
    def confirm_screen(vk, event):
        pictures = db.session.query(Picture).filter(Picture.status_id == PictureStatus.not_checked).order_by(Picture.id).all()
        if any(pictures):
            picture = pictures[0]
            picture.status_id = PictureStatus.confirmed
            picture.user.scores = picture.user.scores + 1
            db.session.commit()

            scores_plural = ControllerScreens.plural_form(picture.user.scores, 'очко)', 'очка', 'очков')
            vk.send(picture.user_id, f'поздравляю, один из твоих скринов приняли. '
                                     f'на данный момент у тебя {picture.user.scores} {scores_plural}',
                    forward_messages=picture.message_id)
            ControllerScreens.check_screen(vk, event)
        else:
            vk.send(event.user_id, 'картинки закончились')

    @staticmethod
    def reject_screen(vk, event):
        pictures = db.session.query(Picture).filter(Picture.status_id == PictureStatus.not_checked).order_by(Picture.id).all()
        if any(pictures):
            picture = pictures[0]
            picture.status_id = PictureStatus.rejected
            db.session.commit()

            vk.send(picture.user_id, f'твой скрин не приняли. проверь его, может с ним что-то не так?',
                    forward_messages=picture.message_id)
            ControllerScreens.check_screen(vk, event)  # TODO: комментарий от админа
        else:
            vk.send(event.user_id, 'картинки закончились')

    @staticmethod
    def send_screen_button(vk, event):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: Buttons.get_key(Buttons.send_screen)})
        vk.send(event.user_id, 'жду твой скрин, передам его админу', [[Buttons.to_main]])

    @staticmethod
    def send_screen(vk, event):
        if event.attachments != {}:
            all_photos, duplicates_count, confirmed_count = True, 0, 0
            attachments = vk.get_message_attachments(event.message_id)

            if attachments:
                for attachment in attachments:
                    if attachment['type'] == MediaTypes.photo:
                        url = MediaTypes.get_max_quality_url(attachment['photo']['sizes'])
                        name = url.split('/')[-1]
                        if db.session.query(Picture).filter(Picture.name == name).first():  # Ахтунг: воможен баг
                            duplicates_count = duplicates_count + 1
                        else:
                            db.add(Picture(event.user_id, PictureStatus.not_checked, url, name, event.message_id))
                            confirmed_count = confirmed_count + 1
                    else:
                        all_photos = False

                if all_photos:
                    if confirmed_count == 1 and duplicates_count == 0:
                        vk.send(event.user_id, 'отлично, отпишу после того как проверят твою фотокарточку')
                    elif confirmed_count + duplicates_count == 1:
                        vk.send(event.user_id, f'не, такую фотку я уже видел, ее не приму')
                    else:
                        photos_plural = ControllerScreens.plural_form(confirmed_count, 'фотокарточку', 'фотокарточки', 'фотокарточек')
                        if duplicates_count == 0:
                            vk.send(event.user_id, f'отлично, отпишу после того как проверят все {confirmed_count} {photos_plural}')
                        elif duplicates_count != 0:
                            vk.send(event.user_id, f'ты дублируешь фотки, я зачел {confirmed_count} {photos_plural}')
                elif not all_photos and confirmed_count + duplicates_count != 0:
                    if confirmed_count != 0 and duplicates_count == 0:
                        vk.send(event.user_id, 'в твоих вложениях есть что-то кроме скринов. скрины я возьму, остальное оставь себе')
                    elif duplicates_count != 0:
                        photos_plural = ControllerScreens.plural_form(confirmed_count, 'фотокарточку', 'фотокарточки', 'фотокарточек')
                        vk.send(event.user_id, f'ты дублируешь фотки, я зачел {confirmed_count} {photos_plural}')
                else:
                    vk.send(event.user_id, 'я же просил скрины')
            else:
                vk.send(event.user_id, Config.error_message)
        else:
            vk.send(event.user_id, 'что-то не вижу картинки в твоем сообщении')

    @staticmethod
    def plural_form(n, form1, form2, form5):
        n = abs(n) % 100
        n1 = n % 10
        if 10 < n < 20:
            return form5
        if 1 < n1 < 5:
            return form2
        if n1 == 1:
            return form1
        return form5
