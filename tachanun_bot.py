"""
בוט תחנון יומי לטלגרם
מחשב האם יש תחנון היום ושולח הודעה בוקר
"""

import os
import requests
from datetime import datetime
import pyluach.dates as hdate
import pyluach.hebrewcal as hcal

# ─────────────────────────────────────────
# הגדרות — שנה את הערכים האלה
# ─────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID        = os.environ.get("CHAT_ID",        "YOUR_CHAT_ID_HERE")
# ─────────────────────────────────────────


def get_hebrew_date():
    """מחזיר את התאריך העברי של היום"""
    today = datetime.now()
    h = hdate.HebrewDate.from_pydate(today)
    return h


def check_tachanun(h: hdate.HebrewDate) -> tuple[bool, str]:
    """
    מחזיר (יש_תחנון, סיבה)
    המקורות: שולחן ערוך או"ח סי' קלא
    """
    month = h.month   # 1=ניסן, 2=אייר, ... 7=תשרי ...
    day   = h.day

    # ─── ימים שאין בהם תחנון ───

    # שבת
    weekday = h.weekday()  # 7 = שבת
    if weekday == 7:
        return False, "שבת קודש"

    # ראש השנה (א-ב תשרי)
    if month == 7 and day in (1, 2):
        return False, "ראש השנה"

    # יום כיפור (י' תשרי)
    if month == 7 and day == 10:
        return False, "יום הכיפורים"

    # סוכות (ט\"ו-כב תשרי — כולל חוה\"מ ושמחת תורה)
    if month == 7 and 15 <= day <= 23:
        return False, "סוכות / שמיני עצרת / שמחת תורה"

    # חנוכה (כה כסלו – ב/ג טבת)
    if month == 9 and day >= 25:
        return False, "חנוכה"
    if month == 10 and day <= 3:
        return False, "חנוכה"

    # ט\"ו בשבט
    if month == 11 and day == 15:
        return False, "ט\"ו בשבט"

    # פורים ושושן פורים
    if month == 12 and day in (14, 15):
        return False, "פורים"
    # אדר א בשנה מעוברת
    if h.year_is_leap() and month == 13 and day in (14, 15):
        return False, "פורים קטן"

    # פסח (ניסן)
    if month == 1:
        if day >= 15:  # חוה\"מ, שביעי, אחרון של פסח
            return False, "פסח"
        if day == 14:  # ערב פסח
            return False, "ערב פסח"

    # ספירת העומר — ל\"ג בעומר
    if month == 2 and day == 18:
        return False, "ל\"ג בעומר"

    # שבועות (ו-ז סיון)
    if month == 3 and day in (6, 7):
        return False, "שבועות"

    # ט\"ו באב
    if month == 5 and day == 15:
        return False, "ט\"ו באב"

    # ראש חודש
    if day == 1 or (day == 30):
        # בדוק אם יש יום ל' בחודש הזה
        return False, "ראש חודש"

    # ערב ראש חודש — יש מנהגים שונים
    # (מופסק לפי מנהג אשכנז, לא לפי ספרד — אפשר להפעיל)
    # from pyluach.dates import HebrewDate
    # next_day = h + 1
    # if next_day.day == 1:
    #     return False, "ערב ראש חודש (מנהג אשכנז)"

    # ═══ ימים מיוחדים ═══

    # יום העצמאות (ה' אייר) — לנוהגים
    if month == 2 and day == 5:
        return False, "יום העצמאות (לנוהגים)"

    # יום ירושלים (כח אייר) — לנוהגים
    if month == 2 and day == 28:
        return False, "יום ירושלים (לנוהגים)"

    return True, "יום רגיל"


def format_hebrew_date(h: hdate.HebrewDate) -> str:
    """מחזיר תאריך עברי כטקסט"""
    months_he = {
        1: "ניסן", 2: "אייר", 3: "סיון", 4: "תמוז",
        5: "אב", 6: "אלול", 7: "תשרי", 8: "חשוון",
        9: "כסלו", 10: "טבת", 11: "שבט", 12: "אדר",
        13: "אדר ב'"
    }
    days_he = ["", "א'", "ב'", "ג'", "ד'", "ה'", "ו'", "ז'",
               "ח'", "ט'", "י'", "י\"א", "י\"ב", "י\"ג", "י\"ד",
               "ט\"ו", "ט\"ז", "י\"ז", "י\"ח", "י\"ט", "כ'",
               "כ\"א", "כ\"ב", "כ\"ג", "כ\"ד", "כ\"ה", "כ\"ו",
               "כ\"ז", "כ\"ח", "כ\"ט", "ל'"]
    return f"{days_he[h.day]} {months_he[h.month]} {h.year}"


def format_day_line(h: hdate.HebrewDate, label: str) -> str:
    """מחזיר שורה אחת עם סטטוס תחנון ליום נתון"""
    weekdays_he = {1: "ראשון", 2: "שני", 3: "שלישי",
                   4: "רביעי", 5: "חמישי", 6: "שישי", 7: "שבת"}
    day_name = weekdays_he.get(h.weekday(), "")
    date_str = format_hebrew_date(h)
    has_tachanun, reason = check_tachanun(h)
    emoji = "✅" if has_tachanun else "🚫"
    status = "יש תחנון" if has_tachanun else "אין תחנון"
    return (
        f"*{label} — יום {day_name}*\n"
        f"📅 {date_str}\n"
        f"{emoji} {status} | {reason}"
    )


def build_message(today: hdate.HebrewDate, tomorrow: hdate.HebrewDate) -> str:
    today_line    = format_day_line(today,    "היום")
    tomorrow_line = format_day_line(tomorrow, "מחר")
    return f"{today_line}\n\n{tomorrow_line}"


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    print("✅ הודעה נשלחה בהצלחה")


def main():
    today    = get_hebrew_date()
    tomorrow = today + 1
    message  = build_message(today, tomorrow)
    print(message)
    send_telegram(message)


if __name__ == "__main__":
    main()
