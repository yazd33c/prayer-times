import json
import time
import urllib.request
import os

# تنظیمات
TOTAL_POINTS = 25000  # تعداد کل نقاط مورد نیاز
BATCH_SIZE = 500      # تعداد درخواست در هر بار اجرا
OUTPUT_FILE = "elevation_data.json"
PROGRESS_FILE = "progress.json"

def get_elevation(lat, lng):
    url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={lng}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data["elevation"][0]
    except Exception as e:
        print(f"Error fetching {lat},{lng}: {e}")
        return None

def main():
    # خواندن پیشرفت قبلی
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            progress = json.load(f)
    else:
        progress = {"current_index": 0}

    # خواندن داده‌های ذخیره شده قبلی
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            db = json.load(f)
    else:
        db = {}

    start = progress["current_index"]
    print(f"Starting from point {start} to {start + BATCH_SIZE}")

    # تولید نقاط (مثلاً شبکه‌ای برای ایران)
    # این یک نمونه است، بعداً می‌توانیم مختصات دقیق شهرها را جایگزین کنیم
    count = 0
    for i in range(start, min(start + BATCH_SIZE, TOTAL_POINTS)):
        lat = 25.0 + (i * 0.01)  # تولید عرض جغرافیایی
        lng = 45.0 + (i * 0.01)  # تولید طول جغرافیایی
        key = f"{lat:.4f},{lng:.4f}"
        
        if key in db:
            continue

        elev = get_elevation(lat, lng)
        if elev is not None:
            db[key] = elev
            count += 1
        
        # تاخیر برای جلوگیری از بلاک شدن
        time.sleep(0.15)

    progress["current_index"] = start + BATCH_SIZE

    # ذخیره داده‌ها
    with open(OUTPUT_FILE, "w") as f:
        json.dump(db, f)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

    print(f"Saved {count} new points. Total: {len(db)}")

if __name__ == "__main__":
    main()