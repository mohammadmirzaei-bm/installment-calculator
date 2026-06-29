# -*- coding: utf-8 -*-
"""
ماشین‌حساب پیشرفته فروش اقساطی و تسهیلات بانکی
بر اساس متدهای آنوئیته، فرمول قدیمی بانک مرکزی، قاعده ۷۸، بخشنامه‌های تسویه زودهنگام و وجه التزام
"""

import streamlit as st
import pandas as pd
from datetime import date
import math

# تنظیمات صفحه استریم‌لیت
st.set_page_config(
    page_title="ماشین‌حساب جامع فروش اقساطی",
    layout="wide",
    initial_sidebar_state="expanded"
)

# اعمال استایل‌های CSS بسیار پیشرفته و واکنش‌گرا بدون آسیب زدن به پوسته متحرک سایدبار
st.markdown("""
<style>
    /* تنظیم فونت کلی برنامه */
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Vazirmatn', sans-serif !important;
    }
    
    /* راست‌چین کردن محتوای بلاک اصلی بدون دستکاری ساختار بیرونی */
    .main .block-container {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* راست‌چین کردن محتوای سایدبار بدون خراب کردن انیمیشن باز و بسته شدن */
    [data-testid="stSidebarUserContent"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* راست‌چین کردن المان‌های فرم و اسلایدرها */
    .stSlider, .stSelectbox, .stNumberInput, .stRadio, label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* طراحی کارت‌های مدرن و شیشه‌ای برای متریک‌ها با هماهنگی کامل با تم فعال کاربر */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        text-align: center !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* تضمین نمایش درست عنوان با کنتراست بالا بر اساس متغیرهای تم استریم‌لیت */
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: var(--text-color) !important; /* هماهنگی خودکار با تم تیره یا روشن */
        margin-bottom: 8px !important;
        font-family: 'Vazirmatn', sans-serif !important;
        text-align: center !important;
    }
    
    /* نمایش عدد به صورت خوانا و با رنگ سبز زمردی لوکس مالی */
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricValue"] {
        font-size: 1.7rem !important;
        font-weight: 700 !important;
        color: #10b981 !important; /* رنگ سبز پول */
        direction: ltr !important; /* نمایش صحیح ارقام از چپ به راست */
        display: block !important;
        text-align: center !important;
    }
    
    /* هشدارهای زیبا و فارسی */
    .stAlert {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 12px !important;
    }
    
    /* دکمه‌های شکیل‌تر */
    .stButton>button {
        width: 100%;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# توابع محاسباتی و کمکی ریاضی و مالی
# ==========================================

def g_to_j(g_date):
    """
    محاسبه دقیق سال شمسی بر اساس تاریخ میلادی.
    این تابع به زیبایی مرز دقیق تحویل سال (نوروز) را در سال‌های کبیسه و عادی رصد می‌کند.
    """
    gy, gm, gd = g_date.year, g_date.month, g_date.day
    
    # تعداد روزهای هر ماه میلادی
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    # بررسی سال کبیسه میلادی
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        g_days_in_month[1] = 29
        
    # تعداد روزهای سپری شده از ابتدای سال میلادی
    g_day_no = sum(g_days_in_month[:gm-1]) + gd
    
    # تحویل سال نو (نوروز) به طور تقویمی همواره در روز ۸۰ام میلادی قرار می‌گیرد
    jy = gy - 621
    if g_day_no < 80:
        jy -= 1
    return jy


def add_months(sourcedate, months):
    """
    افزودن دقیق ماه‌ها به یک تاریخ بدون خطای سرریز روزها و اعشار تجمعی
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    
    # تعیین حداکثر تعداد روزهای مجاز ماه جدید برای جلوگیری از خطای روزهای غیرمجاز (مانند ۳۱ فوریه)
    days_in_months = [
        31, 
        29 if ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)) else 28, 
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31
    ]
    day = min(sourcedate.day, days_in_months[month-1])
    return date(year, month, day)


def format_currency(value, unit="تومان"):
    """فرمت‌دهی سه‌رقم سه‌رقم اعداد به همراه واحد پولی انتخابی"""
    try:
        return f"{int(round(value)):,} {unit}"
    except:
        return f"{value} {unit}"


