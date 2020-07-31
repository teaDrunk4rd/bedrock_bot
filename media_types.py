class MediaTypes:
    photo = 'photo'
    video = 'video'
    audio = 'audio'
    doc = 'doc'
    link = 'link'
    market = 'market'
    market_album = 'market_album'
    wall = 'wall'
    wall_reply = 'wall_reply'
    sticker = 'sticker'
    gift = 'gift'
    audiomsg = 'audiomsg'

    __photo_qualities = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']  # порядок убывания по качеству

    @staticmethod
    def get_max_quality_url(sizes):  # TODO: протестить на разных размерах фото
        for quality in MediaTypes.__photo_qualities:
            try:
                return next(iter([
                    size for size in sizes
                    if size['type'] == quality
                ]))['url']
            except StopIteration:
                continue
