import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Khảo sát Hợp đồng B2B",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #F8F9FB; }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 720px;
    }

    .survey-header {
        background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 100%);
        border-radius: 12px;
        padding: 2rem 2rem 1.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
    }

    .survey-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        color: white;
    }

    .survey-header p {
        font-size: 0.9rem;
        opacity: 0.85;
        margin: 0;
        line-height: 1.6;
    }

    .section-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #2563EB;
        margin-bottom: 0.5rem;
        margin-top: 2rem;
    }

    .section-divider {
        border: none;
        border-top: 1px solid #E2E8F0;
        margin: 1.5rem 0 1rem 0;
    }

    .progress-bar-container {
        background: #E2E8F0;
        border-radius: 99px;
        height: 6px;
        margin-bottom: 2rem;
    }

    .stRadio > label { font-size: 0.9rem; }
    .stCheckbox > label { font-size: 0.9rem; }

    .stButton > button {
        background: #2563EB;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 0.95rem;
        font-weight: 500;
        width: 100%;
        margin-top: 1rem;
        transition: background 0.2s;
    }

    .stButton > button:hover {
        background: #1D4ED8;
    }

    .success-box {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-top: 2rem;
    }

    .disqualified-box {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin-top: 2rem;
    }

    .stSlider > div { padding-top: 0.5rem; }

    div[data-testid="stForm"] {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Google Sheets connection ───────────────────────────────────────────────────
def get_sheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open(st.secrets["sheet_name"]).sheet1
        return sheet
    except Exception as e:
        return None

def save_response(data: dict):
    sheet = get_sheet()
    if sheet is None:
        # Fallback: save locally
        import os, csv
        file_exists = os.path.exists("responses.csv")
        with open("responses.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        return True

    try:
        # Header row if empty
        if sheet.row_count < 1 or not sheet.row_values(1):
            sheet.append_row(list(data.keys()))
        sheet.append_row(list(data.values()))
        return True
    except Exception:
        return False

# ── Session state init ─────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="survey-header">
    <h1>📋 Khảo sát Quản lý Hợp đồng B2B</h1>
    <p>Nghiên cứu học thuật thuộc chương trình Thạc sĩ Trí tuệ Nhân tạo Ứng dụng, Swiss UMEF University.
    Thời gian hoàn thành: 5 đến 7 phút. Thông tin được bảo mật và chỉ dùng cho mục đích nghiên cứu.</p>
</div>
""", unsafe_allow_html=True)

step = st.session_state.step
total_steps = 4

# Progress
if step <= total_steps:
    progress_pct = int((step - 1) / total_steps * 100)
    st.markdown(f"""
    <div class="progress-bar-container">
        <div style="background:#2563EB;height:6px;border-radius:99px;width:{progress_pct}%;transition:width 0.4s;"></div>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Phần {step} / {total_steps}")

# ── STEP 1: Screening ──────────────────────────────────────────────────────────
if step == 1:
    st.markdown('<div class="section-label">Phần 1 — Xác nhận đối tượng</div>', unsafe_allow_html=True)

    with st.form("form_step1"):
        q1 = st.radio(
            "**Câu 1.** Trong công việc hiện tại, bạn có tham gia vào việc soạn thảo, review, hoặc phê duyệt hợp đồng thương mại B2B không?",
            ["Có, thường xuyên", "Có, thỉnh thoảng", "Không"],
            index=None
        )

        q2 = st.radio(
            "**Câu 2.** Giá trị hợp đồng bạn thường làm việc ở mức nào?",
            [
                "Dưới 500 triệu VND",
                "500 triệu đến 5 tỷ VND",
                "Trên 5 tỷ VND",
                "Tôi không làm việc trực tiếp với giá trị hợp đồng"
            ],
            index=None
        )

        submitted = st.form_submit_button("Tiếp theo")

    if submitted:
        if q1 is None or q2 is None:
            st.warning("Vui lòng trả lời đầy đủ cả 2 câu hỏi.")
        elif q1 == "Không" or q2 in ["Dưới 500 triệu VND", "Tôi không làm việc trực tiếp với giá trị hợp đồng"]:
            st.session_state.step = 99  # disqualified
            st.rerun()
        else:
            st.session_state.answers["q1_participation"] = q1
            st.session_state.answers["q2_contract_value"] = q2
            st.session_state.step = 2
            st.rerun()

# ── STEP 2: Pain Points ────────────────────────────────────────────────────────
elif step == 2:
    st.markdown('<div class="section-label">Phần 2 — Thực trạng vấn đề</div>', unsafe_allow_html=True)

    with st.form("form_step2"):
        st.markdown("**Câu 3.** Trong quá trình soạn thảo hoặc review hợp đồng, bạn đã từng gặp tình huống nào sau đây chưa? *(Chọn tất cả đáp án phù hợp)*")
        c1 = st.checkbox("Phải nhập lại thông tin từ báo giá vào hợp đồng bằng tay")
        c2 = st.checkbox("Phát hiện số liệu không khớp giữa các điều khoản (ví dụ: thời hạn thanh toán không khớp với điều kiện bảo lãnh ngân hàng)")
        c3 = st.checkbox("Phát hiện lỗi copy-paste trong bảng thiết bị hoặc thông số kỹ thuật")
        c4 = st.checkbox("Phải sửa hợp đồng sau khi đã gần ký vì lỗi dữ liệu")
        c5 = st.checkbox("Chưa gặp tình huống nào trong danh sách trên")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q4 = st.radio(
            "**Câu 4.** Nếu bạn đã từng phát hiện lỗi trong hợp đồng, hậu quả nghiêm trọng nhất là gì?",
            [
                "Mất thời gian sửa nhưng không ảnh hưởng lớn",
                "Chậm tiến độ ký kết",
                "Phát sinh chi phí hoặc rủi ro tài chính",
                "Ảnh hưởng đến quan hệ với đối tác hoặc khách hàng",
                "Chưa từng gặp lỗi hợp đồng"
            ],
            index=None
        )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q5 = st.slider(
            "**Câu 5.** Mức độ phức tạp của việc kiểm tra tính nhất quán giữa các điều khoản trong hợp đồng B2B?",
            min_value=1, max_value=5, value=3,
            help="1 = Rất đơn giản, 5 = Rất phức tạp"
        )
        st.caption(f"Bạn chọn: {'⭐' * q5}  ({q5}/5)")

        submitted = st.form_submit_button("Tiếp theo")

    if submitted:
        if q4 is None:
            st.warning("Vui lòng trả lời Câu 4.")
        else:
            selected = []
            if c1: selected.append("Nhập lại thông tin thủ công")
            if c2: selected.append("Số liệu không khớp giữa điều khoản")
            if c3: selected.append("Lỗi copy-paste thiết bị")
            if c4: selected.append("Sửa hợp đồng sát thời điểm ký")
            if c5: selected.append("Chưa gặp")
            st.session_state.answers["q3_pain_points"] = ", ".join(selected) if selected else "Không chọn"
            st.session_state.answers["q4_consequence"] = q4
            st.session_state.answers["q5_complexity"] = q5
            st.session_state.step = 3
            st.rerun()

# ── STEP 3: AI Adoption ────────────────────────────────────────────────────────
elif step == 3:
    st.markdown('<div class="section-label">Phần 3 — Đánh giá giải pháp AI</div>', unsafe_allow_html=True)

    with st.form("form_step3"):
        st.info(
            "**Mô tả hệ thống:** Một công cụ AI có thể tự động trích xuất dữ liệu từ báo giá vào hợp đồng, "
            "phát hiện các điều khoản không nhất quán (ví dụ: bảo lãnh ngân hàng không khớp thời hạn thanh toán), "
            "và xuất bản draft để người có thẩm quyền phê duyệt trước khi ký.",
            icon="🤖"
        )

        q6 = st.radio(
            "**Câu 6.** Bạn có sẵn sàng thử nghiệm hệ thống AI như trên không?",
            [
                "Có, sẵn sàng thử ngay",
                "Có, nhưng cần xem thêm kết quả thực tế trước",
                "Chưa chắc",
                "Không, quy trình hiện tại của tôi đã đủ tốt"
            ],
            index=None
        )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q7 = st.radio(
            "**Câu 7.** AI phân tích và đưa ra cảnh báo rủi ro, nhưng quyết định cuối cùng luôn thuộc về người có thẩm quyền. Bạn đánh giá mô hình này như thế nào?",
            [
                "Phù hợp, đây là cách tôi muốn AI được tích hợp vào quy trình hợp đồng",
                "Chấp nhận được, nhưng cần thêm cơ chế kiểm soát",
                "Chưa chắc, phụ thuộc vào độ chính xác thực tế của AI",
                "Không phù hợp với quy trình của tôi"
            ],
            index=None
        )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        st.markdown("**Câu 8.** Rào cản lớn nhất khiến tổ chức bạn chưa sẵn sàng áp dụng AI vào review hợp đồng? *(Chọn tối đa 2)*")
        b1 = st.checkbox("Lo ngại về bảo mật dữ liệu hợp đồng")
        b2 = st.checkbox("Thiếu tin tưởng vào độ chính xác của AI")
        b3 = st.checkbox("Kháng cự từ nội bộ hoặc thói quen làm việc")
        b4 = st.checkbox("Chi phí triển khai")
        b5 = st.checkbox("Không có nhu cầu vì quy trình hiện tại đã ổn")
        b6 = st.checkbox("Khác")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q9 = st.slider(
            "**Câu 9.** Nếu hệ thống được dùng thử miễn phí 3 tháng, khả năng bạn giới thiệu cho đồng nghiệp?",
            min_value=1, max_value=10, value=5,
            help="1 = Chắc chắn không, 10 = Chắc chắn có"
        )
        col1, col2, col3 = st.columns(3)
        with col1: st.caption("1 = Chắc chắn không")
        with col2: st.caption(f"Bạn chọn: **{q9}/10**")
        with col3: st.caption("10 = Chắc chắn có")

        submitted = st.form_submit_button("Tiếp theo")

    if submitted:
        barriers_selected = []
        if b1: barriers_selected.append("Bảo mật dữ liệu")
        if b2: barriers_selected.append("Độ chính xác AI")
        if b3: barriers_selected.append("Kháng cự nội bộ")
        if b4: barriers_selected.append("Chi phí")
        if b5: barriers_selected.append("Không có nhu cầu")
        if b6: barriers_selected.append("Khác")

        if q6 is None or q7 is None:
            st.warning("Vui lòng trả lời Câu 6 và Câu 7.")
        elif len(barriers_selected) > 2:
            st.warning("Câu 8: Vui lòng chọn tối đa 2 rào cản.")
        else:
            st.session_state.answers["q6_adoption_intent"] = q6
            st.session_state.answers["q7_hitl_acceptance"] = q7
            st.session_state.answers["q8_barriers"] = ", ".join(barriers_selected) if barriers_selected else "Không chọn"
            st.session_state.answers["q9_nps"] = q9
            st.session_state.step = 4
            st.rerun()

# ── STEP 4: Demographics ───────────────────────────────────────────────────────
elif step == 4:
    st.markdown('<div class="section-label">Phần 4 — Thông tin bối cảnh (không bắt buộc)</div>', unsafe_allow_html=True)

    with st.form("form_step4"):
        q10 = st.selectbox(
            "**Câu 10.** Vai trò hiện tại của bạn gần nhất với nhóm nào?",
            ["(Bỏ qua)", "Quản lý thương mại / Kinh doanh", "Mua hàng / Đấu thầu",
             "Quản lý dự án", "Pháp lý / Hành chính hợp đồng",
             "Tài chính / Kế toán", "Khác"]
        )

        q11 = st.selectbox(
            "**Câu 11.** Số năm kinh nghiệm làm việc với hợp đồng B2B?",
            ["(Bỏ qua)", "Dưới 2 năm", "2 đến 5 năm", "5 đến 10 năm", "Trên 10 năm"]
        )

        q12 = st.selectbox(
            "**Câu 12.** Ngành bạn đang làm việc?",
            ["(Bỏ qua)", "Thiết bị công nghiệp / Năng lượng", "Xây dựng / EPC / Tổng thầu",
             "Logistics / Vận tải", "Sản xuất / Chế biến", "Khác"]
        )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        email = st.text_input(
            "📧 Nếu muốn nhận tóm tắt kết quả nghiên cứu, để lại email tại đây (không bắt buộc):",
            placeholder="example@company.com"
        )

        submitted = st.form_submit_button("Gửi khảo sát")

    if submitted:
        st.session_state.answers["q10_role"] = q10
        st.session_state.answers["q11_experience"] = q11
        st.session_state.answers["q12_industry"] = q12
        st.session_state.answers["email_optional"] = email if email else ""
        st.session_state.answers["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with st.spinner("Đang lưu phản hồi..."):
            time.sleep(0.8)
            success = save_response(st.session_state.answers)

        if success:
            st.session_state.step = 100
        else:
            st.session_state.step = 101
        st.rerun()

# ── DONE ───────────────────────────────────────────────────────────────────────
elif step == 100:
    st.markdown("""
    <div class="success-box">
        <div style="font-size:2.5rem;margin-bottom:1rem;">✅</div>
        <h3 style="color:#166534;margin-bottom:0.5rem;">Cảm ơn bạn đã tham gia!</h3>
        <p style="color:#15803D;margin:0;">Phản hồi của bạn đã được ghi nhận thành công.<br>
        Kết quả nghiên cứu sẽ được tổng hợp và công bố trong luận văn Thạc sĩ tháng 8/2026.</p>
    </div>
    """, unsafe_allow_html=True)

elif step == 101:
    st.error("Có lỗi xảy ra khi lưu phản hồi. Vui lòng thử lại sau hoặc liên hệ trực tiếp.")
    if st.button("Thử lại"):
        success = save_response(st.session_state.answers)
        if success:
            st.session_state.step = 100
            st.rerun()

# ── DISQUALIFIED ───────────────────────────────────────────────────────────────
elif step == 99:
    st.markdown("""
    <div class="disqualified-box">
        <div style="font-size:2rem;margin-bottom:1rem;">🙏</div>
        <h3 style="color:#9A3412;margin-bottom:0.5rem;">Cảm ơn bạn đã quan tâm!</h3>
        <p style="color:#C2410C;margin:0;">Khảo sát này hướng đến các chuyên gia có kinh nghiệm trực tiếp
        với hợp đồng B2B có giá trị từ 500 triệu VND trở lên.<br><br>
        Rất tiếc bạn không thuộc nhóm đối tượng mục tiêu lần này.</p>
    </div>
    """, unsafe_allow_html=True)
