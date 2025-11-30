import os
import json
import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

# Token bota ze zmiennych środowiskowych (ENV),
API_TOKEN = os.getenv("BOT_TOKEN", "8249152623:AAHvQAILS-EHvfVakD6crHHtXeEGEfWjh54")

# Plik JSON, w którym zapisujemy wybrany język użytkownika, żeby bot pamiętał ustawienia po restarcie.
LANG_FILE = Path("user_lang.json")

# Słownik: user_id -> kod języka (np. "pl", "en", "ru")
user_lang: dict[int, str] = {}


def load_lang() -> None:
    """Wczytuje zapisane języki użytkowników z pliku JSON."""
    global user_lang
    # Jeśli plik istnieje, to wczytujemy dane.
    if LANG_FILE.exists():
        data = json.loads(LANG_FILE.read_text(encoding="utf-8"))
        # W JSON klucze są zawsze stringami, więc zamieniamy je na int.
        user_lang = {int(k): v for k, v in data.items()}


def save_lang() -> None:
    """Zapisuje aktualny słownik user_lang do pliku JSON."""
    # Zamieniamy klucze na string, bo JSON nie zapisze poprawnie int jako klucza.
    data = {str(k): v for k, v in user_lang.items()}
    LANG_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# === Teksty (tłumaczenia) ===
# Wszystkie komunikaty bota w różnych językach trzymamy w jednym słowniku.
TEXT = {
    "choose_lang": {"en": "Choose a language 👇", "pl": "Wybierz język 👇", "ru": "Выбери язык 👇"},
    "hello": {
        "en": "Hi, I'm Calmify. Tell me how you're feeling 🙂",
        "pl": "Cześć, jestem Calmify. Napisz jak się czujesz 🙂",
        "ru": "Привет, я Calmify. Напиши, как ты себя чувствуешь 🙂",
    },
    "lang_set": {"en": "Language set: English ✅", "pl": "Ustawiono język: Polski ✅", "ru": "Язык установлен: Русский ✅"},
}


def t(user_id: int, key: str) -> str:
    """Zwraca tekst o danym kluczu w języku ustawionym dla użytkownika."""
    # Domyślnie ustawiamy polski, jeśli użytkownik nie ma jeszcze wyboru.
    lang = user_lang.get(user_id, "pl")
    # Jeśli nie ma tłumaczenia w wybranym języku, robimy „awaryjnie” po angielsku.
    return TEXT[key].get(lang, TEXT[key]["en"])


def lang_keyboard() -> InlineKeyboardMarkup:
    """Tworzy klawiaturę (inline) do wyboru języka."""
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="English 🇬🇧", callback_data="lang:en"),
        InlineKeyboardButton(text="Polski 🇵🇱", callback_data="lang:pl"),
        InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang:ru"),
    ]])


async def main():
    # Na starcie wczytujemy zapisane ustawienia języka.
    load_lang()

    # Tworzymy obiekt bota i dispatcher.
    bot = Bot(API_TOKEN)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message):
        # Po /start prosimy o wybór języka.
        await message.answer(TEXT["choose_lang"]["en"], reply_markup=lang_keyboard())

    @dp.callback_query(F.data.startswith("lang:"))
    async def set_language(callback: CallbackQuery):
        # callback_data ma format "lang:xx" (np. "lang:pl")
        lang = callback.data.split(":", 1)[1]

        # Zapisujemy wybrany język dla danego użytkownika.
        user_lang[callback.from_user.id] = lang
        save_lang()  # utrwalamy wybór w pliku

        await callback.answer()

        # Edytujemy wiadomość z wyborem języka na potwierdzenie.
        await callback.message.edit_text(t(callback.from_user.id, "lang_set"))

        # Wysyłamy powitanie w wybranym języku.
        await callback.message.answer(t(callback.from_user.id, "hello"))

    @dp.message()
    async def echo(message: Message):
        # Proste echo: wysyłamy powitanie + treść wiadomości użytkownika.
        await message.answer(f"{t(message.from_user.id, 'hello')}\n\n{message.text}")

    # odrzucanie zaległych aktualizacji
    await bot.delete_webhook(drop_pending_updates=True)

    logging.info("Bot started ✅")

    # Uruchamiamy polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    #uruchomienie programu
    asyncio.run(main())
