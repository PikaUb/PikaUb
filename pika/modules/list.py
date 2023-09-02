# meta developer: @PikaUb

from .. import loader, utils
import logging


logger = logging.getLogger(__name__)


@loader.tds
class ListMod(loader.Module):
    """List of all of the modules currently installed"""

    strings = {
        "name": "List",
        "amount": "🦐 <code>{}</code> modules loaded:\n",
        "partial_load": (
            "\n😾 <b>It's not all modules"
            " Pika is restarting...</b>"
        ),
        "cmd": "🔹 <i><b>To find out the module commands, use <code>{}help (module name)</code></i></b>\n",
        "module": "▫️",
        "core_module": "▪️",
    }

    strings_ru = {
        "amount": "🦐 Установлено <code>{}</code> модулей:",
        "partial_load": (
            "\n😾 <b>Это не все модули,"
            " Pika перезагружается...</b>"
        ),
        "cmd": "🔹 <i><b>Чтобы узнать команды модуля используй <code>{}help (название)</code></i></b>\n",
    }

    @loader.command(
        ru_doc="Показать все установленные модули",
    )
    async def listcmd(self, message):
        """- List of all of the modules currently installed"""

        prefix = f"{self.strings('cmd').format(str(self.get_prefix()))}\n"
        result = f"{self.strings('amount').format(str(len(self.allmodules.modules)))}\n"

        for mod in self.allmodules.modules:
            try:
                name = mod.strings["name"]
            except KeyError:
                name = mod.__clas__.__name__
            emoji = (
                self.strings("core_module")
                if mod.__origin__.startswith("<core")
                else self.strings("module")
            )
            result += f"\n {emoji} <code>{name}</code>"

        result += (
            ""
            if self.lookup("Loader").fully_loaded
            else f"\n\n{self.strings('partial_load')}"
        )
        result += f"\n\n {prefix}"

        await utils.answer(message, result)
