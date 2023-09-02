import contextlib
import itertools
import os
import sys
import typing
from types import ModuleType

import telethon
from meval import meval
from telethon.errors.rpcerrorlist import MessageIdInvalidError
from telethon.sessions import StringSession
from telethon.tl.types import Message

from .. import loader, main, utils
from ..log import HikkaException


@loader.tds
class EvalutorMod(loader.Module):
    """Evaluates python code"""

    strings = {
        "name": "Python",
        "eval": (
            "<emoji document_id=4985626654563894116>💻</emoji><b>"
            " Code:</b>\n<code>{}</code>\n\n<emoji"
            " document_id=5197688912457245639>✅</emoji><b>"
            " Result:</b>\n<code>{}</code>"
        ),
        "err": (
            "<emoji document_id=4985626654563894116>💻</emoji><b>"
            " Code:</b>\n<code>{}</code>\n\n<emoji"
            " document_id=5312526098750252863>🚫</emoji> <b>Error:</b>\n{}"
        ),
    }

    strings_ru = {
        "eval": (
            "<emoji document_id=4985626654563894116>💻</emoji><b>"
            " Код:</b>\n<code>{}</code>\n\n<emoji"
            " document_id=5197688912457245639>✅</emoji><b>"
            " Результат:</b>\n<code>{}</code>"
        ),
        "err": (
            "<emoji document_id=4985626654563894116>💻</emoji><b>"
            " Код:</b>\n<code>{}</code>\n\n<emoji"
            " document_id=5312526098750252863>🚫</emoji> <b>Ошибка:</b>\n{}"
        ),
        "_cls_doc": "Выполняет Python код",
    }

    strings_uk = {
        "eval": (
            "<emoji document_id=4985626654563894116>💻</emoji><b>"
            " Код:</b>\n<code>{}</code>\n\n<emoji"
            " document_id=5197688912457245639>✅</emoji><b>"
            " Результат:</b>\n<code>{}</code>"
        ),
        "err": (
            "<emoji document_id=4985626654563894116>💻</emoji><b>"
            " Код:</b>\n<code>{}</code>\n\n<emoji"
            " document_id=5312526098750252863>🚫</emoji> <b>Помилка:</b>\n{}"
        ),
        "_cls_doc": "Виконує Python код",
    }

    @loader.owner
    @loader.command(ru_doc="Выполняет Python код", alias="eval")
    async def e(self, message: Message):
        """Evaluates python code"""
        try:
            result = await meval(
                utils.get_args_raw(message),
                globals(),
                **await self.getattrs(message),
            )
        except Exception:
            item = HikkaException.from_exc_info(*sys.exc_info())

            await utils.answer(
                message,
                self.strings("err").format(
                    utils.escape_html(utils.get_args_raw(message)),
                    self.censor(
                        (
                            "\n".join(item.full_stack.splitlines()[:-1])
                            + "\n\n"
                            + "🚫 "
                            + item.full_stack.splitlines()[-1]
                        )
                    ),
                ),
            )

            return

        if callable(getattr(result, "stringify", None)):
            with contextlib.suppress(Exception):
                result = str(result.stringify())

        with contextlib.suppress(MessageIdInvalidError):
            await utils.answer(
                message,
                self.strings("eval").format(
                    utils.escape_html(utils.get_args_raw(message)),
                    utils.escape_html(self.censor(str(result))),
                ),
            )

    def censor(self, ret: str) -> str:
        ret = ret.replace(str(self._client.hikka_me.phone), "&lt;phone&gt;")

        if redis := os.environ.get("REDIS_URL") or main.get_config_key("redis_uri"):
            ret = ret.replace(redis, f'redis://{"*" * 26}')

        if db := os.environ.get("DATABASE_URL") or main.get_config_key("db_uri"):
            ret = ret.replace(db, f'postgresql://{"*" * 26}')

        if btoken := self._db.get("hikka.inline", "bot_token", False):
            ret = ret.replace(
                btoken,
                f'{btoken.split(":")[0]}:{"*" * 26}',
            )

        if htoken := self.lookup("loader").get("token", False):
            ret = ret.replace(htoken, f'eugeo_{"*" * 26}')

        ret = ret.replace(
            StringSession.save(self._client.session),
            f"StringSession({'*' * 26})",
        )

        return ret

    async def getattrs(self, message: Message) -> dict:
        reply = await message.get_reply_message()
        return {
            **{
                "message": message,
                "client": self._client,
                "reply": reply,
                "r": reply,
                **self.get_sub(telethon.tl.types),
                **self.get_sub(telethon.tl.functions),
                "event": message,
                "chat": message.to_id,
                "telethon": telethon,
                "utils": utils,
                "main": main,
                "loader": loader,
                "f": telethon.tl.functions,
                "c": self._client,
                "m": message,
                "lookup": self.lookup,
                "self": self,
                "db": self.db,
            },
        }

    def get_sub(self, obj: typing.Any, _depth: int = 1) -> dict:
        """Get all callable capitalised objects in an object recursively, ignoring _*"""
        return {
            **dict(
                filter(
                    lambda x: x[0][0] != "_"
                    and x[0][0].upper() == x[0][0]
                    and callable(x[1]),
                    obj.__dict__.items(),
                )
            ),
            **dict(
                itertools.chain.from_iterable(
                    [
                        self.get_sub(y[1], _depth + 1).items()
                        for y in filter(
                            lambda x: x[0][0] != "_"
                            and isinstance(x[1], ModuleType)
                            and x[1] != obj
                            and x[1].__package__.rsplit(".", _depth)[0]
                            == "telethon.tl",
                            obj.__dict__.items(),
                        )
                    ]
                )
            ),
        }
