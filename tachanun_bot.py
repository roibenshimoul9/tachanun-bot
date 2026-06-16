import os
from datetime import date, timedelta
from hdate.date_info import HDateInfo
from hdate import Months
from astral import LocationInfo
from astral.sun import sun
import pytz

from telegram import Bot
import asyncio

CITY = LocationInfo("Beer Sheva", "Israel", "Asia/Jerusalem", 31.2518, 34.7913)


def get_sunset(check_date: date) -> str:
    tz = pytz.timezone(CITY.timezone)
    s = sun(CITY.observer, date=check_date, tzinfo=tz)
    return s["sunset"].strftime("%H:%M")


def get_tachanun_status_for(check_date: date) -> str:
    hdate_info = HDateInfo(check_date, diaspora=False)
    no_tachanun_reasons = []

    # שבת
    if hdate_info.is_shabbat:
        no_tachanun_reasons.append("שבת")

    # יום טוב
    if hdate_info.is_yom_tov:
        no_tachanun_reasons.append("יום טוב")

    # ראש חודש — בדיקה כפולה: לפי שם חג וגם לפי יום א' בחודש
    rosh_chodesh_by_holiday = any(
        "rosh" in h.name.lower() or "chodesh" in h.name.lower()
        for h in hdate_info.holidays
    )
    if rosh_chodesh_by_holiday or hdate_info.date.day == 1:
        no_tachanun_reasons.append("ראש חודש")

    # כל חודש ניסן
    if hdate_info.date.month == Months.NISAN:
        no_tachanun_reasons.append("כל חודש ניסן")

    # ל"ג בעומר
    for holiday in hdate_info.holidays:
        if holiday.name == "Lag BaOmer":
            no_tachanun_reasons.append('ל"ג בעומר')
            break

    # מר"ח סיון עד י"ב סיון
    if hdate_info.date.month == Months.SIVAN and hdate_info.date.day <= 12:
        no_tachanun_reasons.append('מר"ח סיון עד י"ב סיון')

    # תשעה באב
    for holiday in hdate_info.holidays:
        if "Tisha" in holiday.name or "Av" in holiday.name:
            no_tachanun_reasons.append("תשעה באב")
            break

    # ט"ו באב
    for holiday in hdate_info.holidays:
        if "Tu B'Av" in holiday.name or "Tu BAv" in holiday.name:
            no_tachanun_reasons.append('ט"ו באב')
            break

    # ערב ראש השנה
    for holiday in hdate_info.holidays:
        if "Erev Rosh" in holiday.name:
            no_tachanun_reasons.append("ערב ראש השנה")
            break

    # ערב יום כיפור
    for holiday in hdate_info.holidays:
        if "Erev Yom Kippur" in holiday.name:
            no_tachanun_reasons.append("ערב יום כיפור")
            break

    # י"א תשרי עד סוף תשרי
    if hdate_info.date.month == Months.TISHREI and hdate_info.date.day >= 11:
        no_tachanun_reasons.append('מי"א תשרי עד סוף תשרי')

    # חנוכה
    for holiday in hdate_info.holidays:
        if "Chanukah" in holiday.name or "Hanukkah" in holiday.name:
            no_tachanun_reasons.append("חנוכה")
            break

    # ט"ו בשבט
    for holiday in hdate_info.holidays:
        if "BiShvat" in holiday.name or "Bishvat" in holiday.name:
            no_tachanun_reasons.append('ט"ו בשבט')
            break

    # פורים ושושן פורים
    for holiday in hdate_info.holidays:
        if "Purim" in holiday.name:
            no_tachanun_reasons.append("פורים / שושן פורים")
            break

    # יום העצמאות
    for holiday in hdate_info.holidays:
        if "Atzmaut" in holiday.name or "HaAtzmaut" in holiday.name:
            no_tachanun_reasons.append("יום העצמאות")
            break

    # יום ירושלים
    for holiday in hdate_info.holidays:
        if "Yerushalayim" in holiday.name:
            no_tachanun_reasons.append("יום ירושלים")
            break

    hebrew_date_str = str(hdate_info.date)
    sunset_str = get_sunset(check_date)

    if no_tachanun_reasons:
        reason_str = ", ".join(no_tachanun_reasons)
        tachanun_line = f"🚫 אין תחנון ({reason_str})"
    else:
        tachanun_line = "✅ יש תחנון"

    return (
        f"{tachanun_line}\n"
        f"📅 {hebrew_date_str}\n"
        f"🌅 שקיעה: {sunset_str}"
    )


async def send_telegram_message(chat_id, message_text, bot_token):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")


async def main():
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8971218554:AAF0Dv3nG7PRebV7oF4v5IPLmmHy6kQwXV8")
    telegram_chat_id   = os.environ.get("TELEGRAM_CHAT_ID",   "789180775")

    today    = date.today()
    tomorrow = today + timedelta(days=1)

    status_today    = get_tachanun_status_for(today)
    status_tomorrow = get_tachanun_status_for(tomorrow)

    message = (
        f"*היום*\n{status_today}\n\n"
        f"*מחר*\n{status_tomorrow}"
    )

    await send_telegram_message(telegram_chat_id, message, telegram_bot_token)


if __name__ == "__main__":
    asyncio.run(main())
