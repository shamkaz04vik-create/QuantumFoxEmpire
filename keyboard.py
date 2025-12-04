from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🛠 Услуги")],
            [KeyboardButton("👤 Личный кабинет"), KeyboardButton("📢 VPN")],
            [KeyboardButton("💬 Поддержка")]
        ],
        resize_keyboard=True
    )

def services_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("🤖 Создание ботов"), KeyboardButton("🎨 Дизайн")],
            [KeyboardButton("📣 Реклама"), KeyboardButton("🌐 Создание сайтов")],
            [KeyboardButton("⬅️ Назад")]
        ],
        resize_keyboard=True
    )

def back_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("⬅️ Назад")]],
        resize_keyboard=True
    )