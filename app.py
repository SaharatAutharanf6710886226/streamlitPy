import pandas as pd
import requests
import streamlit as st

# 1. ตั้งค่าหน้าตาของเว็บ
st.set_page_config(
    page_title="ระบบอัตราแลกเปลี่ยนเงินตรา", page_icon="💱", layout="centered"
)

st.title("💱 ระบบแสดงอัตราแลกเปลี่ยนเงินตรา")
st.write(
    "แอปพลิเคชันแสดงอัตราแลกเปลี่ยนและคำนวณการแลกเปลี่ยนเงินตราระหว่างสกุลเงินต่างๆ"
    " (API: ExchangeRate-API)"
)


# 2. ฟังก์ชันดึงข้อมูลอัตราแลกเปลี่ยนจาก ExchangeRate-API
@st.cache_data(ttl=3600)
def get_exchange_rates(base_currency):
  url = f"https://open.er-api.com/v6/latest/{base_currency}"
  try:
    response = requests.get(url)
    if response.status_code == 200:
      return response.json()
  except Exception:
    return None
  return None


# รายชื่อสกุลเงินสำรอง
default_currencies = [
    "USD",
    "THB",
    "EUR",
    "JPY",
    "GBP",
    "AUD",
    "CAD",
    "CHF",
    "CNY",
    "SGD",
    "KRW",
    "HKD",
]

# ดึงรายชื่อสกุลเงินทั้งหมดจาก API
initial_data = get_exchange_rates("USD")
if initial_data and initial_data.get("result") == "success":
  all_currencies = sorted(list(initial_data["rates"].keys()))
else:
  all_currencies = default_currencies

st.divider()

# -------------------------------------------------------------
# ส่วนที่ 1: การแลกเปลี่ยนเงินตราระหว่างสกุลเงินต่างๆ (From -> To)
# -------------------------------------------------------------
st.header("💵 คำนวณการแลกเปลี่ยนเงินตรา")

col1, col2 = st.columns(2)

with col1:
  base_currency = st.selectbox(
      "เลือกสกุลเงินต้นทาง (From):",
      all_currencies,
      index=(
          all_currencies.index("USD") if "USD" in all_currencies else 0
      ),
  )

with col2:
  target_currency = st.selectbox(
      "เลือกสกุลเงินปลายทาง (To):",
      all_currencies,
      index=(
          all_currencies.index("THB") if "THB" in all_currencies else 0
      ),
  )

amount = st.number_input(
    "จำนวนเงินที่ต้องการแลกเปลี่ยน:",
    min_value=0.01,
    value=100.0,
    step=10.0,
    format="%.2f",
)

# ดึงข้อมูลอัตราแลกเปลี่ยนของสกุลเงินต้นทางที่เลือก
data = get_exchange_rates(base_currency)

if data and data.get("result") == "success":
  rates = data["rates"]

  # คำนวณผลการแลกเปลี่ยน
  if target_currency in rates:
    rate = rates[target_currency]
    total_converted = amount * rate

    st.success(
        f"### {amount:,.2f} {base_currency} = {total_converted:,.2f}"
        f" {target_currency}"
    )
    st.info(
        f"💡 อัตราแลกเปลี่ยนปัจจุบัน: 1 {base_currency} = {rate:,.4f}"
        f" {target_currency}"
    )

  st.divider()

  # -------------------------------------------------------------
  # ส่วนที่ 2: ตารางแสดงอัตราแลกเปลี่ยนเทียบกับสกุลเงินอื่นๆ
  # -------------------------------------------------------------
  st.header(
      f"📊 ตารางอัตราแลกเปลี่ยนของ 1 {base_currency} เทียบกับสกุลเงินอื่น"
  )

  # ช่องค้นหาสกุลเงิน
  search_keyword = st.text_input(
      "🔍 ค้นหาสกุลเงิน (เช่น THB, EUR, JPY):", ""
  ).upper()

  # แสดงตาราง DataFrame
  df_rates = pd.DataFrame(
      list(rates.items()),
      columns=["สกุลเงิน (Currency)", "อัตราแลกเปลี่ยน (Exchange Rate)"],
  )

  if search_keyword:
    df_rates = df_rates[
        df_rates["สกุลเงิน (Currency)"].str.contains(search_keyword)
    ]

  st.dataframe(df_rates, use_container_width=True, height=350)

  # แสดงเวลาอัปเดตข้อมูล
  last_updated = data.get("time_last_update_utc", "N/A")
  st.caption(f"🕒 อัปเดตข้อมูลอัตราแลกเปลี่ยนล่าสุดเมื่อ: {last_updated}")

else:
  st.error(
      "ไม่สามารถเชื่อมต่อข้อมูลจาก ExchangeRate-API ได้"
      " โปรดตรวจสอบการเชื่อมต่ออินเทอร์เน็ต"
  )

# ท้ายหน้าแสดงที่มาข้อมูลตามข้อกำหนด API
st.markdown("---")
st.markdown(
    "ข้อมูลอัตราแลกเปลี่ยนอ้างอิงจาก"
    " [ExchangeRate-API](https://www.exchangerate-api.com/)"
)