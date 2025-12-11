import cv2  # type: ignore
import math
import time
import random
import json # لإعداد بيانات التنبيه بصيغة الإرسال إلى السحابة
from ultralytics import YOLO # type: ignore

# ---------------------------------------------------------
# إعدادات النظام الأساسية
# ---------------------------------------------------------
print("جاري تحميل نموذج الذكاء الاصطناعي YOLOv8n... ⏳")
# نموذج خفيف وسريع للكشف عن الأجسام
model = YOLO("yolov8n.pt") 

# الأغراض الممنوعة (لغرض المحاكاة)
PROHIBITED_ITEMS = ["bottle", "scissors", "knife", "cell phone"]

# موقع GPS المحاكى للجهاز (Al Bukayriyah, KSA)
MOCK_GPS_LOCATION = {"latitude": 26.1306, "longitude": 43.5186}

# ---------------------------------------------------------
# محاكاة الحساسات (Sensors Simulation Module)
# ---------------------------------------------------------
def get_sensor_readings():
    """
    تحاكي قراءة حساس الغاز والمواد الطيفية.
    """
    # 1. محاكاة حساس الغاز (MQ-Series)
    # قيمة عشوائية تحاكي الكشف (الخطر فوق 80)
    gas_level = random.randint(5, 95) 
    
    # 2. محاكاة حساس التحليل الطيفي (Spectroscopy)
    # ناتج التحليل الطيفي: يتم توليده عشوائياً، لكن لو كان الغاز مرتفعاً نزيد احتمالية الخطر
    if gas_level > 85:
        spectral_match = "COCAINE_TRACE" # محاكاة اكتشاف مادة
    else:
        spectral_match = "NO_=MATCH"
        
    return gas_level, spectral_match

# ---------------------------------------------------------
# وظيفة إرسال التنبيه (Mock IoT Communication)
# ---------------------------------------------------------
def send_alert_to_cloud(alert_data): # type: ignore
    """
    تحاكي إرسال البيانات المشفرة إلى منصة الإدارة المركزية عبر ملف alerts.json.
    """
    ALERT_FILE = "alerts.json"
    
    # قراءة البيانات القديمة
    try:
        with open(ALERT_FILE, 'r') as f:
            alerts_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        alerts_list = []

    # إضافة التنبيه الجديد
    alerts_list.append(alert_data)
    
    # كتابة قائمة التنبيهات المحدثة
    with open(ALERT_FILE, 'w') as f:
        json.dump(alerts_list, f, indent=4)
    
    print(f"\n--- 🌐 ALERT SENT and Logged to {ALERT_FILE} ---")

# ---------------------------------------------------------
# التشغيل الرئيسي والتحليل
# ---------------------------------------------------------
cap = cv2.VideoCapture(0) # فتح الكاميرا
cap.set(3, 1280) # العرض
cap.set(4, 720)  # الطول

print("\n🚀 CognifyX System Online - Running Simulation Mode...")

while True:
    success, img = cap.read()
    if not success:
        break

    # الحالة الافتراضية للنظام
    system_status = "SECURE ✅"
    alert_triggered = False
    color_status = (0, 255, 0) # أخضر

    # 1. قراءة الحساسات المحاكاة
    gas_level, spectral_match = get_sensor_readings()

    # 2. تحليل الرؤية الحاسوبية
    results = model(img, stream=True, verbose=False)
    
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_name = model.names[int(box.cls[0])]
            
            # 🚨 منطق كشف الممنوعات البصرية
            if class_name in PROHIBITED_ITEMS:
                alert_triggered = True
                system_status = f"WARNING: {class_name.upper()} DETECTED"
                
                # رسم مربع أحمر حول الجسم
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)

    # 3. دمج منطق الحساسات مع الرؤية
    if spectral_match != "NO_MATCH": # type: ignore
        alert_triggered = True
        system_status = f"CRITICAL: {spectral_match} TRACE FOUND!"

    elif gas_level > 85:
        # لو كان الغاز مرتفعاً جداً (حالة تحذير كيميائي)
        alert_triggered = True
        system_status = "CHEM ALERT: High Volatile Compound"
        color_status = (0, 165, 255) # برتقالي

    # 4. إصدار التنبيه والإرسال
    if alert_triggered:
        color_status = (0, 0, 255) # أحمر للخطر البصري والكيميائي
        
        # إنشاء حمولة التنبيه (Payload)
        alert_payload = {
            "Time": time.strftime("%H:%M:%S"),
            "Location": MOCK_GPS_LOCATION,
            "Trigger": system_status,
            "Sensor_Data": {"Gas_PPM": gas_level, "Spectral_Match": spectral_match}
        }
        
        # إرسال التنبيه (المحاكاة)
        send_alert_to_cloud(alert_payload)
        time.sleep(1) # تأخير لمنع إرسال مئات التنبيهات في الثانية الواحدة

    # 5. عرض الواجهة (UI)
    cv2.rectangle(img, (0, 0), (1280, 100), (0, 0, 0), -1)
    
    # عرض الحالة
    cv2.putText(img, "CognifyX STATUS:", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img, system_status, (350, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_status, 3)

    # عرض الحساسات
    cv2.putText(img, f"Gas: {gas_level} | Spec: {spectral_match}", (20, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow('CognifyX - Edge AI Simulation', img)

    # الخروج بالضغط على 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()