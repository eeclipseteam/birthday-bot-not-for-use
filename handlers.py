from aiogram import Router, types, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from datetime import datetime
from utils import calculate_birthday_time

router = Router()

users = {}

@router.message(F.text.lower().in_({"мой др", "мое день рождения", "/birthday", "др"}))
async def handle_birthday(message: Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.answer("Напиши свою дату рождения в формате ДД.ММ (например, 13.06):")
        users[user_id] = {"stage": "awaiting_birthday"}
        return

    user_data = users[user_id]
    if "birthday" not in user_data:
        await message.answer("Напиши свою дату рождения в формате ДД.ММ (например, 13.06):")
        users[user_id]["stage"] = "awaiting_birthday"
        return

    now = datetime.utcnow()
    bday_str = user_data["birthday"]
    bday = datetime.strptime(bday_str, "%d.%m")
    time_left = calculate_birthday_time(bday, user_data["utc"])
    await message.answer(f"Дата рождения: {bday_str}\nДо дня рождения: {time_left}")

@router.message(F.text.lower().in_({"др участников", "/group_birthday"}))
async def handle_group_birthday(message: Message):
    if message.chat.type == "private":
        await message.answer("Эта команда работает только в группах.")
        return

    group_members = [uid for uid in users if users[uid].get("birthday")]
    if not group_members:
        await message.answer("Нет данных о днях рождения участников.")
        return

    now = datetime.utcnow()
    upcoming = []
    for uid in group_members:
        data = users[uid]
        name = data.get("name", f"User {uid}")
        bday = datetime.strptime(data["birthday"], "%d.%m")
        time_left = calculate_birthday_time(bday, data["utc"])
        upcoming.append((name, time_left))

    upcoming.sort(key=lambda x: x[1])
    msg = "Дни рождения участников:\n" + "\n".join(
        f"{name} — через {delta}" for name, delta in upcoming
    )
    await message.answer(msg)

@router.message(F.text.lower().in_({"привет", "/privet"}))
async def handle_privet(message: Message):
    await message.answer("Бесполезная кнопка :3")

@router.message(F.location)
async def handle_location(message: Message):
    user_id = message.from_user.id
    if user_id in users and users[user_id].get("stage") == "awaiting_utc":
        lon = message.location.longitude
        utc_offset = int(round(lon / 15))
        users[user_id]["utc"] = utc_offset
        await message.answer("Спасибо, запомнил ваш UTC!")
    else:
        await message.answer("Сначала введите дату рождения.")

@router.message(F.text.regexp(r"^\d{1,2}\.\d{1,2}$"))
async def receive_birthday(message: Message):
    user_id = message.from_user.id
    try:
        datetime.strptime(message.text, "%d.%m")
    except:
        await message.answer("Неверный формат. Введите в виде 13.06")
        return

    users[user_id] = {
        "birthday": message.text,
        "stage": "awaiting_utc",
        "name": message.from_user.first_name or "Пользователь"
    }

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]
    ], resize_keyboard=True)

    await message.answer("Теперь отправьте геолокацию или напишите свой UTC (например: 3)", reply_markup=kb)

@router.message(F.text.regexp(r"^[-+]?\d+$"))
async def receive_utc(message: Message):
    user_id = message.from_user.id
    try:
        users[user_id]["utc"] = int(message.text)
        await message.answer("Спасибо! Все сохранено.", reply_markup=types.ReplyKeyboardRemove())
    except:
        await message.answer("Введите корректный UTC в виде числа, например: 3")
