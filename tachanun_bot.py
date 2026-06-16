import os
from datetime import date, timedelta
from hdate.date_info import HDateInfo
from hdate import Months
from astral import LocationInfo
from astral.sun import sun
import datetime as dt
import pytz

from telegram import Bot
import asyncio

CITY = LocationInfo("Beer Sheva", "Israel", "Asia/Jerusalem", 31.2518, 34.7913)


def get_sunset(check_date: date) -> str:
    """מחזיר שעת שקיעה כטקסט עבור תאריך נתון"""
    tz = pytz.timezone(CITY.timezone)
    s = sun(CITY.observer, date=check_date, tzinfo=tz)
    return s["sunset"].strftime("%H:%M")


def get_tachanun_status_for(check_date: date) -> str:
    """מחזיר סטטוס תחנון + תאריך עברי + שקיעה לתאריך נתון"""
    hdate_info = HDateInfo(check_date, diaspora=True)
    no_tachanun_reasons = []

    if hdate_info.is_shabbat:
        no_tachanun_reasons.append("שבת")
    if hdate_info.is_yom_tov:
        no_tachanun_reasons.append("יום טוב")

    for holiday in hdate_info.holidays:
        if holiday.name == "Rosh Chodesh":
            no_tachanun_reasons.append("ראש חודש")
            break

    if hdate_info.date.month == Months.NISAN:
        no_tachanun_reasons.append("כל חודש ניסן")

    for holiday in hdate_info.holidays:
        if holiday.name == "Lag BaOmer":
            no_tachanun_reasons.append('ל"ג בעומר')
            break

    if hdate_info.date.month == Months.SIVAN and hdate_info.date.day <= 12:
        no_tachanun_reasons.append('מר"ח סיון עד י"ב סיון')

    for holiday in hdate_info.holidays:
        if holiday.name == "Tisha B'Av":
            no_tachanun_reasons.append("תשעה באב")
            break

    for holiday in hdate_info.holidays:
        if holiday.name == "Tu B'Av":
            no_tachanun_reasons.append('ט"ו באב')
            break

    for holiday in hdate_info.holidays:
        if holiday.name == "Erev Rosh Hashana":
            no_tachanun_reasons.append("ערב ראש השנה")
            break

    for holiday in hdate_info.holidays:
        if holiday.name == "Erev Yom Kippur":
            no_tachanun_reasons.append("ערב יום כיפור")
            break

    if hdate_info.date.month == Months.TISHREI and hdate_info.date.day >= 11:
        no_tachanun_reasons.append('מי"א תשרי עד סוף תשרי')

    for holiday in hdate_info.holidays:
        if holiday.name == "Chanukah":
            no_tachanun_reasons.append("חנוכה")
            break

    for holiday in hdate_info.holidays:
        if holiday.name == "Tu BiShvat":
            no_tachanun_reasons.append('ט"ו בשבט')
            break

    for holiday in hdate_info.holidays:
        if holiday.name in ("Purim", "Shushan Purim"):
            no_tachanun_reasons.append("פורים / שושן פורים")
            break

    for holiday in hdate_info.holidays:
        if holiday.name == "Yom HaAtzmaut":
            no_tachanun_reasons.append("יום העצמאות")
            break

    for holiday in hdate_info.holidays:
        if holiday.name == "Yom Yerushalayim":
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
    await bot.send_message(chat_id=chat_id, text=message_text)


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
