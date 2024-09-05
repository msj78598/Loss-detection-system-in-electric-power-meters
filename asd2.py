import streamlit as st
import pandas as pd
from io import BytesIO

# مسار ملف الفريم الذي سيتم تحميله
template_path = r'C:\asd2\Meter data frame to be analyzed.xlsx'

# استخدام CSS لجعل العناصر متجاوبة مع الشاشة
st.markdown("""
    <style>
    /* جعل النصوص متجاوبة مع حجم الشاشة */
    h1 {
        font-size: 2.5vw; /* حجم الخط يعتمد على عرض الشاشة */
        text-align: center; /* توسيط العنوان */
    }
    .block-container {
        padding: 2vw; /* الهوامش تتكيف مع حجم الشاشة */
    }
    /* جعل زر التحميل وعناصر الإدخال متجاوبة */
    .stButton, .stFileUploader, .stNumberInput {
        width: 100%; /* جعل الأزرار وعناصر الإدخال تحتل كامل العرض المتاح */
        max-width: 500px; /* تحديد الحد الأقصى للعرض */
        margin: 0 auto; /* توسيط العناصر */
    }
    </style>
    """, unsafe_allow_html=True)

def process_file(file, min_average):
    # قراءة ملف الاكسل
    df = pd.read_excel(file)

    # التحقق من الشروط (إذا كانت إحدى القيم تساوي صفرًا بينما القيمتين الأخريين أو أحدهما أكبر من صفر)
    anomaly = df[
        # الشرط الحالي: أحد التيارات يساوي صفر بينما القيم الأخرى أكبر من صفر
        (((df['A1'] == 0) & ((df['A2'] > 0) | (df['A3'] > 0))) |
        ((df['A2'] == 0) & ((df['A1'] > 0) | (df['A3'] > 0))) |
        ((df['A3'] == 0) & ((df['A1'] > 0) | (df['A2'] > 0)))) |
        
        # الشرط الجديد: أحد الفولتات يساوي صفر مع وجود تيار أكبر من صفر في أي من الفازات
        (((df['V1'] == 0) & ((df['A1'] > 0) | (df['A2'] > 0) | (df['A3'] > 0))) |
        ((df['V2'] == 0) & ((df['A1'] > 0) | (df['A2'] > 0) | (df['A3'] > 0))) |
        ((df['V3'] == 0) & ((df['A1'] > 0) | (df['A2'] > 0) | (df['A3'] > 0))))
    ]

    # حساب متوسط القيم A1, A2, A3
    anomaly['متوسط'] = anomaly[['A1', 'A2', 'A3']].mean(axis=1)

    # تطبيق الفلتر: عرض الحالات التي يكون فيها المتوسط أعلى من الحد الأدنى المحدد
    anomaly = anomaly[anomaly['متوسط'] >= min_average]

    # ترتيب الحالات بناءً على قيمة المتوسط من الأكبر إلى الأصغر
    anomaly = anomaly.sort_values(by='متوسط', ascending=False)

    # حساب عدد الحالات المكتشفة
    num_cases = len(anomaly)

    return anomaly, num_cases

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# عنوان المشروع
st.title("نظام اكتشاف حالات الفاقد في عدادات الطاقة الكهربائية")

# إضافة رسالة واضحة ضمن إطار
st.info("قالب البيانات المعتمد")

# زر تحميل ملف الفريم لتفريغ البيانات
with open(template_path, 'rb') as f:
    st.download_button(
        label="تحميل قالب البيانات",
        data=f,
        file_name="Meter_data_frame_to_be_analyzed.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# تحميل ملف الاكسل المراد تحليله
uploaded_file = st.file_uploader("ارفع ملف الاكسل الخاص بالعدادات")
min_avg = st.number_input("  مقياس تحديد الأولوية  ", value=0.0, step=0.1)

if uploaded_file is not None:
    df, num_cases = process_file(uploaded_file, min_avg)
    st.write(f"عدد الحالات المكتشفة: {num_cases}")
    st.write(df)

    # تحويل البيانات إلى ملف Excel وتنزيله
    excel_data = to_excel(df)
    st.download_button(label="تحميل النتائج كملف Excel", data=excel_data, file_name='anomalies_filtered.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