def calculate_installments(principal, rate_pct, months, formula_type="آنوئیته (فرمول نوین)"):
    """
    محاسبه قسط ماهانه و سود کل بر اساس فرمول انتخابی:
    ۱. روش آنوئیته استاندارد
    ۲. روش سنتی بانک مرکزی ایران
    """
    if months <= 0:
        return 0.0, 0.0
    
    if rate_pct == 0:
        installment = principal / months
        total_interest = 0.0
        return installment, total_interest

    if formula_type == "آنوئیته (فرمول نوین)":
        # فرمول آنوئیته استاندارد
        i = rate_pct / 1200.0
        factor = (1 + i) ** months
        installment = (principal * i * factor) / (factor - 1)
        total_repay = installment * months
        total_interest = total_repay - principal
    else:
        # فرمول سنتی بانک مرکزی ایران
        total_interest = (principal * rate_pct * (months + 1)) / 2400.0
        total_repay = principal + total_interest
        installment = total_repay / months
        
    return installment, total_interest


def generate_amortization_schedule(principal, rate_pct, months, installment, formula_type):
    """تولید جدول استهلاک گام‌به‌گام وام برای درک توزیع اصل و سود در هر قسط"""
    schedule = []
    remaining_balance = principal
    monthly_rate = rate_pct / 1200.0
    
    for m in range(1, months + 1):
        if formula_type == "آنوئیته (فرمول نوین)":
            if rate_pct > 0:
                interest_payment = remaining_balance * monthly_rate
                principal_payment = installment - interest_payment
            else:
                interest_payment = 0.0
                principal_payment = installment
        else:
            # در فرمول سنتی سود به صورت مساوی تقسیم بر ماه‌ها فرض می‌شود (ساده‌سازی تدریس)
            total_interest = (principal * rate_pct * (months + 1)) / 2400.0
            interest_payment = total_interest / months
            principal_payment = installment - interest_payment
            
        remaining_balance -= principal_payment
        # جلوگیری از منفی شدن ناچیز در گام آخر به علت رند کردن اعشار
        if remaining_balance < 0 or m == months:
            remaining_balance = 0.0
            
        schedule.append({
            "شماره قسط": m,
            "مبلغ قسط": round(installment),
            "سهم سود قسط": round(interest_payment),
            "سهم اصل قسط": round(principal_payment),
            "باقیمانده اصل": round(remaining_balance)
        })
    return pd.DataFrame(schedule)


def rule78_interest_distribution(total_interest, months, start_date):
    """تخصیص سود کل R به تفکیک سال‌های شمسی بر اساس قاعده ۷۸"""
    if months <= 0 or total_interest <= 0:
        return pd.DataFrame()
    
    total_weight = months * (months + 1) / 2
    year_buckets = {}
    
    # تخمین و توزیع دقیق اقساط در ماه‌های آتی بدون انحراف زمانی
    for i in range(1, months + 1):
        # محاسبه دقیق تاریخ سررسید هر قسط با افزودن ماه واقعی
        inst_date = add_months(start_date, i - 1)
        j_year = g_to_j(inst_date)
        
        # وزن قسط طبق قاعده ۷۸
        weight = (months - i + 1)
        if j_year not in year_buckets:
            year_buckets[j_year] = {"count": 0, "weight_sum": 0.0}
        year_buckets[j_year]["count"] += 1
        year_buckets[j_year]["weight_sum"] += weight
        
    rows = []
    for y in sorted(year_buckets.keys()):
        w_sum = year_buckets[y]["weight_sum"]
        allocated_interest = total_interest * (w_sum / total_weight)
        rows.append({
            "سال شمسی": y,
            "تعداد اقساط سررسید شده": year_buckets[y]["count"],
            "مجموع وزن اقساط": int(w_sum),
            "سود تخصیص‌یافته": round(allocated_interest)
        })
    return pd.DataFrame(rows)


# ==========================================
# طراحی سایدبار (Sidebar) - هاب ورودی اطلاعات
# ==========================================

st.sidebar.header("🛠️ تنظیمات پایه قرارداد")

