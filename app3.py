import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Apple Watch 頂級客製化 BOM 估算系統", layout="wide")
st.title("⌚ Apple Watch 頂級客製化與 BOM 成本估算系統")
st.write("即時輸入產量、材質、毛利率、供應商前置期，並支援成本敏感度分析與多工作表 Excel 完整匯出！")

st.sidebar.header("⚙️ 訂單規格設定")
volume = st.sidebar.number_input("生產數量 (pcs)", min_value=1, max_value=1000000, value=20000, step=1)
material = st.sidebar.selectbox("主要錶殼材質選擇", ["航太鈦金屬", "高階陶瓷", "鍛造碳纖維"])

st.sidebar.markdown("---")
st.sidebar.header("📈 毛利與定價策略設定")
target_margin = st.sidebar.slider("目標毛利率 (%)", min_value=10, max_value=80, value=55, step=1)

st.sidebar.markdown("---")
st.sidebar.header("⚖️ 交叉比較設定")
all_materials = ["航太鈦金屬", "高階陶瓷", "鍛造碳纖維"]
selected_materials = st.sidebar.multiselect("選擇要交叉比較的材質", options=all_materials, default=all_materials)

st.sidebar.markdown("---")
st.sidebar.header("📊 供應鏈成本敏感度分析")
pcba_fluctuation = st.sidebar.slider("智慧手錶 PCBA (晶片) 價格波動 (%)", min_value=-20, max_value=20, value=0, step=1)
screen_fluctuation = st.sidebar.slider("AMOLED 螢幕總成價格波動 (%)", min_value=-20, max_value=20, value=0, step=1)
casing_fluctuation = st.sidebar.slider("外殼 CNC 加工價格波動 (%)", min_value=-20, max_value=20, value=0, step=1)

if volume >= 50000:
    scale_factor = 0.85
elif volume >= 10000:
    scale_factor = 0.90
else:
    scale_factor = 1.00

material_multiplier = {"航太鈦金屬": 1.0, "高階陶瓷": 1.25, "鍛造碳纖維": 1.4}
current_multiplier = scale_factor * material_multiplier[material]

pcba_factor = scale_factor * (1 + pcba_fluctuation / 100)
screen_factor = scale_factor * (1 + screen_fluctuation / 100)
casing_multiplier = current_multiplier * (1 + casing_fluctuation / 100)

data = []
data.append({
    "階層": "L1.1", "模組分類": "機構外殼", 
    "項目": material + "錶殼與底蓋 (含CNC)", 
    "單價低 (USD)": round(14.25 * casing_multiplier, 2), 
    "單價高 (USD)": round(16.80 * casing_multiplier, 2), 
    "成本占比": "26%", "供應商 / 產地": "Foxconn / 台灣廠", 
    "前置期 (Lead Time)": "4 - 6 週 (加工難度高)"})
data.append({
    "階層": "L1.2", "模組分類": "光學鏡面", 
    "項目": "曲面人工藍寶石玻璃鏡面", 
    "單價低 (USD)": round(5.20 * current_multiplier, 2), 
    "單價高 (USD)": round(6.20 * current_multiplier, 2), 
    "成本占比": "10%", "供應商 / 產地": "Lens Technology / 湖南", 
    "前置期 (Lead Time)": "3 - 5 週"})
data.append({
    "階層": "L1.3", "模組分類": "電子主板", 
    "項目": "智慧手錶 PCBA (含晶片、GPS)", 
    "單價低 (USD)": round(17.10 * pcba_factor, 2), 
    "單價高 (USD)": round(20.16 * pcba_factor, 2), 
    "成本占比": "32%", "供應商 / 產地": "Compeq / 台灣與越南", 
    "前置期 (Lead Time)": "6 - 8 週 (關鍵交期)"})
data.append({
    "階層": "L1.4", "模組分類": "顯示面板", 
    "項目": "1.4 吋 AMOLED 觸控螢幕總成", 
    "單價低 (USD)": round(10.45 * screen_factor, 2), 
    "單價高 (USD)": round(12.32 * screen_factor, 2), 
    "成本占比": "19%", "供應商 / 產地": "Samsung Display / 韓國", 
    "前置期 (Lead Time)": "4 - 6 週"})
data.append({
    "階層": "L1.5", "模組分類": "結構配件", 
    "項目": "氟橡膠快拆錶帶與扣具", 
    "單價低 (USD)": round(2.38 * scale_factor, 2), 
    "單價高 (USD)": round(2.80 * scale_factor, 2), 
    "成本占比": "4%", "供應商 / 產地": "Jinhualong / 廣東", 
    "前置期 (Lead Time)": "2 - 3 週"})
data.append({
    "階層": "L2.1", "模組分類": "製程工時", 
    "項目": "無塵室組裝與 5ATM 防水檢測", 
    "單價低 (USD)": round(2.38 * scale_factor, 2), 
    "單價高 (USD)": round(3.36 * scale_factor, 2), 
    "成本占比": "9%", "供應商 / 產地": "Pegatron / 越南廠", 
    "前置期 (Lead Time)": "2 週內"})

df = pd.DataFrame(data)
total_low = df["單價低 (USD)"].sum()
total_high = df["單價高 (USD)"].sum()

total_row = {
    "階層": "總計",
    "模組分類": "整機 COGS",
    "項目": "預估整機總成本區間 (產量: " + str(volume) + " pcs)",
    "單價低 (USD)": total_low,
    "單價高 (USD)": total_high,
    "成本占比": "100%",
    "供應商 / 產地": "-",
    "前置期 (Lead Time)": "最長 6 - 8 週"}
