from flask import Flask, jsonify
from datetime import datetime, timedelta, date
import requests
import pytz

app = Flask(__name__)

# ====== 祝日数据（可自行更新扩展）======
JAPAN_HOLIDAYS = [
    {"name": "海の日", "date": "2025-07-21"},
    {"name": "山の日", "date": "2025-08-11"},
    {"name": "敬老の日", "date": "2025-09-15"},
    {"name": "秋分の日", "date": "2025-09-23"},
    {"name": "スポーツの日", "date": "2025-10-13"},
    {"name": "文化の日", "date": "2025-11-03"},
    {"name": "勤労感謝の日", "date": "2025-11-23"},
    {"name": "天皇誕生日", "date": "2025-12-23"},
]

# ====== 获取日语星期几 ======
def get_japanese_weekday(dt):
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    return weekdays[dt.weekday()]

# ====== 获取下一个周六还有几天 ======
def get_days_to_weekend(today):
    days_ahead = (5 - today.weekday()) % 7
    return days_ahead if days_ahead != 0 else 7

# ====== 计算两个日期之间的天数差 ======
def days_between(date1, date2):
    return (date2 - date1).days

# ====== 获取汇率（ExchangeRate.host） ======
def get_jpy_to_cny():
    try:
        response = requests.get("https://api.exchangerate.host/convert?from=JPY&to=CNY&amount=10000", timeout=5)
        response.raise_for_status()
        data = response.json()
        result = round(data["result"], 2)
        timestamp = datetime.now(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M")
        return result, timestamp
    except Exception as e:
        print("汇率获取失败：", e)
        return None, None

# ====== 主API入口 ======
@app.route("/api/japan-info")
def japan_info():
    tz = pytz.timezone("Asia/Tokyo")
    now = datetime.now(tz)
    today_str = now.strftime(f"%Y年%-m月%-d日（{get_japanese_weekday(now)}）")
    today = now.date()

    # 找出接下来的三个祝日
    upcoming = [h for h in JAPAN_HOLIDAYS if datetime.strptime(h["date"], "%Y-%m-%d").date() >= today][:3]

    # 获取汇率
    jpy_cny, exchange_time = get_jpy_to_cny()

    # 计算本月最后一天
    next_month = today.replace(day=28) + timedelta(days=4)
    month_end = next_month.replace(day=1) - timedelta(days=1)

    response = {
        "today": today_str,
        "next_holiday_1_name": upcoming[0]["name"] if len(upcoming) > 0 else None,
        "next_holiday_1_date": datetime.strptime(upcoming[0]["date"], "%Y-%m-%d").strftime("%-m月%-d日（{}）").format(get_japanese_weekday(datetime.strptime(upcoming[0]["date"], "%Y-%m-%d"))) if len(upcoming) > 0 else None,
        "next_holiday_2_name": upcoming[1]["name"] if len(upcoming) > 1 else None,
        "next_holiday_2_date": datetime.strptime(upcoming[1]["date"], "%Y-%m-%d").strftime("%-m月%-d日（{}）").format(get_japanese_weekday(datetime.strptime(upcoming[1]["date"], "%Y-%m-%d"))) if len(upcoming) > 1 else None,
        "next_holiday_3_name": upcoming[2]["name"] if len(upcoming) > 2 else None,
        "next_holiday_3_date": datetime.strptime(upcoming[2]["date"], "%Y-%m-%d").strftime("%-m月%-d日（{}）").format(get_japanese_weekday(datetime.strptime(upcoming[2]["date"], "%Y-%m-%d"))) if len(upcoming) > 2 else None,
        "days_to_next": days_between(today, datetime.strptime(upcoming[0]["date"], "%Y-%m-%d").date()) if len(upcoming) > 0 else None,
        "days_to_weekend": get_days_to_weekend(today),
        "days_to_month_end": days_between(today, month_end),
        "days_to_year_end": days_between(today, date(today.year, 12, 31)),
        "jpy_to_cny": jpy_cny,
        "exchange_update_time": exchange_time
    }

    return jsonify(response)

# ====== 启动 ======
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