# واحد پول پیش‌فرض و ثابت روی تومان قرار دارد
currency_unit = "تومان"

# انتخاب فرمول محاسباتی
calc_method = st.sidebar.selectbox(
    "روش محاسبه سود و اقساط:",
    ["آنوئیته (فرمول نوین)", "فرمول سنتی بانک مرکزی ایران"],
    help="فرمول آنوئیته مبتنی بر ارزش زمانی پول است در حالی که فرمول سنتی به صورت خطی سود را تقسیم می‌کند."
)

st.sidebar.markdown("---")

# دریافت پارامترهای عددی بدون اسلایدر محدودکننده
raw_price = st.sidebar.number_input(
    f"قیمت نقدی کالا ({currency_unit})",
    min_value=0,
    value=10000000,
    step=100000,
    format="%d"
)

# تبدیل اسلایدر به باکس عددی پیش‌پرداخت بر اساس درخواست شما
down_pct = st.sidebar.number_input(
    "درصد پیش‌پرداخت مشتری (٪)",
    min_value=0,
    max_value=100,
    value=20,
    step=1,
    format="%d"
)

months_input = st.sidebar.number_input(
    "مدت زمان بازپرداخت (ماه)",
    min_value=1,
    max_value=120,
    value=12,
    step=1
)

annual_rate_input = st.sidebar.number_input(
    "نرخ سود سالانه تسهیلات (٪)",
    min_value=0.0,
    max_value=100.0,
    value=23.0,
    step=0.5
)

# محاسبات میانی و ذخیره‌سازی در متغیرهای سراسری برای سادگی رندر تب‌ها
down_payment_val = (raw_price * down_pct) / 100.0
loan_principal = max(raw_price - down_payment_val, 0)

monthly_payment, total_interest_val = calculate_installments(
    loan_principal, annual_rate_input, int(months_input), calc_method
)
total_repayment_val = loan_principal + total_interest_val


# ==========================================
# طراحی بدنه اصلی نرم‌افزار (تب‌ها)
# ==========================================

st.title("🎯 سامانه شبیه‌ساز و محاسباتی فروش اقساطی")
st.write("این ابزار بر اساس استانداردهای آکادمیک و قوانین جاری بانکداری اسلامی ایران طراحی شده است.")

tabs = st.tabs([
    "📊 خلاصه تسهیلات و جدول استهلاک",
    "📅 تخصیص سود سالانه (قاعده ۷۸)",
    "💸 تسویه زودهنگام (تخفیف متمم)",
    "⚠️ محاسبه جریمه دیرکرد (وجه التزام)"
])

# ------------------------------------------
# تب اول: خلاصه تسهیلات و جدول استهلاک
# ------------------------------------------
with tabs[0]:
    st.subheader("📋 جزئیات مالی محاسبات تسهیلات")
    
    # نمایش خلاصه در کارت‌های شیک و منظم
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("مبلغ پیش‌پرداخت", format_currency(down_payment_val, currency_unit))
    with c2:
        st.metric("اصل تسهیلات (مبلغ وام)", format_currency(loan_principal, currency_unit))
    with c3:
        st.metric("مبلغ هر قسط ماهانه", format_currency(monthly_payment, currency_unit))
        
    c4, c5 = st.columns(2)
    with c4:
        st.metric("کل سود تسهیلات", format_currency(total_interest_val, currency_unit))
    with c5:
        st.metric("مجموع کل بازپرداخت", format_currency(total_repayment_val, currency_unit))
        
    st.markdown("---")
    
    st.subheader("📈 جدول و نمودار استهلاک قسط")
    
    if loan_principal > 0 and months_input > 0:
        # ایجاد جدول استهلاک
        df_amort = generate_amortization_schedule(
            loan_principal, annual_rate_input, int(months_input), monthly_payment, calc_method
        )
        
        # نمایش چارت تعاملی توزیع اصل و سود در طول دوره قسط
        st.write("💡 **نمودار سهم اصل و سود در پرداختی‌های ماهانه:**")
        chart_data = df_amort[["شماره قسط", "سهم سود قسط", "سهم اصل قسط"]].set_index("شماره قسط")
        st.area_chart(chart_data)
        
        # قالب‌بندی ریال/تومان جدول جهت نمایش به کاربر
        df_display = df_amort.copy()
        cols_to_format = ["مبلغ قسط", "سهم سود قسط", "سهم اصل قسط", "باقیمانده اصل"]
        for col in cols_to_format:
            df_display[col] = df_display[col].apply(lambda x: format_currency(x, currency_unit))
            
        st.write("💡 **جدول پرداخت جزئیات اقساط:**")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.warning("لطفاً مقادیر صحیحی برای اصل مبلغ و تعداد اقساط در سایدبار وارد کنید.")

