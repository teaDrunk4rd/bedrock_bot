from buttons import Buttons
from config import Config
from controllers.controller import Controller
from db.db import db
from db.models.picture import Picture
from db.models.picture_status import PictureStatus
from db.models.settings import Settings
from db.models.user import User
from media_types import MediaTypes


class ControllerScreens(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.screen_check),
                'admin': lambda vk, event: self.check_screen_first(vk, event),
                'editor': lambda vk, event: self.check_screen_first(vk, event)
            },
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.screen_confirm),
                'admin': lambda vk, event: self.confirm_screen(vk, event),
                'editor': lambda vk, event: self.confirm_screen(vk, event)
            },
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.screen_reject),
                'admin': lambda vk, event: self.reject_screen(vk, event),
                'editor': lambda vk, event: self.reject_screen(vk, event)
            },
            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.comment_screen_reject),
                'admin': lambda vk, event: self.comment_screen_reject_button(vk, event),
                'editor': lambda vk, event: self.comment_screen_reject_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.comment_screen_reject),
                'admin': lambda vk, event: self.comment_screen_reject(vk, event),
                'editor': lambda vk, event: self.comment_screen_reject(vk, event)
            },

            {
                'condition': lambda vk, event: Controller.check_payload(event, Buttons.send_screen) and
                                               self.check_access(Settings.screen, event.user_id),
                'main': lambda vk, event: self.send_screen_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.send_screen),
                'main': lambda vk, event: self.send_screen(vk, event)
            }
        ]

    def __get_pics(self):
        return db.session.query(Picture).filter(Picture.status_id == PictureStatus.not_checked).order_by(Picture.id).all()

    def __over(self, vk, event):
        buttons_access_key = 'admin' if event.user_id in Config.admin_ids else 'editor'
        vk.send(event.user_id, 'картинки закончились', self.main_menu_buttons[buttons_access_key])

    def check_screen_first(self, vk, event):
        pics = self.__get_pics()
        if any(pics):
            vk.send(event.user_id, 'сейчас по очереди я буду скидывать тебе скрины. твоя задача — принимать или отклонять их.\n'
                                   'если принимаешь, то +1 балл челу, если отклоняешь, то 0 баллов.\n'
                                   'в сообщении я прикрепляю сам скрин, пересылаю сообщение от которого скрин был взят и '
                                   'указываю список ссылок на предыдущие скрины чела, чтобы ты мог сравнить их')
            self.check_screen(vk, event)
        else:
            self.__over(vk, event)

    def check_screen(self, vk, event):  # TODO: улучшить, чтобы несколько админов могли проверять фото!
        user = db.get_user(event.user_id)
        db.update(user, {User.path: ''})
        pictures = self.__get_pics()
        if any(pictures):
            picture = pictures[0]
            previous_photos = '\n'.join([
                photo.url for photo in
                db.session.query(Picture).filter(
                    Picture.user_id == picture.user_id, Picture.status_id == PictureStatus.confirmed).all()
            ])
            message = f'предыдущие фотокарточки:\n{previous_photos}' if previous_photos else f'этот новенький'
            message += f'\nтекущая фотокарточка:\n{picture.url}'
            vk.send(
                event.user_id, message,
                [[Buttons.screen_confirm, Buttons.screen_reject],
                 [Buttons.comment_screen_reject, Buttons.to_main]],
                picture.message_id,
            )
        else:
            self.__over(vk, event)

    def confirm_screen(self, vk, event):
        pictures = self.__get_pics()
        if any(pictures):
            picture = pictures[0]
            picture.status_id = PictureStatus.confirmed
            picture.user.scores = picture.user.scores + 1
            db.session.commit()

            scores_plural = ControllerScreens.plural_form(picture.user.scores, 'очко', 'очка', 'очков')
            vk.send(picture.user_id, f'поздравляю, один из твоих скринов приняли. '
                                     f'на данный момент у тебя {picture.user.scores} {scores_plural}',
                    forward_messages=picture.message_id)
            self.check_screen(vk, event)
        else:
            self.__over(vk, event)

    def reject_screen(self, vk, event):
        pictures = self.__get_pics()
        if any(pictures):
            picture = pictures[0]
            picture.status_id = PictureStatus.rejected
            db.session.commit()

            vk.send(picture.user_id, 'твой скрин не приняли. проверь его, может с ним что-то не так?',
                    forward_messages=picture.message_id)
            self.check_screen(vk, event)
        else:
            self.__over(vk, event)

    @staticmethod
    def comment_screen_reject_button(vk, event):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: Buttons.get_key(Buttons.comment_screen_reject)})
        vk.send(event.user_id, 'давай комментарий', [[Buttons.change_command(Buttons.to_main, Buttons.screen_check)]])

    def comment_screen_reject(self, vk, event):
        pictures = self.__get_pics()
        if any(pictures):
            picture = pictures[0]
            picture.status_id = PictureStatus.rejected
            picture.comment = event.text
            db.session.commit()

            vk.send(picture.user_id, f'твой скрин не приняли. {event.text}',
                    forward_messages=picture.message_id)
            self.check_screen(vk, event)
        else:
            self.__over(vk, event)

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
                vk.send(event.user_id, Config.user_error_message)
        else:
            vk.send(event.user_id, 'что-то не вижу картинки в твоем сообщении')
