import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. 페이지 및 전역 CSS 설정 ---
st.set_page_config(page_title="Collatz CA Visualizer", layout="centered")

# 배경색 및 셀 디자인 CSS 주입
custom_css = """
<style>
/* 전체 배경색 설정 */
[data-testid="stAppViewContainer"] {
    background-color: #FFFFCC;
}
/* 상단 헤더 배경색 투명화 */
[data-testid="stHeader"] {
    background-color: transparent;
}

/* 가로/세로 스크롤을 지원하는 컨테이너 */
.scroll-container {
    width: 100%;
    max-height: 70vh; /* 화면 높이의 70%만큼만 차지하도록 제한 */
    overflow-x: auto;
    overflow-y: auto; /* 세로 스크롤도 컨테이너 내부에서 작동 */
    white-space: nowrap;
    padding-bottom: 15px;
}

/* 가로 스크롤바 디자인 */
.scroll-container::-webkit-scrollbar {
    height: 6px;
}
.scroll-container::-webkit-scrollbar-thumb {
    background: #FF1493; /* 소수점 색상과 맞춘 핫핑크 */
    border-radius: 4px;
}
.scroll-container::-webkit-scrollbar-track {
    background: transparent;
}

@keyframes jellyAppear {
    0% {
        transform: scale(0) rotate(-45deg);
        opacity: 0;
    }
    50% {
        transform: scale(1.2) rotate(15deg);
    }
    70% {
        transform: scale(0.9) rotate(-5deg);
    }
    100% {
        transform: scale(1) rotate(0deg);
        opacity: 1;
    }
}

/* CA 행 컨테이너 */
.ca-row {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 20px;
    padding: 10px;
}

/* 개별 셀 기본 스타일 */
.ca-cell {
    width: 40px;
    height: 40px;
    margin: 0 2px;
    border: 2px solid black;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
    font-family: monospace;
    color: black;
    animation: jellyAppear 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
    flex-shrink: 0;
}

/* 숫자 셀 색상 그라데이션 */
.cell-0 { background-color: #E8F5E9; }
.cell-1 { background-color: #C8E6C9; }
.cell-2 { background-color: #90CAF9; }
.cell-3 { background-color: #64B5F6; }
.cell-4 { background-color: #1E88E5; }
.cell-5 { background-color: #1565C0; color: black; }

/* 소수점 셀 네온사인 효과 */
.cell-x {
    background-color: transparent;
    color: #FF1493;
    border-color: #FF1493;
    box-shadow: 0 0 12px #FF1493, inset 0 0 12px #FF1493;
    text-shadow: 0 0 8px #FF1493;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 2. CA 규칙 정의 ---
CA_RULES = {}

for left in [0, 1, 2, 3, 4, 5, 'x']:
    for curr in [0, 1, 2, 3, 4, 5]:
        for right in [0, 1, 2, 3, 4, 5]:
            CA_RULES[(left, curr, right)] = (3 * curr) % 6 + (3 * right) // 6

for left in [0, 1, 2, 3, 4, 5, 'x']:
    for curr in [1, 3, 5]:
        CA_RULES[(left, curr, 'x')] = (3 * curr) % 6 + 1
    for curr in [0, 2, 4]:
        CA_RULES[(left, curr, 'x')] = 'x'

for left in [1, 3, 5]:
    for right in [0, 1, 2, 3, 4, 5, 'x']:
        CA_RULES[(left, 'x', right)] = 'x'
for left in [0, 2, 4]:
    for right in [0, 1, 2, 3, 4, 5, 'x']:
        CA_RULES[(left, 'x', right)] = 0

def collatz_ca_step(state):
    next_body = [
        CA_RULES[(l, c, r)] 
        for l, c, r in zip(state[:-2], state[1:-1], state[2:])
    ]
    return [0] + next_body + [0]

def to_base6_list(num):
    if num == 0:
        return [0]
    base6 = []
    temp = num
    while temp > 0:
        base6.insert(0, temp % 6)
        temp //= 6
    return base6

# --- 3. Streamlit 상태 및 화면 제어 ---
if 'phase' not in st.session_state:
    st.session_state.phase = 'input'

if st.session_state.phase == 'input':
    st.title("Collatz Conjecture CA")
    
    col1, col2 = st.columns(2)
    with col1:
        num_input = st.number_input("10진법 정수 입력", min_value=0, value=27, step=1)
    with col2:
        # [핵심 수정] max_value 속성을 제거하여 스트림릿이 멋대로 값을 20이나 50으로 바꾸는 독단(?)을 막습니다.
        steps_input = st.number_input("계산할 스텝 수", min_value=1, value=20, step=1)
        
    # --- 우리가 직접 만든 강력한 50스텝 검문소 ---
    is_over_limit = steps_input > 50
    
    if is_over_limit:
        # 사용자가 입력한 숫자가 그대로 유지되면서 빨간 에러창이 뜹니다.
        st.error(f"🚨 **스텝 수 제한 초과:** 안정적인 시각화를 위해 최대 **50스텝**까지만 연산 가능합니다. 현재 입력값: {steps_input}")
        # 버튼을 완전히 무력화된 비활성화 버전으로 바꿔치기합니다.
        st.button("실행 불가 (스텝 수 초과)", use_container_width=True, disabled=True, key="btn_disabled")
    else:
        st.info("💡 Tip: 숫자가 커질수록 연산 공간이 늘어나므로 적절한 스텝 수를 입력하는 것이 좋습니다.")
        # 50 이하일 때만 정상적인 실행 버튼이 뜹니다.
        if st.button("실행", use_container_width=True, key="btn_enabled"):
            st.session_state.num = num_input
            st.session_state.steps = steps_input
            st.session_state.phase = 'conversion'
            st.rerun()

elif st.session_state.phase == 'conversion':
    base6_vals = to_base6_list(st.session_state.num)
    base6_str = "".join(map(str, base6_vals))
    
    st.title("🔄 6진법으로 변환 중...")
    st.markdown(f"<h2 style='text-align: center; color: #1565C0;'>10진수 {st.session_state.num} ➔ 6진수 {base6_str}</h2>", unsafe_allow_html=True)
    
    time.sleep(1.0)
    st.session_state.phase = 'ca_run'
    st.rerun()

elif st.session_state.phase == 'ca_run':
    st.title("Collatz CA Visualization")
    
    if st.button("다시 입력하기"):
        st.session_state.phase = 'input'
        st.rerun()
    
    ca_container = st.empty()
    
    base6_list = to_base6_list(st.session_state.num)
    state = [0] * 500 + base6_list + ['x'] + [0] * 2
    
    steps = st.session_state.steps
    accumulated_html = ""
    
    for step in range(steps + 1):
        try:
            x_idx = state.index('x')
        except ValueError:
            x_idx = len(state) // 2
            
        if x_idx < 40:
            state = [0] * 50 + state
            x_idx += 50
        if len(state) - x_idx < 3:
            state = state + [0] * 2
            
        # 소수점 고정 해제 및 정적 맵 넓게 출력
        window = state[350:]
        
        row_html = '<div class="ca-row">'
        for val in window:
            if val == 'x':
                row_html += '<div class="ca-cell cell-x">.</div>'
            else:
                row_html += f'<div class="ca-cell cell-{val}">{val}</div>'
        row_html += '</div>'
        
        accumulated_html += row_html
        
        full_wrapped_html = f'<div class="scroll-container" id="ca-scroll-box">{accumulated_html}</div>'
        ca_container.markdown(full_wrapped_html, unsafe_allow_html=True)
        
        # [버버벅임 완벽 최적화 버전 적용]
        # 첫 스텝은 'instant'로 강제 우측 정렬, 이후 연산은 대기 시간 충돌을 방지하기 위해 'instant'로 끊김 없이 밀어줍니다.
        scroll_behavior = 'instant'
        
        components.html(
            f"""
            <script>
            var scrollBox = parent.document.getElementById('ca-scroll-box');
            if (scrollBox) {{
                var cells = scrollBox.getElementsByClassName('cell-x');
                if (cells.length > 0) {{
                    var lastCell = cells[cells.length - 1];
                    
                    scrollBox.scrollTo({{
                        left: lastCell.offsetLeft - (scrollBox.clientWidth / 2) + (lastCell.clientWidth / 2),
                        top: scrollBox.scrollHeight,
                        behavior: '{scroll_behavior}'
                    }});
                }}
            }}
            </script>
            """,
            height=0,
            width=0
        )
        
        if step < steps:
            time.sleep(0.3)
            state = collatz_ca_step(state)