# ------------------------------------------
# تب دوم: تخصیص سود سالانه (قاعده ۷۸)
# ------------------------------------------
with tabs[1]:
    st.subheader("📅 تقسیم و تخصیص سود بر اساس سال‌های مالی (قاعده ۷۸)")
    st.write(
        "قاعده ۷۸ روشی پذیرفته شده برای تخصیص سود در حسابداری است که فرض می‌کند "
        "سودهای اولیه قرارداد وزن و مبالغ بزرگتری نسبت به ماه‌های آخر بازپرداخت دارند."
    )
    
    contract_start = st.date_input("تاریخ شروع و امضای قرارداد:", value=date.today())
    
    if loan_principal > 0 and total_interest_val > 0:
        df_78 = rule78_interest_distribution(total_interest_val, int(months_input), contract_start)
        
        if not df_78.empty:
            df_78_display = df_78.copy()
            df_78_display["سود تخصیص‌یافته"] = df_78_display["سود تخصیص‌یافته"].apply(lambda x: format_currency(x, currency_unit))
            
            st.write("📊 **جدول تراز توزیع سود سالانه:**")
            st.dataframe(df_78_display, use_container_width=True, hide_index=True)
            
            # ارائه توضیحات آکادمیک
            st.info(
                f"💡 **تفسیر مالی:** بر مبنای جدول بالا، کل سود شما به ارزش "
                f"**{format_currency(total_interest_val, currency_unit)}** به نسبت اوزان هر سال مالی تسهیم شد. "
                "این توزیع به واحد مالی/حسابداری شرکت کمک می‌کند تا درآمد حاصل از تسهیلات را در ترازنامه‌های سالانه خود به درستی شناسایی کند."
            )
        else:
            st.error("خطا در محاسبه توزیع قاعده ۷۸.")
    else:
        st.info("سود محاسبه شده در سایدبار صفر است، لذا توزیعی صورت نمی‌گیرد.")

# ------------------------------------------
# تب سوم: تسویه زودهنگام (تخفیف متمم)
# ------------------------------------------
with tabs[2]:
    st.subheader("💸 محاسبه مانده بدهی جهت تسویه پیش از موعد")
    st.write(
        "هرگاه تسهیلات‌گیرنده تصمیم بگیرد کل بدهی خود را یک‌جا قبل از سررسید نهایی تسویه کند، "
        "مستحق دریافت تخفیف سود سال‌های آتی خواهد بود."
    )
    
    col_early1, col_early2 = st.columns(2)
    with col_early1:
        paid_installments = st.number_input(
            "تعداد اقساط پرداخت شده تا کنون:",
            min_value=0,
            max_value=int(months_input) - 1,
            value=0,
            step=1
        )
    with col_early2:
        rebate_method = st.selectbox(
            "روش محاسبه تخفیف تسویه زودهنگام:",
            ["آیین‌نامه بانک مرکزی ایران (تخفیف ۹۰٪ سود آتی)", "فرمول ریاضی محض قاعده ۷۸ (تخفیف کامل)"]
        )
        
    if loan_principal > 0 and total_interest_val > 0:
        total_term = int(months_input)
        remaining_term = total_term - paid_installments
        
        # محاسبه کل سود اقساط باقی‌مانده بر اساس قاعده ۷۸
        # سود کل اقساط آتی طبق قاعده ۷۸: R_remaining = R_total * [L(L+1) / n(n+1)]
        future_interest = total_interest_val * (remaining_term * (remaining_term + 1)) / (total_term * (total_term + 1))
        
        if rebate_method == "آیین‌نامه بانک مرکزی ایران (تخفیف ۹۰٪ سود آتی)":
            rebate_val = future_interest * 0.90
        else:
            rebate_val = future_interest
            
        # مبلغ تسویه نهایی = (تعداد اقساط باقی‌مانده * مبلغ هر قسط) - میزان تخفیف
        payoff_amount_val = (monthly_payment * remaining_term) - rebate_val
        
        st.markdown("---")
        st.write("### 💎 گزارش مالی تسویه زودهنگام")
        
        e_col1, e_col2, e_col3 = st.columns(3)
        with e_col1:
            st.metric("تعداد اقساط باقیمانده", f"{remaining_term} قسط")
        with e_col2:
            st.metric("میزان تخفیف سود (کاهنده)", format_currency(rebate_val, currency_unit))
        with e_col3:
            st.metric("مبلغ خالص جهت تسویه نهایی", format_currency(payoff_amount_val, currency_unit))
            
        st.warning(
            f"📌 **راهنمای پرداخت:** برای تسویه کامل این قرارداد، بجای پرداخت کل مبالغ سررسید نشده به ارزش "
            f"**{format_currency(monthly_payment * remaining_term, currency_unit)}**، شما فقط مبلغ "
            f"**{format_currency(payoff_amount_val, currency_unit)}** را واریز خواهید کرد."
        )
    else:
        st.info("ابتدا ورودی‌های معتبر در سایدبار وارد کنید.")

