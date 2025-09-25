# คือ project ยิงเบอร์

# 📱 Single API Tester  

สคริปต์ Python สำหรับทดสอบยิง API ที่เกี่ยวข้องกับ **เบอร์โทรศัพท์**  
มีระบบ  
- **Rate limit** (เว้นช่วงระหว่างยิง)  
- **Retry + Backoff** (ยิงซ้ำอัตโนมัติถ้าล้มเหลว)  
- **Dry run** (ไม่ยิงจริง แค่พิมพ์)

> ⚠️ **ก่อนใช้จริง**: ติดตั้งไลบรารี `phonenumbers` ก่อน  
> ```bash
> pip install phonenumbers
> ```

---

## 🚀 วิธีใช้งาน  

1. รันไฟล์  
   ```bash
   python single_api_tester.py

# --------------------------------------------------------------------
# ตั้งค่า
RATE_LIMIT_SECONDS = 30     # จำนวนวินาทีขั้นต่ำระหว่างการส่งแต่ละครั้ง (ป้องกัน spam)
MAX_RETRIES = 3             # จำนวนครั้ง retry ต่อการส่ง 1 ครั้ง
BACKOFF_BASE = 2            # exponential backoff factor
DRY_RUN = True              # True = ไม่ยิงจริง แค่พิมพ์ (สำหรับทดสอบ) -> เปลี่ยนเป็น False เมื่อแน่ใจแล้ว

# เลือก API ที่จะใช้ (ชื่อจาก mapping)
selected_api = "api1"  # เปลี่ยนเป็น api2, api3... ถ้ามี wrapper ให้เรียก


