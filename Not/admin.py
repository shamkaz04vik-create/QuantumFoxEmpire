from aiogram import Router, types
from config import ADMIN_ID

router = Router()

@router.message(lambda m: m.from_user.id == ADMIN_ID, commands=["admin"])
async def admin_panel(message: types.Message):
    await message.answer(
        "📊 Админ-панель\n\n"
        "/stats — статистика\n"
        "/broadcast — рассылка\n"
        "/users — список пользователей\n"
        "/vip — управление VIP\n"
        "/logs — логи"
    )