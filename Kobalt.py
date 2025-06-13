__version__ = (0, 1, 0)
# meta developer: @Kovalsky_modules


import os
from hikkatl.types import Message
from .. import loader, utils
from pydub import AudioSegment
from Kobalt import CobaltAPI

@loader.tds
class Kobalt(loader.Module):
    """Скачивание видео по ссылке из разных источников"""

    strings = {
        'name': 'Kobalt',
        'audio_load': '<emoji document_id=5873204392429096339>📥</emoji> Загрузка <a href="{}">Аудио</a>',
        'audio_send': '<emoji document_id=5361697044723419988>✅</emoji> Ваше <a href="{}">Аудио</a>',
        'audio_error': '<emoji document_id=5361780367088958862>⚠</emoji> Не получилось скачать аудио. Проверьте правильность ссылки',
        'video_load': '<emoji document_id=5873204392429096339>📥</emoji> Загрузка <a href="{}">Видео</a>',
        'video_send': '<emoji document_id=5361697044723419988>✅</emoji> Ваше <a href="{}">Видео</a>',
        'video_error': '<emoji document_id=5361780367088958862>⚠</emoji> Не получилось скачать видео. Проверьте правильность ссылки',
        'video_muted': ' без звука',
        'services': '<blockquote><b>Поддерживаемые сервисы:</b></blockquote>\n<blockquote>{}</blockquote>'
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "caption", True,
                "Подписывать файлы?",
                validator=loader.validators.Boolean(),
            ),
        )
        
    @loader.command(ru_doc='Поддерживаемые сервисы')
    async def kservicescmd(self, message: Message):
        cobalt = CobaltAPI()
        services = cobalt.services()
        await utils.answer(message, self.strings["services"].format('\n'.join(services)))
        
    @loader.command(ru_doc='Скачать Аудио')
    async def kacmd(self, message: Message):
        cobalt = CobaltAPI()
        cobalt.mode("audio")
        args = utils.get_args_raw(message).split()
        await utils.answer(message, self.strings["audio_load"].format(args[0]))
        try:
            filename = cobalt.download(args[0])
        except:
            await utils.answer(message, self.strings["audio_error"])
            return
            
        me = await self._client.get_me()
        artist = "@" + me.username if me.username else me.first_name
        
        with open(filename, "rb") as f:
            audio = AudioSegment.from_file(filename, format='mp3')
            audio.export(
                        filename,
                        format='mp3',
                        tags={'artist': artist, 'title': f'{filename.split("_")[0]}_audio'}
                    )
            await utils.answer_file(
            message, f,
            caption=self.strings["audio_send"].format(
                args[0]) if self.config["caption"] else None,
            force_document=False
            )
            os.remove(filename)
        

    @loader.command(ru_doc='{url} {quality} - Скачать Видео, если не указывать качество оно будет выбрано автоматически. max, 4320, 2160, 1440, 1080, 720, 480, 360, 240, 144')
    async def kvcmd(self, message: Message):
        cobalt = CobaltAPI()
        args = utils.get_args_raw(message).split()
        if len(args) > 1:
            quality = args[1]
            cobalt.quality(quality)
        await utils.answer(message, self.strings["video_load"].format(args[0]))
        try:
            filename = cobalt.download(args[0])
        except:
            await utils.answer(message, self.strings["video_error"])
            return
            
        with open(filename, "rb") as f:
            await utils.answer_file(
            message, f,
            caption=self.strings["video_send"].format(
                args[0]) if self.config["caption"] else None,
            force_document=False
            )
            os.remove(filename)
        
    @loader.command(ru_doc='Скачать Видео без звука')
    async def kmvcmd(self, message: Message):
        cobalt = CobaltAPI()
        cobalt.mode("mute")
        args = utils.get_args_raw(message).split()
        await utils.answer(message, self.strings["video_load"].format(args[0])+self.strings["video_muted"])
        try:
            filename = cobalt.download(args[0])
        except:
            await utils.answer(message, self.strings["video_error"])
            return
            
        with open(filename, "rb") as f:
            await utils.answer_file(
            message, f,
            caption=self.strings["video_send"].format(
                args[0])+self.strings["video_muted"] if self.config["caption"] else None,
            force_document=False
            )
            os.remove(filename)
