from machine import Pin, ADC, RTC
import time

# --- إعداد ساعة الوقت الحقيقي (Real Time Clock) ---
rtc = RTC()

# ملاحظة: البيكو لا يحتفظ بالوقت عند فصل الكهرباء.
# يمكنك ضبط الوقت الحالي يدوياً هنا عند تشغيل الكود لأول مرة:
# الصيغة: (سنة, شهر, يوم, يوم_من_أسبوع, ساعة, دقيقة, ثانية, ميكروثانية)
# مثال: rtc.datetime((2023, 10, 25, 3, 14, 30, 0, 0))

# --- إعداد الحساسات ---
# حساس الغاز القديم على GP26
gas_sensor = ADC(26)
# حساس المخدرات الجديد على GP27
drug_sensor = ADC(27)

# --- إعداد شاشات البار (LED Bar Graphs) ---
# البار الأخضر (للغاز)
gas_leds = [Pin(i, Pin.OUT) for i in range(10)]

# البار الأحمر (للمخدرات)
drug_leds = [Pin(i, Pin.OUT) for i in range(10, 20)]

# --- إعدادات المعايرة ---
RAW_MIN = 13475
RAW_MAX = 64655
NUM_LEDS = 10

# حساب العتبات
THRESHOLD_LEVELS = [
    RAW_MIN + ((RAW_MAX - RAW_MIN) * (i + 1)) // NUM_LEDS
    for i in range(NUM_LEDS)
]

# --- دالة التحديث ---
def update_bar_graph(value, pins):
    for i in range(NUM_LEDS):
        pins[i].value(1 if value >= THRESHOLD_LEVELS[i] else 0)

print("System Started - Dual Detection Mode (Gas & Drugs)")

while True:
    # 1. جلب الوقت الحالي
    t = rtc.datetime()
    # تنسيق الوقت ليظهر بشكل: HH:MM:SS
    # t[4]=الساعة, t[5]=الدقيقة, t[6]=الثانية
    timestamp = "{:02d}:{:02d}:{:02d}".format(t[4], t[5], t[6])

    # 2. قراءة القيم من الحساسين
    gas_val = gas_sensor.read_u16()
    drug_val = drug_sensor.read_u16()
    
    # 3. طباعة الوقت مع القيم
    print(f"[{timestamp}] نسبة الغاز: {gas_val} | نسبة المخدرات: {drug_val}")
    
    # 4. تحديث المؤشرات الضوئية
    update_bar_graph(gas_val, gas_leds)
    update_bar_graph(drug_val, drug_leds)
    
    time.sleep(1)