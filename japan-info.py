from flask import Flask, Response
import requests
import json
from datetime import datetime, timedelta, date

app = Flask(__name__)

# 日本法定节日（示例）
JAPANESE_HOLIDAYS = [
    # 2025 年
    {"name": "元日", "date": date(2025, 1, 1)},
    {"name": "成人の日", "date": date(2025, 1, 13)},
    {"name": "建国記念の日", "date": date(2025, 2, 11)},
    {"name": "天皇誕生日", "date": date(2025, 2, 23)},
    {"name": "春分の日", "date": date(2025, 3, 20)},
    {"name": "昭和の日", "date": date(2025, 4, 29)},
    {"name": "憲法記念日", "date": date(2025, 5, 3)},
    {"name": "みどりの日", "date": date(2025, 5, 4)},
    {"name": "こどもの日", "date": date(2025, 5, 5)},
    {"name": "憲法記念日 振替休日", "date": date(2025, 5, 6)},
    {"name": "海の日", "date": date(2025, 7, 21)},
    {"name": "山の日", "date": date(2025, 8, 11)},
    {"name": "敬老の日", "date": date(2025, 9, 15)},
    {"name": "秋分の日", "date": date(2025, 9, 23)},
    {"name": "スポーツの日", "date": date(2025, 10, 13)},
    {"name": "文化の日", "date": date(2025, 11, 3)},
    {"name": "勤労感謝の日", "date": date(2025, 11, 23)},
    {"name": "勤労感謝の日 振替休日", "date": date(2025, 11, 24)},

    # 2026 年
    {"name": "元日", "date": date(2026, 1, 1)},
    {"name": "成人の日", "date": date(2026, 1, 12)},
    {"name": "建国記念の日", "date": date(2026, 2, 11)},
    {"name": "天皇誕生日", "date": date(2026, 2, 23)},
    {"name": "春分の日", "date": date(2026, 3, 20)},
    {"name": "昭和の日", "date": date(2026, 4, 29)},
    {"name": "憲法記念日", "date": date(2026, 5, 3)},
    {"name": "みどりの日", "date": date(2026, 5, 4)},
    {"name": "こどもの日", "date": date(2026, 5, 5)},
    {"name": "憲法記念日 振替休日", "date": date(2026, 5, 6)},
    {"name": "海の日", "date": date(2026, 7, 20)},
    {"name": "山の日", "date": date(2026, 8, 11)},
    {"name": "敬老の日", "date": date(2026, 9, 21)},
    {"name": "国民の休日", "date": date(2026, 9, 22)},
    {"name": "秋分の日", "date": date(2026, 9, 23)},
    {"name": "スポーツの日", "date": date(2026, 10, 12)},
    {"name": "文化の日", "date": date(2026, 11, 3)},
    {"name": "勤労感謝の日", "date": date(2026, 11, 23)},

    # 2027 年
    {"name": "元日", "date": date(2027, 1, 1)},
    {"name": "成人の日", "date": date(2027, 1, 11)},
    {"name": "建国記念の日", "date": date(2027, 2, 11)},
    {"name": "天皇誕生日", "date": date(2027, 2, 23)},
    {"name": "春分の日", "date": date(2027, 3, 21)},
    {"name": "春分の日 振替休日", "date": date(2027, 3, 22)},
    {"name": "昭和の日", "date": date(2027, 4, 29)},
    {"name": "憲法記念日", "date": date(2027, 5, 3)},
    {"name": "みどりの日", "date": date(2027, 5, 4)},
    {"name": "こどもの日", "date": date(2027, 5, 5)},
    {"name": "海の日", "date": date(2027, 7, 19)},
    {"name": "山の日", "date": date(2027, 8, 11)},
    {"name": "敬老の日", "date": date(2027, 9, 20)},
    {"name": "秋分の日", "date": date(2027, 9, 23)},
    {"name": "スポーツの日", "date": date(2027, 10, 11)},
    {"name": "文化の日", "date": date(2027, 11, 3)},
    {"name": "勤労感謝の日", "date": date(2027, 11, 23)},
]

def get_next_weekend(today):
    weekday = today.weekday()
    return (5 - weekday) % 7 if weekday < 5 else 0

def get_exchange_rate():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/JPY", timeout=5)
        data = res.json()
        rate = data["rates"]["CNY"]
        jpy_to_cny = round(rate * 10000, 2)
        update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        return jpy_to_cny, update_time
    except Exception as e:
        print("⚠️ 汇率获取失败：", e)
        return None, None

@app.route("/api/japan-info")
def japan_info():
    today = date.today()

    holidays = [h for h in JAPANESE_HOLIDAYS if h["date"] > today]
    days_to_next = (holidays[0]["date"] - today).days if holidays else None

    if today.month < 12:
        next_month_start = date(today.year, today.month + 1, 1)
    else:
        next_month_start = date(today.year + 1, 1, 1)
    days_to_month_end = (next_month_start - timedelta(days=1) - today).days

    jpy_to_cny, exchange_time = get_exchange_rate()

    response = {
        "today": today.strftime("%Y年%-m月%-d日（%a）"),
        "next_holiday_1_name": holidays[0]["name"] if len(holidays) > 0 else "",
        "next_holiday_1_date": holidays[0]["date"].strftime("%-m月%-d日（月）") if len(holidays) > 0 else "",
        "next_holiday_2_name": holidays[1]["name"] if len(holidays) > 1 else "",
        "next_holiday_2_date": holidays[1]["date"].strftime("%-m月%-d日（月）") if len(holidays) > 1 else "",
        "next_holiday_3_name": holidays[2]["name"] if len(holidays) > 2 else "",
        "next_holiday_3_date": holidays[2]["date"].strftime("%-m月%-d日（月）") if len(holidays) > 2 else "",
        "days_to_next": days_to_next,
        "days_to_weekend": get_next_weekend(today),
        "days_to_month_end": days_to_month_end,
        "days_to_year_end": (date(today.year + 1, 1, 1) - today).days,
        "jpy_to_cny": jpy_to_cny,
        "exchange_update_time": exchange_time
    }

    return Response(
        json.dumps(response, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
