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

/* 가로 스크롤을 지원하는 컨테이너 보완 */
.scroll-container {
    width: 100%;
    max-height: 70vh; /* 화면 높이의 70%만큼만 차지하도록 제한 */
    overflow-x: auto;
    overflow-y: auto; /* [추가] 세로 스크롤도 컨테이너 내부에서 작동하도록 설정 */
    white-space: nowrap;
    padding-bottom: 15px;
}

/* (선택사항) 가로 스크롤바를 조금 더 얇고 예쁘게 만들기 */
.scroll-container::-webkit-scrollbar {
    height: 6px;
}
.scroll-container::-webkit-scrollbar-thumb {
    background: #FF1493; /* 소수점 색상과 맞춘 핫핑크 얇은 바 */
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
        transform: scale(1.2) rotate(15deg); /* 살짝 커졌다가 회전 */
    }
    70% {
        transform: scale(0.9) rotate(-5deg); /* 살짝 수축 */
    }
    100% {
        transform: scale(1) rotate(0deg);    /* 원래대로 */
        opacity: 1;
    }
}


/* CA 행 컨테이너 (가운데 정렬, 셀 높이의 반인 20px 마진) */
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
    /* 0.4초 동안 젤리 효과 실행 */
    animation: jellyAppear 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
    flex-shrink: 0; /* 셀 크기가 찌그러지지 않도록 고정 */
}

