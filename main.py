import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz

TOKEN = "7680686918:AAFavPOQFBvK9omWgMZdsaoh-dPlY8IOcro"
bot = Bot(token=TOKEN)
dp = Dispatcher()

users_db = {}  # user_id: {"dob": "13.06", "utc": 3, "name": "Имя"}

geo_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="\ud83d\udccd \u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0433\u0435\u043e\u043b\u043e\u043a\u0430\u0446\u0438\u044e", request_location=True)]], resize_keyboard=True)

@dp.message(F.text.in_(["/start"]))
async def start(msg: types.Message):
    await msg.answer("\u041f\u0440\u0438\u0432\u0435\u0442! \u041d\u0430\u043f\u0438\u0448\u0438 \u0441\u0432\u043e\u044e \u0434\u0430\u0442\u0443 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, 13.06)", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.in_(["/privet"]))
async def privet(msg: types.Message):
    await msg.answer("\u0431\u0435\u0437\u043f\u043e\u043b\u0435\u0437\u043d\u0430\u044f \u043a\u043d\u043e\u043f\u043a\u0430 :3")

@dp.message(F.location)
async def get_location(msg: types.Message):
    lat = msg.location.latitude
    lon = msg.location.longitude
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=lat, lng=lon)
    if tz_str:
        utc_offset = int(pytz.timezone(tz_str).utcoffset(datetime.now()).total_seconds() // 3600)
        users_db[msg.from_user.id]["utc"] = utc_offset
        await msg.answer(f"\u0412\u0430\u0448 UTC: {utc_offset}\n\u0422\u0435\u043f\u0435\u0440\u044c \u0432\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u0430\u043d\u0434\u0443 /birthday")
    else:
        await msg.answer("\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u044c UTC. \u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0432\u0440\u0443\u0447\u043d\u0443\u044e (\u043d\u0430\u043f\u0440. 3)")

@dp.message(F.text.regexp(r"^\d{1,2}\.\d{1,2}$"))
async def set_birthday(msg: types.Message):
    users_db[msg.from_user.id] = {"dob": msg.text, "utc": None, "name": msg.from_user.full_name}
    await msg.answer("\u0422\u0435\u043f\u0435\u0440\u044c \u043e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0441\u0432\u043e\u0439 UTC (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, 3) \u0438\u043b\u0438 \u043d\u0430\u0436\u043c\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443 \u043d\u0438\u0436\u0435:", reply_markup=geo_kb)

@dp.message(F.text.regexp(r"^-?\d{1,2}$"))
async def set_utc(msg: types.Message):
    if msg.from_user.id in users_db:
        users_db[msg.from_user.id]["utc"] = int(msg.text)
        await msg.answer("\u0413\u043e\u0442\u043e\u0432\u043e! \u0422\u0435\u043f\u0435\u0440\u044c \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u043a\u043e\u043c\u0430\u043d\u0434\u0443 /birthday")
    else:
        await msg.answer("\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u0434\u0430\u0442\u0443 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f")

def get_birthday_text(user_id):
    data = users_db.get(user_id)
    if not data:
        return "\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u0434\u0430\u0442\u0443 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f"
    if data["utc"] is None:
        return "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 UTC \u043f\u0435\u0440\u0435\u0434 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u0435\u043c \u043a\u043e\u043c\u0430\u043d\u0434\u044b"

    now_utc = datetime.utcnow() + timedelta(hours=data["utc"])
    day, month = map(int, data["dob"].split('.'))
    bday = datetime(now_utc.year, month, day, 0, 0, 0)
    if bday.date() == now_utc.date():
        return f"\U0001f389 Сегодня день рождения у *{data['name']}*!\nПоздравляем и желаем счастья!"
    if bday < now_utc:
        bday = bday.replace(year=now_utc.year + 1)
    delta = bday - now_utc
    parts = []
    if delta.days > 0: parts.append(f"{delta.days} д")
    h, rem = divmod(delta.seconds, 3600)
    if h > 0: parts.append(f"{h} ч")
    m, s = divmod(rem, 60)
    if m > 0: parts.append(f"{m} м")
    if s > 0: parts.append(f"{s} с")
    return f"Ваше день рождения через: {' '.join(parts)}\nДата рождения: {data['dob']}"

@dp.message(F.text.in_(["/birthday", "др", "день рождения", "мой др", "мое день рождения"]))
async def birthday(msg: types.Message):
    text = get_birthday_text(msg.from_user.id)
    if "\U0001f389" in text:
        await msg.answer_sticker("CAACAgIAAxkBAAEF6jRlmAxhR26nqZn4YItt3oiLPqN1-QAC0wADVp29Ck1cwJ_2RYYzNAQ")
    sent = await msg.answer(text, parse_mode="Markdown")
    for _ in range(10):
        await asyncio.sleep(1)
        new_text = get_birthday_text(msg.from_user.id)
        if "\U0001f389" not in new_text:
            try:
                await sent.edit_text(new_text)
            except:
                break

@dp.message(F.text.in_(["/group_birthday", "др уч", "др участников"]))
async def group_birthday(msg: types.Message):
    if msg.chat.type == "private":
        return await msg.answer("Эта команда работает только в группах.")

    async def build_group_text():
        now = datetime.utcnow()
        result = []
        for user_id, data in users_db.items():
            if data.get("dob") and data.get("utc") is not None:
                local_now = now + timedelta(hours=data["utc"])
                day, month = map(int, data["dob"].split('.'))
                bday = datetime(local_now.year, month, day)
                if bday.date() == local_now.date():
                    result.append((timedelta(0), user_id, data["dob"], data["name"]))
                else:
                    if bday < local_now:
                        bday = bday.replace(year=local_now.year + 1)
                    delta = bday - local_now
                    result.append((delta, user_id, data["dob"], data["name"]))

        result.sort()
        if not result:
            return "Нет пользователей с установленной датой рождения."

        text = "День рождения участников группы:\n"
        for delta, uid, dob, name in result[:5]:
            if delta.days == 0:
                text += f"🎉 <b>{name}</b> — СЕГОДНЯ! ({dob})\n"
            else:
                text += f"<b>{name}</b> — через {delta.days}д ({dob})\n"
        return text

    text = await build_group_text()
    sent = await msg.answer(text, parse_mode="HTML")
    for _ in range(10):
        await asyncio.sleep(1)
        new_text = await build_group_text()
        try:
            await sent.edit_text(new_text, parse_mode="HTML")
        except:
            break

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz

TOKEN = "7680686918:AAFavPOQFBvK9omWgMZdsaoh-dPlY8IOcro"
bot = Bot(token=TOKEN)
dp = Dispatcher()

users_db = {}  # user_id: {"dob": "13.06", "utc": 3, "name": "Имя"}

geo_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="\ud83d\udccd \u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u0433\u0435\u043e\u043b\u043e\u043a\u0430\u0446\u0438\u044e", request_location=True)]], resize_keyboard=True)