df_final = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

st.subheader("📊 目前專案配置：" + material + " | 產量：" + str(volume) + " 支")
st.dataframe(df_final, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="💰 預估整機總成本 (COGS) 區間", value=f"${total_low:.2f} - ${total_high:.2f} USD")

with col2:
    margin_decimal = target_margin / 100
    if margin_decimal >= 1.0:
        margin_decimal = 0.99
    msrp_low = total_low / (1 - margin_decimal)
    msrp_high = total_high / (1 - margin_decimal)
    st.metric(label="🏷️ 建議零售價 (MSRP 區間, 毛利率 " + str(target_margin) + "%)", value=f"${msrp_low:.2f} - ${msrp_high:.2f} USD")

st.markdown("---")

st.subheader("🔍 關鍵零組件成本敏感度分析 (Sensitivity Analysis)")
st.write("評估關鍵零件價格波動對整機總成本的衝擊：")

base_casing_low = round(14.25 * current_multiplier, 2)
base_lens_low = round(5.20 * current_multiplier, 2)
base_pcba_low = round(17.10 * scale_factor, 2)
base_screen_low = round(10.45 * scale_factor, 2)
base_strap_low = round(2.38 * scale_factor, 2)
base_labor_low = round(2.38 * scale_factor, 2)
base_total_low = base_casing_low + base_lens_low + base_pcba_low + base_screen_low + base_strap_low + base_labor_low

diff_amount = round(total_low - base_total_low, 2)
diff_percent = round((diff_amount / base_total_low) * 100, 2) if base_total_low > 0 else 0

df_sensitivity = pd.DataFrame([
    {"關鍵零件項目": "智慧手錶 PCBA (晶片)", "波動幅度": f"{pcba_fluctuation}%", "單機成本變動預估": f"${round(17.10 * scale_factor * (pcba_fluctuation / 100), 2):+.2f} USD"},
    {"關鍵零件項目": "AMOLED 觸控螢幕總成", "波動幅度": f"{screen_fluctuation}%", "單機成本變動預估": f"${round(10.45 * scale_factor * (screen_fluctuation / 100), 2):+.2f} USD"},
    {"關鍵零件項目": "外殼與底蓋 (含CNC)", "波動幅度": f"{casing_fluctuation}%", "單機成本變動預估": f"${round(14.25 * current_multiplier * (casing_fluctuation / 100), 2):+.2f} USD"},
    {"關鍵零件項目": "【總結】整機 COGS 累計變動", "波動幅度": "綜合影響", "單機成本變動預估": f"{diff_amount:+.2f} USD ({diff_percent:+.2f}%)"}])
st.dataframe(df_sensitivity, use_container_width=True)

st.markdown("---")

st.subheader("⚖️ 多材質方案交叉比較 (Matrix Comparison)")

if not selected_materials:
    st.warning("⚠️ 請在左側側邊欄至少勾選一種材質來進行比較。")
    df_compare = pd.DataFrame()
else:
    st.write("在產量固定為 **" + str(volume) + " pcs**、目標毛利率 **" + str(target_margin) + "%** 的條件下，比較所選外殼材質的預估整機 COGS 與建議售價：")
    
    comparison_data = []
    for mat in selected_materials:
        mat_mult = scale_factor * material_multiplier[mat]
        
        part_casing_low = round(14.25 * mat_mult, 2)
        part_lens_low = round(5.20 * mat_mult, 2)
        part_pcba_low = round(17.10 * scale_factor, 2)
        part_screen_low = round(10.45 * scale_factor, 2)
        part_strap_low = round(2.38 * scale_factor, 2)
        part_labor_low = round(2.38 * scale_factor, 2)
        mat_low = part_casing_low + part_lens_low + part_pcba_low + part_screen_low + part_strap_low + part_labor_low
        
        part_casing_high = round(16.80 * mat_mult, 2)
        part_lens_high = round(6.20 * mat_mult, 2)
        part_pcba_high = round(20.16 * scale_factor, 2)
        part_screen_high = round(12.32 * scale_factor, 2)
        part_strap_high = round(2.80 * scale_factor, 2)
        part_labor_high = round(3.36 * scale_factor, 2)
        mat_high = part_casing_high + part_lens_high + part_pcba_high + part_screen_high + part_strap_high + part_labor_high
        
        mat_msrp_low = round(mat_low / (1 - margin_decimal), 2)
        mat_msrp_high = round(mat_high / (1 - margin_decimal), 2)
        
        comparison_data.append({
            "錶殼材質": mat,
            "整機 COGS 低 (USD)": mat_low,
            "整機 COGS 高 (USD)": mat_high,
            "建議零售價低 (USD)": mat_msrp_low,
            "建議零售價高 (USD)": mat_msrp_high})

    df_compare = pd.DataFrame(comparison_data)
    st.dataframe(df_compare, use_container_width=True)

output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    df_final.to_excel(writer, index=False, sheet_name="Apple_Watch_BOM")
    if not df_compare.empty:
        df_compare.to_excel(writer, index=False, sheet_name="Material_Comparison")
    df_sensitivity.to_excel(writer, index=False, sheet_name="Sensitivity_Analysis")
excel_data = output.getvalue()

st.download_button(
    label="📥 點擊下載完整多工作表 Excel 報表 (含 BOM、材質比較與敏感度分析)",
    data=excel_data,
    file_name=f"Apple_Watch_Comprehensive_Report_{volume}pcs.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")