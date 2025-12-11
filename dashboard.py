import streamlit as st # type: ignore
import pandas as pd # type: ignore
import json
import time

st.set_page_config(layout="wide")
st.title("🛡️ CognifyX: منصة الإدارة المركزية")

ALERT_FILE = "alerts.json"
MAP_CENTER = [26.1306, 43.5186] # موقع البكيرية (الافتراضي)

# دالة لتحميل البيانات وتحديثها
@st.cache_data(ttl=1) # تحديث البيانات كل 1 ثانية  # type: ignore
def load_alert_data():
    try:
        with open(ALERT_FILE, 'r') as f:
            data = json.load(f)
            
        # تحويل بيانات التنبيه إلى DataFrame لعرضها في جدول وخريطة
        df = pd.DataFrame(data)
        
        # تنسيق الأسماء لتناسب Streamlit Map
        df['lat'] = df['Location'].apply(lambda x: x['latitude']) # type: ignore
        df['lon'] = df['Location'].apply(lambda x: x['longitude']) # type: ignore
        
        return df
    
    except (FileNotFoundError, json.JSONDecodeError):
        return pd.DataFrame()

# -----------------
# عرض الواجهة
# -----------------

# لإجبار الصفحة على التحديث كل فترة قصيرة
st.rerun() # هذه الدالة بديلة للدالة الأقدم

st.subheader("سجل التنبيهات الحية")

alerts_df = load_alert_data()

if alerts_df.empty:
    st.info("النظام آمن. لا يوجد بلاغات واردة.")
else:
    # عرض آخر تنبيه في الأعلى
    latest_alert = alerts_df.iloc[-1]
    
    st.error(f"🚨 **تنبيه عاجل** في {latest_alert['Time']} - التهديد: **{latest_alert['Trigger']}**")
    st.write(f"بيانات الحساس: {latest_alert['Sensor_Data']}")
    
    # عرض التنبيهات على الخريطة
    st.subheader("موقع البلاغ الجغرافي (GPS)")
    st.map(alerts_df, latitude='lat', longitude='lon', zoom=10)
    
    # عرض سجل كامل للبيانات
    st.subheader("السجل الكامل")
    st.dataframe(alerts_df)


# عرض حالة الجهاز الطرفي
st.sidebar.title("إعدادات الجهاز")
st.sidebar.metric("عدد البلاغات", len(alerts_df))
st.sidebar.metric("الحالة", "متصل" if not alerts_df.empty else "انتظار")