@dp.message(F.text.in_(["/start"]))
async def start(msg: types.Message):
    await msg.answer("\u041f\u0440\u0438\u0432\u0435\u0442! \u041d\u0430\u043f\u0438\u0448\u0438 \u0441\u0432\u043e\u044e \u0434\u0430\u0442\u0443 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, 13.06)", reply_markup=types.ReplyKeyboardRemove())

@dp.message(F.text.in_(["/privet"]))
async def privet(msg: types.Message):
    await msg.answer("\u0431\u0435\u0437\u043f\u043e\u043b\u0435\u0437\u043d\u0430\u044f \u043a\u043d\u043e\u043f\u043a\u0430 :3")

@dp.message(F.location)
async def get_location(msg: types.Message):
    lat = msg.location.latitude
    lon = msg.location.longitude
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=lat, lng=lon)
    if tz_str:
        utc_offset = int(pytz.timezone(tz_str).utcoffset(datetime.now()).total_seconds() // 3600)
        users_db[msg.from_user.id]["utc"] = utc_offset
        await msg.answer(f"\u0412\u0430\u0448 UTC: {utc_offset}\n\u0422\u0435\u043f\u0435\u0440\u044c \u0432\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043a\u043e\u043c\u0430\u043d\u0434\u0443 /birthday")
    else:
        await msg.answer("\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442\u044c UTC. \u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0432\u0440\u0443\u0447\u043d\u0443\u044e (\u043d\u0430\u043f\u0440. 3)")

@dp.message(F.text.regexp(r"^\d{1,2}\.\d{1,2}$"))
async def set_birthday(msg: types.Message):
    users_db[msg.from_user.id] = {"dob": msg.text, "utc": None, "name": msg.from_user.full_name}
    await msg.answer("\u0422\u0435\u043f\u0435\u0440\u044c \u043e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0441\u0432\u043e\u0439 UTC (\u043d\u0430\u043f\u0440\u0438\u043c\u0435\u0440, 3) \u0438\u043b\u0438 \u043d\u0430\u0436\u043c\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443 \u043d\u0438\u0436\u0435:", reply_markup=geo_kb)

@dp.message(F.text.regexp(r"^-?\d{1,2}$"))
async def set_utc(msg: types.Message):
    if msg.from_user.id in users_db:
        users_db[msg.from_user.id]["utc"] = int(msg.text)
        await msg.answer("\u0413\u043e\u0442\u043e\u0432\u043e! \u0422\u0435\u043f\u0435\u0440\u044c \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 \u043a\u043e\u043c\u0430\u043d\u0434\u0443 /birthday")
    else:
        await msg.answer("\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u0434\u0430\u0442\u0443 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f")

def get_birthday_text(user_id):
    data = users_db.get(user_id)
    if not data:
        return "\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u0434\u0430\u0442\u0443 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f"
    if data["utc"] is None:
        return "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 UTC \u043f\u0435\u0440\u0435\u0434 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u0435\u043c \u043a\u043e\u043c\u0430\u043d\u0434\u044b"

    now_utc = datetime.utcnow() + timedelta(hours=data["utc"])
    day, month = map(int, data["dob"].split('.'))
    bday = datetime(now_utc.year, month, day, 0, 0, 0)
    if bday.date() == now_utc.date():
        return f"\U0001f389 Сегодня день рождения у *{data['name']}*!\nПоздравляем и желаем счастья!"
    if bday < now_utc:
        bday = bday.replace(year=now_utc.year + 1)
    delta = bday - now_utc
    parts = []
    if delta.days > 0: parts.append(f"{delta.days} д")
    h, rem = divmod(delta.seconds, 3600)
    if h > 0: parts.append(f"{h} ч")
    m, s = divmod(rem, 60)
    if m > 0: parts.append(f"{m} м")
    if s > 0: parts.append(f"{s} с")
    return f"Ваше день рождения через: {' '.join(parts)}\nДата рождения: {data['dob']}"

@dp.message(F.text.in_(["/birthday", "др", "день рождения", "мой др", "мое день рождения"]))
async def birthday(msg: types.Message):
    text = get_birthday_text(msg.from_user.id)
    if "\U0001f389" in text:
        await msg.answer_sticker("CAACAgIAAxkBAAEF6jRlmAxhR26nqZn4YItt3oiLPqN1-QAC0wADVp29Ck1cwJ_2RYYzNAQ")
    sent = await msg.answer(text, parse_mode="Markdown")
    for _ in range(10):
        await asyncio.sleep(1)
        new_text = get_birthday_text(msg.from_user.id)
        if "\U0001f389" not in new_text:
            try:
                await sent.edit_text(new_text)
            except:
                break

@dp.message(F.text.in_(["/group_birthday", "др уч", "др участников"]))
async def group_birthday(msg: types.Message):
    if msg.chat.type == "private":
        return await msg.answer("Эта команда работает только в группах.")

    async def build_group_text():
        now = datetime.utcnow()
        result = []
        for user_id, data in users_db.items():
            if data.get("dob") and data.get("utc") is not None:
                local_now = now + timedelta(hours=data["utc"])
                day, month = map(int, data["dob"].split('.'))
                bday = datetime(local_now.year, month, day)
                if bday.date() == local_now.date():
                    result.append((timedelta(0), user_id, data["dob"], data["name"]))
                else:
                    if bday < local_now:
                        bday = bday.replace(year=local_now.year + 1)
                    delta = bday - local_now
                    result.append((delta, user_id, data["dob"], data["name"]))

        result.sort()
        if not result:
            return "Нет пользователей с установленной датой рождения."

        text = "День рождения участников группы:\n"
        for delta, uid, dob, name in result[:5]:
            if delta.days == 0:
                text += f"🎉 <b>{name}</b> — СЕГОДНЯ! ({dob})\n"
            else:
                text += f"<b>{name}</b> — через {delta.days}д ({dob})\n"
        return text

    text = await build_group_text()
    sent = await msg.answer(text, parse_mode="HTML")
    for _ in range(10):
        await asyncio.sleep(1)
        new_text = await build_group_text()
        try:
            await sent.edit_text(new_text, parse_mode="HTML")
        except:
            break

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