# ------------------------------------------
# تب چهارم: محاسبه جریمه دیرکرد (وجه التزام)
# ------------------------------------------
with tabs[3]:
    st.subheader("⚠️ محاسبه وجه التزام تأخیر تأدیه (جریمه دیرکرد)")
    st.write(
        "طبق استانداردهای بانکداری بدون ربا در ایران، جریمه دیرکرد یا وجه التزام به منظور التزام "
        "تسهیلات‌گیرنده به تعهدات خود و بر اساس مانده بدهی معوق و تعداد روزهای واقعی تأخیر محاسبه می‌شود."
    )
    
    col_pen1, col_pen2 = st.columns(2)
    with col_pen1:
        custom_penalty_rate = st.number_input(
            "نرخ جریمه دیرکرد / وجه التزام اضافی (٪)",
            min_value=0.0,
            max_value=20.0,
            value=6.0,
            step=1.0,
            help="در ایران وجه التزام معمولاً برابر است با (نرخ سود تسهیلات + نرخ جریمه دیرکرد که مصوب بانک مرکزی معمولاً ۶ درصد است)."
        )
    with col_pen2:
        delay_days = st.number_input("تعداد کل روزهای تاخیر واقعی قسط معوق:", min_value=1, value=30, step=1)
        overdue_amt = st.number_input(f"مبلغ بدهی معوق شده ({currency_unit}):", min_value=0.0, value=monthly_payment, step=1000.0)

    # اجرای فرمول محاسبات بر اساس فرمول رسمی وجه التزام
    effective_rate = annual_rate_input + custom_penalty_rate
    
    if loan_principal > 0:
        # فرمول رسمی وجه التزام: (مبلغ معوق * نرخ موثر * تعداد روزهای تاخیر) / 36500
        calculated_penalty = (overdue_amt * effective_rate * delay_days) / 36500.0
        
        st.markdown("---")
        st.write("### 🚨 نتیجه محاسبه خسارت")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric("نرخ موثر جریمه (سود + جریمه)", f"{effective_rate} ٪")
        with res_col2:
            st.metric("مبلغ وجه التزام قابل پرداخت", format_currency(calculated_penalty, currency_unit))
            
        st.info(
            "📝 **نکته قانونی:** مبالغ دریافتی بابت وجه التزام در سیستم بانکی ایران طبق موازین فقهی شرعی برای جلوگیری از ربا، "
            "بر اساس شروط ضمن عقد دریافت شده و بخش عمده آن وجه تنبیهی به حساب می‌آآید."
        )
    else:
        st.info("ابتدا اطلاعات تسهیلات را در سایدبار تکمیل کنید.")