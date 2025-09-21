# single_api_tester.py
import time
import random
import threading
import phonenumbers

def api1(phone):
    """
    ตัวอย่าง placeholder - แทนที่ด้วยฟังก์ชัน api จริงของคุณ
    ฟังก์ชันต้อง return (response_like_object_or_None, ref_or_meta)
    """
    # ตัวอย่าง mock response
    class R:
        status_code = 200
        text = '{"code":1}'
    return R(), "N/A"
# --------------------------------------------------------------------

# ตั้งค่า
RATE_LIMIT_SECONDS = 30     # จำนวนวินาทีขั้นต่ำระหว่างการส่งแต่ละครั้ง (ป้องกัน spam)
MAX_RETRIES = 3             # จำนวนครั้ง retry ต่อการส่ง 1 ครั้ง
BACKOFF_BASE = 2            # exponential backoff factor
DRY_RUN = True              # True = ไม่ยิงจริง แค่พิมพ์ (สำหรับทดสอบ) -> เปลี่ยนเป็น False เมื่อแน่ใจแล้ว

# เลือก API ที่จะใช้ (ชื่อจาก mapping)
selected_api = "api1"  # เปลี่ยนเป็น api2, api3... ถ้ามี wrapper ให้เรียก

# mapping ของชื่อไปยังฟังก์ชันจริง
API_MAP = {
    "api1": api1,
    # "api2": api2,  # เพิ่มตามที่มีและเป็นของคุณ
}

def clean_phone_number(phone: str) -> str:
    p = phone.strip()
    # รองรับ +66 -> 0xxxxxxx
    if p.startswith("+66"):
        p = "0" + p[3:]
    p = "".join(filter(str.isdigit, p))
    return p

def is_valid_th_phone(phone: str) -> bool:
    try:
        parsed = phonenumbers.parse(phone, "TH")
        return phonenumbers.is_valid_number(parsed) and phonenumbers.number_type(parsed) == phonenumbers.PhoneNumberType.MOBILE
    except Exception:
        return False

def send_one(phone: str, api_func, dry_run=True):
    """
    ส่งครั้งเดียวด้วย retry + backoff
    คืนค่า (success: bool, info: dict)
    """
    for attempt in range(1, MAX_RETRIES + 1):
        if dry_run:
            print(f"[DRY] Attempt {attempt}: would call API with phone={phone}")
            return True, {"attempts": attempt, "dry_run": True}
        try:
            start = time.time()
            resp, meta = api_func(phone)
            elapsed = time.time() - start
            success = resp is not None and getattr(resp, "status_code", 0) in (200, 201)
            print(f"Attempt {attempt} | status={getattr(resp,'status_code',None)} | time={elapsed:.2f}s | meta={meta}")
            if success:
                return True, {"attempts": attempt, "response": resp, "meta": meta}
        except Exception as e:
            print(f"Attempt {attempt} exception:", e)

        # ถ้าไม่สำเร็จ -> backoff ก่อน retry
        sleep_t = BACKOFF_BASE ** (attempt - 1) + random.uniform(0, 1)
        print(f"Retry in {sleep_t:.1f}s...")
        time.sleep(sleep_t)
    return False, {"attempts": MAX_RETRIES}

def send_multiple(phone: str, attempts: int, api_name: str, dry_run=True):
    """
    ส่งหลายครั้งโดยเคารพ rate limit ระหว่างการยิงแต่ละครั้ง
    """
    if api_name not in API_MAP:
        print("API ที่เลือกไม่มีใน mapping")
        return

    api_func = API_MAP[api_name]
    last_sent = 0
    successes = 0

    for i in range(attempts):
        now = time.time()
        wait = max(0, RATE_LIMIT_SECONDS - (now - last_sent))
        if wait > 0:
            print(f"Waiting {wait:.1f}s to respect rate limit...")
            time.sleep(wait)

        print(f"=== Sending attempt #{i+1} ===")
        ok, info = send_one(phone, api_func, dry_run=dry_run)
        if ok:
            successes += 1
        last_sent = time.time()

    print(f"Finished: requested={attempts}, success={successes}")

if __name__ == "__main__":
    raw_phone = input("ใส่เบอร์ (เช่น 0812345678 หรือ +66812345678): ").strip()
    cleaned = clean_phone_number(raw_phone)
    if not is_valid_th_phone(cleaned):
        print("เบอร์ไม่ถูกต้องหรือไม่ใช่มือถือไทย — หยุดการทำงาน")
    else:
        try:
            n = int(input("จำนวนครั้งที่ต้องการส่ง: "))
        except:
            print("จำนวนต้องเป็นจำนวนเต็ม")
            raise SystemExit
        # เรียกใช้ (DRY_RUN = True แนะนำให้ทดสอบก่อน)
        send_multiple(cleaned, n, selected_api, dry_run=DRY_RUN)
