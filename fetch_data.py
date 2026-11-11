import json
import time
import urllib.request
import os

# تنظیمات محدوده (یزد و همسایه‌ها)
LAT_MIN = 29.0
LAT_MAX = 35.5
LNG_MIN = 51.0
LNG_MAX = 60.0
STEP = 0.02 # <--- تغییر گام به 0.02 درجه (دقت بالاتر)

BATCH_SIZE = 1000 # در هر اجرا 1000 نقطه دانلود می‌کند
OUTPUT_FILE = "elevation_data_002.json" # <--- نام فایل جدید
PROGRESS_FILE = "progress_002.json"     # <--- نام فایل پیشرفت جدید

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
    # ساخت لیست تمام نقاط
    points = []
    lat = LAT_MIN
    while lat <= LAT_MAX:
        lng = LNG_MIN
        while lng <= LNG_MAX:
            points.append((round(lat, 4), round(lng, 4)))
            lng += STEP
        lat += STEP

    TOTAL_POINTS = len(points)
    print(f"Total points to fetch for 0.02 degree grid: {TOTAL_POINTS}")

    # خواندن پیشرفت قبلی
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            progress = json.load(f)
    else:
        progress = {"current_index": 0}

    # خواندن داده‌های ذخیره شده
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            db = json.load(f)
    else:
        db = {}

    start = progress["current_index"]
    if start >= TOTAL_POINTS:
        print("All points for 0.02 grid already fetched.")
        return

    end = min(start + BATCH_SIZE, TOTAL_POINTS)
    print(f"Starting from point {start} to {end}")

    count = 0
    for i in range(start, end):
        lat, lng = points[i]
        key = f"{lat},{lng}"
        
        if key in db:
            continue

        elev = get_elevation(lat, lng)
        if elev is not None:
            db[key] = elev
            count += 1
        
        time.sleep(0.15) # تاخیر برای جلوگیری از بلاک شدن

    progress["current_index"] = end

    # ذخیره داده‌ها
    with open(OUTPUT_FILE, "w") as f:
        json.dump(db, f)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

    print(f"Saved {count} new points. Total in DB: {len(db)}")

if __name__ == "__main__":
    main()
