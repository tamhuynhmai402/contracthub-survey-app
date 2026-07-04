import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import time

st.set_page_config(
    page_title="Khảo sát Ứng dụng AI Hỗ trợ Soạn thảo Hợp đồng B2B",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F8F9FB; }
    .block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 720px; }
    .survey-header {
        background: linear-gradient(135deg, #1B3A6B 0%, #2563EB 100%);
        border-radius: 12px; padding: 2rem 2rem 1.5rem 2rem;
        margin-bottom: 2rem; color: white;
    }
    .survey-header h1 { font-size: 1.5rem; font-weight: 600; margin: 0 0 0.5rem 0; color: white; }
    .survey-header p { font-size: 0.9rem; opacity: 0.85; margin: 0; line-height: 1.6; }
    .section-label {
        font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
        text-transform: uppercase; color: #2563EB; margin-bottom: 0.5rem; margin-top: 2rem;
    }
    .section-divider { border: none; border-top: 1px solid #E2E8F0; margin: 1.5rem 0 1rem 0; }
    .progress-bar-container { background: #E2E8F0; border-radius: 99px; height: 6px; margin-bottom: 2rem; }
    .stButton > button {
        background: #2563EB; color: white; border: none; border-radius: 8px;
        padding: 0.6rem 2rem; font-size: 0.95rem; font-weight: 500;
        width: 100%; margin-top: 1rem;
    }
    .stButton > button:hover { background: #1D4ED8; }
    .success-box {
        background: #F0FDF4; border: 1px solid #86EFAC; border-radius: 10px;
        padding: 2rem; text-align: center; margin-top: 2rem;
    }
    .disqualified-box {
        background: #FFF7ED; border: 1px solid #FED7AA; border-radius: 10px;
        padding: 2rem; text-align: center; margin-top: 2rem;
    }
    div[data-testid="stForm"] {
        background: white; border-radius: 12px; padding: 1.5rem;
        border: 1px solid #E2E8F0; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def get_sheet():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open(st.secrets["sheet_name"]).sheet1
    except Exception:
        return None

def save_response(data: dict):
    sheet = get_sheet()
    if sheet is None:
        import os, csv
        file_exists = os.path.exists("responses.csv")
        with open("responses.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        return True
    try:
        if not sheet.row_values(1):
            sheet.append_row(list(data.keys()))
        sheet.append_row(list(data.values()))
        return True
    except Exception:
        return False

if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

st.markdown("""
<div class="survey-header">
    <h1>📋 Khảo sát Ứng dụng AI Hỗ trợ Soạn thảo và Kiểm tra Hợp đồng B2B</h1>
    <p>Nghiên cứu học thuật thuộc chương trình Thạc sĩ Trí tuệ Nhân tạo Ứng dụng, Swiss UMEF University of Applied Sciences Institute (Geneva).<br>
    Thời gian hoàn thành: 5 đến 7 phút. Thông tin được bảo mật và chỉ dùng cho mục đích nghiên cứu.</p>
</div>
""", unsafe_allow_html=True)

step = st.session_state.step
total_steps = 4

if step <= total_steps:
    progress_pct = int((step - 1) / total_steps * 100)
    st.markdown(f"""
    <div class="progress-bar-container">
        <div style="background:#2563EB;height:6px;border-radius:99px;width:{progress_pct}%;transition:width 0.4s;"></div>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Phần {step} / {total_steps}")

LIKERT = ["Hoàn toàn không đồng ý", "Không đồng ý", "Trung lập", "Đồng ý", "Hoàn toàn đồng ý"]

# ── STEP 1: Screening ──────────────────────────────────────────────────────────
if step == 1:
    st.markdown('<div class="section-label">Phần 1 — Xác nhận đối tượng</div>', unsafe_allow_html=True)
    with st.form("form_step1"):
        q1 = st.radio(
            "**Câu 1.** Trong công việc hiện tại, bạn có tham gia vào việc soạn thảo, review, hoặc phê duyệt hợp đồng thương mại B2B không?",
            ["Có, thường xuyên", "Có, thỉnh thoảng", "Không"], index=None
        )
        q2 = st.radio(
            "**Câu 2.** Giá trị hợp đồng bạn làm việc phổ biến nhất ở mức nào? *(Nếu làm nhiều mức, chọn mức xử lý thường xuyên nhất)*",
            ["Dưới 500 triệu VND", "500 triệu đến 5 tỷ VND", "Trên 5 tỷ VND",
             "Tôi không làm việc trực tiếp với giá trị hợp đồng"], index=None
        )
        submitted = st.form_submit_button("Tiếp theo")

    if submitted:
        if q1 is None or q2 is None:
            st.warning("Vui lòng trả lời đầy đủ cả 2 câu hỏi.")
        elif q1 == "Không" or q2 in ["Dưới 500 triệu VND", "Tôi không làm việc trực tiếp với giá trị hợp đồng"]:
            st.session_state.step = 99
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
        c1 = st.checkbox("Phải nhập lại thông tin từ báo giá / chào thầu vào hợp đồng bằng tay")
        c2 = st.checkbox("Phát hiện số liệu không khớp giữa các điều khoản (ví dụ: thời hạn thanh toán không khớp với điều kiện bảo lãnh ngân hàng)")
        c3 = st.checkbox("Phát hiện lỗi copy-paste trong bảng thiết bị hoặc thông số kỹ thuật")
        c4 = st.checkbox("Phải sửa hợp đồng sau khi đã gần ký vì lỗi dữ liệu")
        c5 = st.checkbox("Trải qua quá trình đàm phán / chỉnh sửa kéo dài qua nhiều phiên bản, các điều khoản không còn nhất quán hoặc mâu thuẫn với nhau")
        c6 = st.checkbox("Phải đối chiếu nhiều tài liệu (báo giá, PO, email, phụ lục...) để xác minh thông tin")
        c7 = st.checkbox("Chưa gặp tình huống nào trong danh sách trên")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        st.markdown("**Câu 4.** Nếu bạn đã từng phát hiện lỗi trong hợp đồng, những hậu quả nào bạn đã từng gặp phải? *(Chọn tất cả đáp án phù hợp)*")
        d1 = st.checkbox("Mất thời gian sửa nhưng không ảnh hưởng lớn")
        d2 = st.checkbox("Chậm tiến độ ký kết")
        d3 = st.checkbox("Phát sinh chi phí hoặc rủi ro tài chính")
        d4 = st.checkbox("Ảnh hưởng đến quan hệ với đối tác hoặc khách hàng")
        d5 = st.checkbox("Bị từ chối nhận hàng hoặc bị phạt vi phạm hợp đồng")
        d6 = st.checkbox("Bị khiển trách hoặc ảnh hưởng đến đánh giá hiệu suất (performance) từ cấp trên")
        d7 = st.checkbox("Chưa từng gặp lỗi hợp đồng")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q5 = st.slider(
            "**Câu 5.** Mức độ phức tạp của việc kiểm tra tính nhất quán giữa các điều khoản trong hợp đồng B2B?",
            min_value=1, max_value=5, value=3,
            help="1 = Rất đơn giản, 5 = Rất phức tạp"
        )
        st.caption(f"Bạn chọn: {'⭐' * q5}  ({q5}/5)")

        submitted = st.form_submit_button("Tiếp theo")

    if submitted:
        q3_sel = []
        if c1: q3_sel.append("Nhập lại thông tin thủ công")
        if c2: q3_sel.append("Số liệu không khớp giữa điều khoản")
        if c3: q3_sel.append("Lỗi copy-paste thiết bị")
        if c4: q3_sel.append("Sửa hợp đồng sát thời điểm ký")
        if c5: q3_sel.append("Điều khoản mâu thuẫn qua nhiều phiên bản")
        if c6: q3_sel.append("Đối chiếu nhiều tài liệu để xác minh")
        if c7: q3_sel.append("Chưa gặp")

        q4_sel = []
        if d1: q4_sel.append("Mất thời gian sửa")
        if d2: q4_sel.append("Chậm tiến độ ký kết")
        if d3: q4_sel.append("Rủi ro tài chính")
        if d4: q4_sel.append("Ảnh hưởng quan hệ đối tác")
        if d5: q4_sel.append("Bị từ chối nhận hàng hoặc bị phạt")
        if d6: q4_sel.append("Ảnh hưởng đánh giá hiệu suất")
        if d7: q4_sel.append("Chưa từng gặp lỗi")

        st.session_state.answers["q3_pain_points"] = ", ".join(q3_sel) if q3_sel else "Không chọn"
        st.session_state.answers["q4_consequences"] = ", ".join(q4_sel) if q4_sel else "Không chọn"
        st.session_state.answers["q5_complexity"] = q5
        st.session_state.step = 3
        st.rerun()

# ── STEP 3: AI Adoption + TAM ─────────────────────────────────────────────────
elif step == 3:
    st.markdown('<div class="section-label">Phần 3 — Đánh giá giải pháp AI</div>', unsafe_allow_html=True)
    with st.form("form_step3"):
        st.info(
            "**Mô tả hệ thống:** Một công cụ AI có thể tự động trích xuất dữ liệu từ báo giá vào hợp đồng, "
            "phát hiện các điều khoản không nhất quán (ví dụ: bảo lãnh ngân hàng không khớp thời hạn thanh toán), "
            "và xuất draft để người có thẩm quyền phê duyệt trước khi ký.",
            icon="🤖"
        )

        q6 = st.radio(
            "**Câu 6.** Bạn có sẵn sàng thử nghiệm hệ thống AI như trên không?",
            ["Rất sẵn sàng", "Sẵn sàng", "Phân vân", "Không sẵn sàng"], index=None
        )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q7 = st.radio(
            "**Câu 7.** AI phân tích và đưa ra cảnh báo rủi ro, nhưng quyết định cuối cùng luôn thuộc về người có thẩm quyền. Bạn đánh giá mô hình này như thế nào?",
            [
                "Phù hợp, đây là cách tôi muốn AI được tích hợp vào quy trình hợp đồng",
                "Chấp nhận được, nhưng cần thêm cơ chế kiểm soát",
                "Chưa chắc, phụ thuộc vào độ chính xác thực tế của AI",
                "Không phù hợp với quy trình của tôi"
            ], index=None
        )

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        st.markdown("**Câu 8.** Rào cản lớn nhất khiến tổ chức bạn chưa sẵn sàng áp dụng AI vào review hợp đồng? *(Chọn tối đa 2)*")
        b1 = st.checkbox("Lo ngại về bảo mật dữ liệu hợp đồng")
        b2 = st.checkbox("Thiếu tin tưởng vào độ chính xác của AI")
        b3 = st.checkbox("Kháng cự từ nội bộ hoặc thói quen làm việc")
        b4 = st.checkbox("Thiếu sự ủng hộ từ Ban lãnh đạo")
        b5 = st.checkbox("Chi phí triển khai")
        b6 = st.checkbox("Không có nhu cầu vì quy trình hiện tại đã ổn")
        b7 = st.checkbox("Khác")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

        q9 = st.slider(
            "**Câu 9.** Giả sử dữ liệu hợp đồng chỉ được xử lý và lưu trữ trong nội bộ công ty, không chia sẻ ra bên ngoài. Nếu hệ thống được cung cấp miễn phí để dùng thử 3 tháng, khả năng bạn giới thiệu cho đồng nghiệp hoặc tổ chức là bao nhiêu?",
            min_value=1, max_value=10, value=5,
            help="1 = Chắc chắn không, 10 = Chắc chắn có"
        )
        col1, col2, col3 = st.columns(3)
        with col1: st.caption("1 = Chắc chắn không")
        with col2: st.caption(f"Bạn chọn: **{q9}/10**")
        with col3: st.caption("10 = Chắc chắn có")

        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("**Câu 10 đến 12:** Vui lòng cho biết mức độ đồng ý của bạn với các nhận định sau.")
        st.caption("1 = Hoàn toàn không đồng ý, 5 = Hoàn toàn đồng ý")

        q10_pu = st.radio(
            "**Câu 10.** Hệ thống AI hỗ trợ review hợp đồng có thể giúp tôi giảm thiểu lỗi thủ công trong công việc hàng ngày.",
            LIKERT, index=None, horizontal=False
        )

        q11_trust = st.radio(
            "**Câu 11.** Tôi sẵn sàng tin tưởng vào các khuyến nghị của AI khi chúng được kiểm tra và phê duyệt bởi người có thẩm quyền.",
            LIKERT, index=None, horizontal=False
        )

        q12_intent = st.radio(
            "**Câu 12.** Nếu tổ chức triển khai hệ thống này, tôi sẵn sàng sử dụng nó như một phần trong quy trình làm việc hàng ngày.",
            LIKERT, index=None, horizontal=False
        )

        submitted = st.form_submit_button("Tiếp theo")

    if submitted:
        barriers = []
        if b1: barriers.append("Bảo mật dữ liệu")
        if b2: barriers.append("Độ chính xác AI")
        if b3: barriers.append("Kháng cự nội bộ")
        if b4: barriers.append("Thiếu ủng hộ từ lãnh đạo")
        if b5: barriers.append("Chi phí")
        if b6: barriers.append("Không có nhu cầu")
        if b7: barriers.append("Khác")

        if q6 is None or q7 is None:
            st.warning("Vui lòng trả lời Câu 6 và Câu 7.")
        elif q10_pu is None or q11_trust is None or q12_intent is None:
            st.warning("Vui lòng trả lời đầy đủ Câu 10, 11 và 12.")
        elif len(barriers) > 2:
            st.warning("Câu 8: Vui lòng chọn tối đa 2 rào cản.")
        else:
            st.session_state.answers["q6_adoption_intent"] = q6
            st.session_state.answers["q7_hitl_acceptance"] = q7
            st.session_state.answers["q8_barriers"] = ", ".join(barriers) if barriers else "Không chọn"
            st.session_state.answers["q9_nps"] = q9
            st.session_state.answers["q10_perceived_usefulness"] = q10_pu
            st.session_state.answers["q11_trust_hitl"] = q11_trust
            st.session_state.answers["q12_deployment_intention"] = q12_intent
            st.session_state.step = 4
            st.rerun()

# ── STEP 4: Demographics ───────────────────────────────────────────────────────
elif step == 4:
    st.markdown('<div class="section-label">Phần 4 — Thông tin bối cảnh (không bắt buộc)</div>', unsafe_allow_html=True)
    with st.form("form_step4"):
        q13 = st.selectbox(
            "**Câu 13.** Vai trò hiện tại của bạn gần nhất với nhóm nào?",
            ["(Bỏ qua)", "Quản lý thương mại / Kinh doanh", "Mua hàng / Đấu thầu",
             "Quản lý dự án", "Pháp lý / Hành chính hợp đồng", "Tài chính / Kế toán", "Khác"]
        )
        q14 = st.selectbox(
            "**Câu 14.** Số năm kinh nghiệm làm việc với hợp đồng B2B?",
            ["(Bỏ qua)", "Dưới 2 năm", "2 đến 5 năm", "5 đến 10 năm", "Trên 10 năm"]
        )
        q15 = st.selectbox(
            "**Câu 15.** Ngành bạn đang làm việc?",
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
        st.session_state.answers["q13_role"] = q13
        st.session_state.answers["q14_experience"] = q14
        st.session_state.answers["q15_industry"] = q15
        st.session_state.answers["email_optional"] = email if email else ""
        st.session_state.answers["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with st.spinner("Đang lưu phản hồi..."):
            time.sleep(0.8)
            success = save_response(st.session_state.answers)

        st.session_state.step = 100 if success else 101
        st.rerun()

# ── DONE ───────────────────────────────────────────────────────────────────────
elif step == 100:
    st.markdown("""
    <div class="success-box">
        <div style="font-size:2.5rem;margin-bottom:1rem;">✅</div>
        <h3 style="color:#166534;margin-bottom:0.5rem;">Cảm ơn bạn đã tham gia!</h3>
        <p style="color:#15803D;margin:0;">Tâm vô cùng biết ơn thời gian quý báu bạn đã dành ra để hỗ trợ tham gia khảo sát.<br>
        Kết quả sẽ được sử dụng trong nghiên cứu học thuật về ứng dụng AI trong soạn thảo và kiểm tra hợp đồng thương mại B2B.<br><br>
        Nếu bạn muốn nhận tóm tắt kết quả nghiên cứu, vui lòng để lại email ở phần trên.</p>
    </div>
    """, unsafe_allow_html=True)

elif step == 101:
    st.error("Có lỗi xảy ra khi lưu phản hồi. Vui lòng thử lại.")
    if st.button("Thử lại"):
        if save_response(st.session_state.answers):
            st.session_state.step = 100
            st.rerun()

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
