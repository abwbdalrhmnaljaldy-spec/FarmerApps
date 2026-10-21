import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# إعداد الصفحة لتناسب شاشة الهاتف واللغة العربية
st.set_page_config(page_title="صديق المزارع", page_icon="🌾", layout="centered")
st.markdown("""
<style>
    * { direction: rtl; font-family: 'Arial', sans-serif; }
    .stTextInput>div>div>input { text-align: right; }
    .stNumberInput>div>div>input { text-align: right; }
    .stSelectbox>div>div>div { text-align: right; }
</style>
""", unsafe_allow_html=True)

# ----------------- إعداد قاعدة البيانات -----------------
conn = sqlite3.connect("farmer_friend.db", check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
c.execute('''CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, item TEXT, amount REAL, z10 REAL, z5 REAL, z25 REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, water REAL, fert REAL, pest REAL, workers REAL, other REAL, other_desc TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS custom_income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT, date TEXT, item TEXT, amount REAL, z10 REAL, z5 REAL, z25 REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS custom_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT, date TEXT, water REAL, fert REAL, pest REAL, workers REAL, other REAL, other_desc TEXT)''')
conn.commit()

# ----------------- الواجهة الرئيسية -----------------
st.title("🌾 برنامج صديق المزارع")
st.write("نظام إدارة حسابات المزرعة - مخصص للهواتف")

# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs(["المدخول العام", "المصروفات العامة", "الحقول المخصصة"])

# ================= الباب الأول: المدخول العام =================
with tab1:
    st.header("إضافة مدخول جديد")
    with st.form("income_form"):
        item = st.text_input("البيان (مثال: بيع طماطم)")
        amount = st.number_input("المبلغ", min_value=0.0, step=1000.0)
        irrig_type = st.selectbox("مصدر السقي", ["غيث (10%)", "مكينة (5%)", "نقل (2.5%)"])
        submit_income = st.form_submit_button("إضافة المدخول وحساب الزكاة", use_container_width=True)

        if submit_income:
            if item and amount > 0:
                z10 = amount * 0.10 if "غيث" in irrig_type else 0.0
                z5 = amount * 0.05 if "مكينة" in irrig_type else 0.0
                z25 = amount * 0.025 if "نقل" in irrig_type else 0.0
                date = datetime.now().strftime("%Y/%m/%d")
                
                c.execute("INSERT INTO income (date, item, amount, z10, z5, z25) VALUES (?, ?, ?, ?, ?, ?)",
                          (date, item, amount, z10, z5, z25))
                conn.commit()
                st.success("تم الحفظ بنجاح!")
            else:
                st.error("تأكد من إدخال البيان والمبلغ.")

    st.divider()
    st.subheader("سجل المدخول العام")
    df_inc = pd.read_sql_query("SELECT date as التاريخ, item as البيان, amount as المدخول, z10 as غيث, z5 as مكينة, z25 as نقل FROM income", conn)
    if not df_inc.empty:
        st.dataframe(df_inc, use_container_width=True, hide_index=True)
        st.info(f"💰 إجمالي المدخول: {df_inc['المدخول'].sum():,.0f}")
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الغيث", f"{df_inc['غيث'].sum():,.0f}")
        col2.metric("إجمالي الماكينة", f"{df_inc['مكينة'].sum():,.0f}")
        col3.metric("إجمالي النقل", f"{df_inc['نقل'].sum():,.0f}")
    else:
        st.warning("لا توجد بيانات مسجلة بعد.")

# ================= الباب الثاني: المصروفات العامة =================
with tab2:
    st.header("تسجيل المصروفات")
    with st.form("expenses_form"):
        col1, col2 = st.columns(2)
        with col1:
            water = st.number_input("المياه", min_value=0.0, step=1000.0)
            pest = st.number_input("المبيدات", min_value=0.0, step=1000.0)
            other = st.number_input("مصاريف أخرى", min_value=0.0, step=1000.0)
        with col2:
            fert = st.number_input("الأسمدة", min_value=0.0, step=1000.0)
            workers = st.number_input("العمال", min_value=0.0, step=1000.0)
            other_desc = st.text_input("تفاصيل الأخرى (مثال: بترول)")
            
        submit_exp = st.form_submit_button("حفظ المصروفات", use_container_width=True)

        if submit_exp:
            if sum([water, fert, pest, workers, other]) > 0:
                date = datetime.now().strftime("%Y/%m/%d")
                c.execute("INSERT INTO expenses (date, water, fert, pest, workers, other, other_desc) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (date, water, fert, pest, workers, other, other_desc))
                conn.commit()
                st.success("تم حفظ المصروفات بنجاح!")
            else:
                st.error("أدخل مبلغاً في خانة واحدة على الأقل.")

    st.divider()
    st.subheader("سجل المصروفات العامة")
    df_exp = pd.read_sql_query("SELECT date as التاريخ, water as المياه, fert as الأسمدة, pest as المبيدات, workers as العمال, other as أخرى, other_desc as تفاصيل FROM expenses", conn)
    if not df_exp.empty:
        st.dataframe(df_exp, use_container_width=True, hide_index=True)
        total_exp = df_exp[['المياه', 'الأسمدة', 'المبيدات', 'العمال', 'أخرى']].sum().sum()
        st.error(f"💸 الإجمالي الكلي للمصروفات: {total_exp:,.0f}")
    else:
        st.warning("لا توجد مصروفات مسجلة بعد.")

# ================= الباب الثالث: الحقول المخصصة =================
with tab3:
    st.header("إدارة الحقول المخصصة")
    sub_tab1, sub_tab2 = st.tabs(["مدخول حقل", "مصروف حقل"])
    
    with sub_tab1:
        with st.form("custom_inc_form"):
            c_field = st.text_input("اسم الحقل (مثال: حقل المانجو)")
            c_item = st.text_input("البيان")
            c_amount = st.number_input("المبلغ", min_value=0.0, step=1000.0)
            c_irrig = st.selectbox("مصدر السقي للحقل", ["غيث (10%)", "مكينة (5%)", "نقل (2.5%)"])
            submit_c_inc = st.form_submit_button("إضافة مدخول الحقل", use_container_width=True)
            
            if submit_c_inc:
                if c_field and c_item and c_amount > 0:
                    z10 = c_amount * 0.10 if "غيث" in c_irrig else 0.0
                    z5 = c_amount * 0.05 if "مكينة" in c_irrig else 0.0
                    z25 = c_amount * 0.025 if "نقل" in c_irrig else 0.0
                    date = datetime.now().strftime("%Y/%m/%d")
                    c.execute("INSERT INTO custom_income (field_name, date, item, amount, z10, z5, z25) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (c_field, date, c_item, c_amount, z10, z5, z25))
                    conn.commit()
                    st.success("تم حفظ مدخول الحقل بنجاح!")
                else:
                    st.error("الرجاء تعبئة اسم الحقل والبيان والمبلغ.")
                    
        df_c_inc = pd.read_sql_query("SELECT date as التاريخ, field_name as الحقل, item as البيان, amount as المدخول FROM custom_income", conn)
        if not df_c_inc.empty:
            st.dataframe(df_c_inc, use_container_width=True, hide_index=True)

    with sub_tab2:
        with st.form("custom_exp_form"):
            ce_field = st.text_input("اسم الحقل (مثال: حقل المانجو) ")
            col1, col2 = st.columns(2)
            with col1:
                ce_water = st.number_input("المياه ", min_value=0.0, step=1000.0)
                ce_pest = st.number_input("المبيدات ", min_value=0.0, step=1000.0)
                ce_other = st.number_input("مصاريف أخرى ", min_value=0.0, step=1000.0)
            with col2:
                ce_fert = st.number_input("الأسمدة ", min_value=0.0, step=1000.0)
                ce_workers = st.number_input("العمال ", min_value=0.0, step=1000.0)
                ce_desc = st.text_input("التفاصيل")
            submit_c_exp = st.form_submit_button("حفظ مصروف الحقل", use_container_width=True)
            
            if submit_c_exp:
                if ce_field and sum([ce_water, ce_fert, ce_pest, ce_workers, ce_other]) > 0:
                    date = datetime.now().strftime("%Y/%m/%d")
                    c.execute("INSERT INTO custom_expenses (field_name, date, water, fert, pest, workers, other, other_desc) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (ce_field, date, ce_water, ce_fert, ce_pest, ce_workers, ce_other, ce_desc))
                    conn.commit()
                    st.success("تم حفظ مصروف الحقل!")
                else:
                    st.error("تأكد من إدخال اسم الحقل ومبلغ واحد على الأقل.")
                    
        df_c_exp = pd.read_sql_query("SELECT date as التاريخ, field_name as الحقل, water as مياه, fert as أسمدة, pest as مبيدات, workers as عمال, other as أخرى FROM custom_expenses", conn)
        if not df_c_exp.empty:
            st.dataframe(df_c_exp, use_container_width=True, hide_index=True)