/* 숫자 셀 색상 그라데이션 */
.cell-0 { background-color: #E8F5E9; }
.cell-1 { background-color: #C8E6C9; }
.cell-2 { background-color: #90CAF9; }
.cell-3 { background-color: #64B5F6; }
.cell-4 { background-color: #1E88E5; }
.cell-5 { background-color: #1565C0; color: black; }

/* 소수점 셀 (x -> .) 네온사인 효과 */
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

# --- 2. CA 규칙 정의 (제공된 코드 적용) ---
CA_RULES = {}

# 기본 규칙
for left in [0, 1, 2, 3, 4, 5, 'x']:
    for curr in [0, 1, 2, 3, 4, 5]:
        for right in [0, 1, 2, 3, 4, 5]:
            CA_RULES[(left, curr, right)] = (3 * curr) % 6 + (3 * right) // 6

# 특별 규칙 1: 오른쪽 셀이 'x'인 경우
for left in [0, 1, 2, 3, 4, 5, 'x']:
    for curr in [1, 3, 5]:
        CA_RULES[(left, curr, 'x')] = (3 * curr) % 6 + 1
    for curr in [0, 2, 4]:
        CA_RULES[(left, curr, 'x')] = 'x'

# 특별 규칙 2: 현재 셀이 'x'인 경우
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
        num_input = st.number_input("10진법 정수 입력", min_value=0, value=9, step=1)
    with col2:
        # max_value=150 을 추가하여 최대 입력 가능한 스텝 수를 제한합니다.
        steps_input = st.number_input("계산할 스텝 수", min_value=1, max_value=50, value=20, step=1)
        st.caption("최대 50스텝까지 제한")        
    if st.button("실행", use_container_width=True):
        st.session_state.num = num_input
        st.session_state.steps = steps_input
        st.session_state.phase = 'conversion'
        st.rerun()

elif st.session_state.phase == 'conversion':
    # 6진수 변환 화면
    base6_vals = to_base6_list(st.session_state.num)
    base6_str = "".join(map(str, base6_vals))
    
    st.title("🔄 6진법으로 변환 중...")
    st.markdown(f"<h2 style='text-align: center; color: #1565C0;'>10진수 {st.session_state.num} ➔ 6진수 {base6_str}</h2>", unsafe_allow_html=True)
    
    # 1초 대기 후 CA 실행 페이지로 자동 전환
    time.sleep(1.0)
    st.session_state.phase = 'ca_run'
    st.rerun()

elif st.session_state.phase == 'ca_run':
    st.title("Collatz CA Visualization")
    
    # 재시작 버튼
    if st.button("다시 입력하기"):
        st.session_state.phase = 'input'
        st.rerun()
    
    # 애니메이션이 렌더링될 빈 컨테이너 생성
    ca_container = st.empty()
    
    # [수정] 100스텝 이상의 대형 연산도 버틸 수 있도록 왼쪽 패딩을 500칸으로 대폭 확장합니다.
    base6_list = to_base6_list(st.session_state.num)
    state = [0] * 500 + base6_list + ['x'] + [0] * 2
    
    steps = st.session_state.steps
    accumulated_html = ""
    
    for step in range(steps + 1):
        # 넉넉한 패딩 유지: 'x'가 왼쪽으로 너무 가면 추가 패딩
        try:
            x_idx = state.index('x')
        except ValueError:
            # 예외적으로 x가 사라진 경우 (규칙에 의해 0으로 소멸) 처리
            x_idx = len(state) // 2
            
        # 왼쪽 공간이 부족해지면 50칸씩 대폭 수급
        if x_idx < 40:
            state = [0] * 50 + state
            x_idx += 50
        # 오른쪽 공간은 항상 '2칸' 근처를 유지하도록 감시 및 보충
        if len(state) - x_idx < 3:
            state = state + [0] * 2
            

        # [수정] 소수점 기준 고정을 완전히 해제합니다.
        # 초기 500칸의 패딩 중 의미 없는 앞쪽 350칸만 잘라내고, 나머지는 통째로 화면에 출력하여 
        # 소수점이 실제로 왼쪽, 오른쪽으로 이동하는 모습을 정적 구조 안에 그대로 노출시킵니다.
        window = state[350:]
        
        # HTML 렌더링을 위한 태그 생성
        row_html = '<div class="ca-row">'
        for val in window:
            if val == 'x':
                row_html += '<div class="ca-cell cell-x">.</div>'
            else:
                row_html += f'<div class="ca-cell cell-{val}">{val}</div>'
        row_html += '</div>'
        
        accumulated_html += row_html
        
# 1. 전체 누적 HTML을 가로 스크롤 컨테이너로 감싸서 마크다운으로 렌더링
        full_wrapped_html = f'<div class="scroll-container" id="ca-scroll-box">{accumulated_html}</div>'
        ca_container.markdown(full_wrapped_html, unsafe_allow_html=True)
        
        # 2. 스트림릿 보안(XSS 제한)을 우회하여 브라우저에 스크롤 명령을 강제로 주입 (유령 iframe 활용)
        # 2. 스트림릿 보안 우회 및 가로/세로 추적 스크롤 (초기 우측 고정 기능 추가)
        components.html(
            f"""
            <script>
            var scrollBox = parent.document.getElementById('ca-scroll-box');
            if (scrollBox) {{
                var cells = scrollBox.getElementsByClassName('cell-x');
                if (cells.length > 0) {{
                    var lastCell = cells[cells.length - 1];
                    
                    // 현재 스텝이 0(첫 시작)일 때는 부드러운 효과 없이 즉시 맨 오른쪽 소수점 위치로 카메라를 고정합니다.
                    var scrollBehavior = '{'instant' if step == 0 else 'smooth'}';
                    
                    // 소수점 셀이 스크롤 박스의 중앙에 오도록 가로/세로 동시 스크롤 수행
                    scrollBox.scrollTo({{
                        left: lastCell.offsetLeft - (scrollBox.clientWidth / 2) + (lastCell.clientWidth / 2),
                        top: scrollBox.scrollHeight,
                        behavior: scrollBehavior
                    }});
                }}
            }}
            </script>
            """,
            height=0,
            width=0
        )
        
        # 다음 스텝 계산 전에 0.3초 대기 (마지막 스텝 제외)
        if step < steps:
            time.sleep(0.3)
            state = collatz_ca_step(state)
