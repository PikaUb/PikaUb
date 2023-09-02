import locale
import os
import string
import sys
import typing

from dialog import Dialog, ExecutableNotFound

from . import utils


def _safe_input(*args, **kwargs):
    try:
        return input(*args, **kwargs)
    except (EOFError, OSError):
        raise
    except KeyboardInterrupt:
        print()
        return None


class TDialog:
    def inputbox(self, query: str) -> typing.Tuple[bool, str]:
        print(query)
        print()
        inp = _safe_input("Введите значение...:")
        return (False, "Cancelled") if not inp else (True, inp)

    def msgbox(self, msg: str) -> bool:
        print(msg)
        return True


TITLE = ""

if sys.stdout.isatty():
    try:
        DIALOG = TDialog()
    except (ExecutableNotFound, locale.Error):
        DIALOG = Dialog(dialog="dialog", autowidgetsize=True)
        locale.setlocale(locale.LC_ALL, "")
else:
    DIALOG = TDialog()


def api_config(data_root: str):
    code, hash_value = DIALOG.inputbox(
        """­

















Pika-Userbot

Пожалуйста, введите API HASH
Для отмены: нажмите Ctrl + Z
    """
    )
    if not code:
        return

    if len(hash_value) != 32 or any(it not in string.hexdigits for it in hash_value):
        DIALOG.msgbox("Неверный HASH")
        return

    code, id_value = DIALOG.inputbox(
        """­
Отлично! Теперь введите API ID
    """
    )

    if not id_value or any(it not in string.digits for it in id_value):
        DIALOG.msgbox("Неверный ID")
        return

    with open(
        os.path.join(
            data_root or os.path.dirname(utils.get_base_dir()), "api_token.txt"
        ),
        "w",
    ) as file:
        file.write(id_value + "\n" + hash_value)

    DIALOG.msgbox(
        "API данные сохранены. Осталось только ввести номер и код подтверждения. Приступим!\n"
    )
