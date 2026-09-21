import streamlit as st
import requests
import pandas as pd

# 1. ตั้งค่าหน้าตาของเว็บ
st.set_page_config(
    page_title="ระบบอัตราแลกเปลี่ยนเงินตรา", 
    page_icon="", 
    layout="centered"
)

st.title("ระบบแสดงอัตราแลกเปลี่ยนเงินตรา")
st.write("แอปพลิเคชันแสดงอัตราแลกเปลี่ยนและคำนวณการแลกเปลี่ยนเงินตรา (API: ExchangeRate-API)")

# API Key ของคุณ
API_KEY = "e794b35d7a64591a9e9f9263"

# 2. ฟังก์ชันดึงข้อมูลอัตราแลกเปลี่ยนจาก API
@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{base_currency}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# สกุลเงินหลักสำหรับตัวเลือก
currencies = ["USD", "THB", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "SGD"]

# 3. ส่วนคำนวณการแลกเปลี่ยนเงิน
st.subheader("คำนวณการแลกเปลี่ยนเงิน")

col1, col2, col3 = st.columns(3)

with col1:
    amount = st.number_input("จำนวนเงิน:", min_value=0.0, value=100.0, step=10.0)

with col2:
    from_curr = st.selectbox("จากสกุลเงิน:", currencies, index=0) # เริ่มต้น USD

with col3:
    to_curr = st.selectbox("ไปยังสกุลเงิน:", currencies, index=1) # เริ่มต้น THB

# ดึงข้อมูลจาก API
data = get_exchange_rates(from_curr)

if data and data.get("result") == "success":
    rates = data.get("conversion_rates", {})
    if to_curr in rates:
        rate = rates[to_curr]
        converted_amount = amount * rate
        st.success(f"**{amount:,.2f} {from_curr}** = **{converted_amount:,.2f} {to_curr}**")
        st.info(f"อัตราแลกเปลี่ยน: 1 {from_curr} = {rate:,.4f} {to_curr}")
    
    # 4. แสดงตารางเปรียบเทียบอัตราแลกเปลี่ยน
    st.subheader(f"ตารางอัตราแลกเปลี่ยนอ้างอิงจาก 1 {from_curr}")
    df_rates = pd.DataFrame(list(rates.items()), columns=["สกุลเงิน", "อัตราแลกเปลี่ยน"])
    filtered_df = df_rates[df_rates["สกุลเงิน"].isin(currencies)].reset_index(drop=True)
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.error("ไม่สามารถเชื่อมต่อดึงข้อมูล API ได้ กรุณาตรวจสอบการเชื่อมต่ออินเทอร์เน็ต")