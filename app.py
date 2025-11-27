import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- إعداد الصفحة ---
st.set_page_config(page_title="نظام التدقيق الآلي", layout="wide")

# --- التنسيق البصري ---
st.markdown("""
<style>
    .reportview-container {margin-top: -2em;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# --- العنوان ---
st.title("🏗️ نظام التدقيق الآلي - رخص البناء")
st.markdown("### إدارة رخص البناء - أمانة منطقة الرياض")
st.info("قم برفع مخطط المشروع وسيقوم النظام بمطابقته مع الدليل الموحد وإظهار المخالفات.")

# --- إعداد الذكاء الاصطناعي ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("مفتاح API غير موجود في إعدادات Secrets.")
    st.stop()

# --- دالة التحليل ---
def analyze_pdf(uploaded_file):
    # حفظ الملف مؤقتاً لرفعه
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # 1. رفع الملف إلى Gemini
        pdf_file = genai.upload_file(tmp_file_path, mime_type="application/pdf")
        
        # 2. تجهيز الموديل
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # 3. التعليمات الصارمة (التي كتبناها سابقاً)
        prompt = """
        بصفتك مهندس تدقيق في أمانة الرياض، قم بتحليل ملف المخطط المرفق بدقة متناهية.
        لديك معرفة مسبقة بـ "الدليل الموحد لاشتراطات البناء".
        
        المطلوب:
        1. استخرج بيانات المشروع (نوع المبنى، المساحة، الشوارع).
        2. قارن الأرقام الموجودة في جدول المخطط مع اشتراطات كود الرياض (الارتدادات، النسب، المواقف).
        3. أنشئ جدولاً للمطابقة: [البند] | [القيمة في المخطط] | [المطلوب في الدليل] | [الحالة: مطابق/مخالف].
        4. اذكر رقم الصفحة في الدليل الموحد كمرجع لكل بند.
        """
        
        # 4. إرسال الطلب
        response = model.generate_content([prompt, pdf_file])
        return response.text

    except Exception as e:
        return f"حدث خطأ أثناء التحليل: {str(e)}"
    finally:
        # تنظيف الملفات المؤقتة
        os.remove(tmp_file_path)

# --- واجهة الرفع ---
uploaded_file = st.file_uploader("ارفع ملف المخطط (PDF)", type=['pdf'])

if uploaded_file is not None:
    if st.button("🚀 ابدأ الفحص الآلي"):
        with st.spinner('جاري قراءة المخطط ومطابقته مع الكود... (قد يستغرق الأمر دقيقة)'):
            result = analyze_pdf(uploaded_file)
            st.success("تم الانتهاء من التدقيق!")
            st.markdown("---")
            st.markdown(result)

