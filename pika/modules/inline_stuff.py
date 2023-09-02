import re
import string

from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest
from telethon.tl.types import Message

from .. import loader, utils
from ..inline.types import BotInlineMessage


@loader.tds
class InlineStuffMod(loader.Module):
    """Provides support for inline stuff"""

    strings = {
        "name": "InlineStuff",
        "bot_username_invalid": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Specified bot"
            " username is invalid. It must end with</b> <code>bot</code> <b>and contain"
            " at least 4 symbols</b>"
        ),
        "bot_username_occupied": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>This username is"
            " already occupied</b>"
        ),
        "bot_updated": (
            "<emoji document_id=6318792204118656433>🎉</emoji> <b>Config successfully"
            " saved. Restart userbot to apply changes</b>"
        ),
        "this_is_hikka": (
            "🦐 <b>Hi! This is PikaUserbot, UserBot that is based on the best Hikka-Pyro. You can"
            " install it to your account!</b>\n\n<b>🌍 <a"
            ' href="https://github.com/PikaUb/PikaUb">GitHub</a></b>\n<b>🧑‍🔧 <a'
            ' href="https://t.me/AllNetfoll">Чат поддержки</a></b>'
        ),
    }

    strings_ru = {
        "bot_username_invalid": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Неправильный ник"
            " бота. Он должен заканчиваться на</b> <code>bot</code> <b>и быть не короче"
            " чем 5 символов</b>"
        ),
        "bot_username_occupied": (
            "<emoji document_id=5312526098750252863>🚫</emoji> <b>Такой ник бота уже"
            " занят</b>"
        ),
        "bot_updated": (
            "<emoji document_id=6318792204118656433>🎉</emoji> <b>Настройки сохранены."
            " Для их применения нужно перезагрузить Netfoll</b>"
        ),
        "this_is_hikka": (
            "🦐 <b>Привет! Это PikaUserbot, ЮзерБот основанный на Hikka-Pyro. Вы можете"
            " установить на свой аккаунт!</b>\n\n<b>💎 <a"
            ' href="https://github.com/PikaUb/PikaUb">GitHub</a></b>\n<b>🧑‍💼 <a'
            ' href="https://t.me/pika_talks">Чат поддержки</a></b>'
        ),
    }

    async def watcher(self, message: Message):
        if (
            getattr(message, "out", False)
            and getattr(message, "via_bot_id", False)
            and message.via_bot_id == self.inline.bot_id
            and "This message will be deleted automatically"
            in getattr(message, "raw_text", "")
        ):
            await message.delete()
            return

        if (
            not getattr(message, "out", False)
            or not getattr(message, "via_bot_id", False)
            or message.via_bot_id != self.inline.bot_id
            or "Opening gallery..." not in getattr(message, "raw_text", "")
        ):
            return

        id_ = re.search(r"#id: ([a-zA-Z0-9]+)", message.raw_text)[1]

        await message.delete()

        m = await message.respond("🦐", reply_to=utils.get_topic(message))

        await self.inline.gallery(
            message=m,
            next_handler=self.inline._custom_map[id_]["handler"],
            caption=self.inline._custom_map[id_].get("caption", ""),
            force_me=self.inline._custom_map[id_].get("force_me", False),
            disable_security=self.inline._custom_map[id_].get(
                "disable_security", False
            ),
            silent=True,
        )

    async def _check_bot(self, username: str) -> bool:
        async with self._client.conversation("@BotFather", exclusive=False) as conv:
            try:
                m = await conv.send_message("/token")
            except YouBlockedUserError:
                await self._client(UnblockRequest(id="@BotFather"))
                m = await conv.send_message("/token")

            r = await conv.get_response()

            await m.delete()
            await r.delete()

            if not hasattr(r, "reply_markup") or not hasattr(r.reply_markup, "rows"):
                return False

            for row in r.reply_markup.rows:
                for button in row.buttons:
                    if username != button.text.strip("@"):
                        continue

                    m = await conv.send_message("/cancel")
                    r = await conv.get_response()

                    await m.delete()
                    await r.delete()

                    return True

    @loader.command(
        ru_doc="<юзернейм> - Изменить юзернейм инлайн бота",
        it_doc="<username> - Cambia il nome utente del bot inline",
        de_doc="<username> - Ändere den Inline-Bot-Nutzernamen",
        tr_doc="<kullanıcı adı> - İçe aktarma botunun kullanıcı adını değiştirin",
        uz_doc="<foydalanuvchi nomi> - Bot foydalanuvchi nomini o'zgartiring",
        es_doc="<nombre de usuario> - Cambia el nombre de usuario del bot de inline",
        kk_doc="<пайдаланушы аты> - Инлайн боттың пайдаланушы атын өзгерту",
    )
    async def ch_netfoll_bot(self, message: Message):
        """<username> - Change your Pima inline bot username"""
        args = utils.get_args_raw(message).strip("@")
        if (
            not args
            or not args.lower().endswith("bot")
            or len(args) <= 4
            or any(
                litera not in (string.ascii_letters + string.digits + "_")
                for litera in args
            )
        ):
            await utils.answer(message, self.strings("bot_username_invalid"))
            return

        try:
            await self._client.get_entity(f"@{args}")
        except ValueError:
            pass
        else:
            if not await self._check_bot(args):
                await utils.answer(message, self.strings("bot_username_occupied"))
                return

        self._db.set("hikka.inline", "custom_bot", args)
        self._db.set("hikka.inline", "bot_token", None)
        await utils.answer(message, self.strings("bot_updated"))

    async def aiogram_watcher(self, message: BotInlineMessage):
        if message.text != "/start":
            return

        await message.answer_photo(
            "https://github.com/PikaUb/PikaUb/raw/master/assets/bot_pfp.jpg",
            caption=self.strings("this_is_hikka"),
        )

    async def client_ready(self):
        if self.get("migrated"):
            return

        self.set("migrated", True)
        async with self._client.conversation("@BotFather") as conv:
            for msg in [
                "/cancel",
                "/setinline",
                f"@{self.inline.bot_username}",
                "👾 Netfoll Inline",
            ]:
                m = await conv.send_message(msg)
                r = await conv.get_response()

                await m.delete()
                await r.delete()
