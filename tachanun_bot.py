import os
from datetime import date
from hdate.date_info import HDateInfo
from hdate import Months

from telegram import Bot
import asyncio

async def send_telegram_message(chat_id, message_text, bot_token):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message_text)

def get_tachanun_status():
    today = date.today()
    hdate_today = HDateInfo(today, diaspora=True)
    
    no_tachanun_reasons = []
    
    # Shabbat and Jewish holidays (Yom Tov)
    if hdate_today.is_shabbat:
        no_tachanun_reasons.append("שבת")
    if hdate_today.is_yom_tov:
        no_tachanun_reasons.append("יום טוב")
    
    # Rosh Chodesh (first of Hebrew month)
    for holiday in hdate_today.holidays:
        if holiday.name == "Rosh Chodesh":
            no_tachanun_reasons.append("ראש חודש")
            break

    # The entire month of Nisan
    if hdate_today.date.month == Months.NISAN:
        no_tachanun_reasons.append("כל חודש ניסן")

    # Lag BaOmer
    for holiday in hdate_today.holidays:
        if holiday.name == "Lag BaOmer":
            no_tachanun_reasons.append("ל""ג בעומר")
            break

    # From Rosh Chodesh Sivan until and including the 12th of Sivan
    if hdate_today.date.month == Months.SIVAN and hdate_today.date.day <= 12:
        no_tachanun_reasons.append("מראש חודש סיוון עד י""ב בסיוון")

    # Tisha B'Av
    for holiday in hdate_today.holidays:
        if holiday.name == "Tisha B'Av":
            no_tachanun_reasons.append("תשעה באב")
            break

    # Tu B'Av (15 Av)
    for holiday in hdate_today.holidays:
        if holiday.name == "Tu B'Av":
            no_tachanun_reasons.append("ט""ו באב")
            break

    # Erev Rosh Hashana
    for holiday in hdate_today.holidays:
        if holiday.name == "Erev Rosh Hashana":
            no_tachanun_reasons.append("ערב ראש השנה")
            break

    # Erev Yom Kippur
    for holiday in hdate_today.holidays:
        if holiday.name == "Erev Yom Kippur":
            no_tachanun_reasons.append("ערב יום כיפור")
            break

    # From 11 Tishrei to end of Tishrei (after Yom Kippur through Simchat Torah)
    if hdate_today.date.month == Months.TISHREI and hdate_today.date.day >= 11:
        no_tachanun_reasons.append("מ-י""א בתשרי עד סוף תשרי")

    # Chanukah (25 Kislev - 2 or 3 Tevet)
    for holiday in hdate_today.holidays:
        if holiday.name == "Chanukah":
            no_tachanun_reasons.append("חנוכה")
            break

    # Tu BiShvat (15 Shvat)
    for holiday in hdate_today.holidays:
        if holiday.name == "Tu BiShvat":
            no_tachanun_reasons.append("ט""ו בשבט")
            break

    # Purim and Shushan Purim (14-15 Adar)
    for holiday in hdate_today.holidays:
        if holiday.name == "Purim" or holiday.name == "Shushan Purim":
            no_tachanun_reasons.append("פורים ושושן פורים")
            break

    # Yom HaAtzmaut (5 Iyar)
    for holiday in hdate_today.holidays:
        if holiday.name == "Yom HaAtzmaut":
            no_tachanun_reasons.append("יום העצמאות")
            break

    # Yom Yerushalayim (28 Iyar)
    for holiday in hdate_today.holidays:
        if holiday.name == "Yom Yerushalayim":
            no_tachanun_reasons.append("יום ירושלים")
            break

    hebrew_date_str = str(hdate_today.date)

    if no_tachanun_reasons:
        reason_str = ", ".join(no_tachanun_reasons)
        return f"✨ היום אין תחנון! 🎉 סיבה: {reason_str}. תאריך עברי: {hebrew_date_str}"
    else:
        return f"🙏 היום יש תחנון בתפילה. תאריך עברי: {hebrew_date_str}"

async def main():
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8971218554:AAF0Dv3nG7PRebV7oF4v5IPLmmHy6kQwXV8")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "789180775")

    message = get_tachanun_status()
    await send_telegram_message(telegram_chat_id, message, telegram_bot_token)

if __name__ == "__main__":
    asyncio.run(main())
