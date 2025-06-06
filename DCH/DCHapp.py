# DCHapp.py
import streamlit as st

st.set_page_config(
    page_title="오이 질병 분석기",
    page_icon="🥒",
    layout="wide"
)

st.title("오이 잎 질병 면적률 계산기")
st.markdown("분석하고자 하는 질병을 아래에서 선택하세요. 각 분석 페이지에서는 HSV 값을 조절하여 병반 영역을 탐색합니다.")
st.divider()

st.subheader("분석할 질병 선택")
col1, col2 = st.columns(2)

with col1:
    if st.button("⚪ 흰가루병 분석 페이지로 이동", use_container_width=True):
        st.switch_page("pages/1_흰가루병_분석.py")

with col2:
    if st.button("🟡 노균병 분석 페이지로 이동", use_container_width=True):
        st.switch_page("pages/2_노균병_분석.py")

st.sidebar.success("분석할 질병을 선택하세요.") # 이 부분은 사이드바에 표시되므로 위치는 그대로 둡니다.

st.divider() # 질병 선택 버튼과 HSV 설명 사이에 구분선 추가

# --- HSV 색상 공간 설명 섹션 (버튼 아래로 이동) ---
st.header("💡 HSV 색상 공간 이해하기 / Understanding HSV Color Space")

st.markdown(
    """
    ---
    **한글 설명 (Korean Description):**

    본 분석기는 이미지에서 특정 색상 범위를 분리하기 위해 **HSV 색상 공간**을 사용합니다. 
    HSV는 색상을 표현하는 한 방식으로, 다음과 같은 세 가지 요소로 구성됩니다:

    *   **H (Hue, 색상)**: 색의 종류를 나타냅니다. 0°에서 360°까지의 각도로 표현되며, 빨간색에서 시작하여 주황, 노랑, 초록, 파랑, 보라를 거쳐 다시 빨간색으로 돌아옵니다.
        *   OpenCV에서는 보통 0-179 범위로 표현됩니다 (360°를 2로 나눈 값).
        *   예: 0은 빨강 근처, 60은 초록 근처, 120은 파랑 근처입니다.
    *   **S (Saturation, 채도)**: 색의 선명도 또는 순도를 나타냅니다. 값이 낮을수록 색이 흐릿해지고 회색에 가까워지며 (무채색), 높을수록 색이 짙고 선명해집니다.
        *   보통 0-255 (또는 0-100%) 범위로 표현됩니다.
    *   **V (Value, 명도 또는 밝기)**: 색의 밝기를 나타냅니다. 값이 낮을수록 어두워지고, 높을수록 밝아집니다.
        *   보통 0-255 (또는 0-100%) 범위로 표현됩니다.

    각 분석 페이지의 HSV 슬라이더를 조절하여, **잎사귀의 건강한 부분(주로 녹색 계열)과 병반 부분(흰가루병의 경우 흰색/회색, 노균병의 경우 노란색/갈색 계열)을 가장 잘 구분**하는 값의 범위를 찾을 수 있습니다. 
    이를 통해 병반 면적률을 더 정확하게 계산할 수 있습니다.

    ---
    **English Description:**

    This analyzer uses the **HSV color space** to isolate specific color ranges in images.
    HSV is a way to represent colors and consists of the following three components:

    *   **H (Hue)**: Represents the type of color. It is expressed as an angle from 0° to 360°, starting from red, passing through orange, yellow, green, blue, purple, and back to red.
        *   In OpenCV, it is typically represented in the range of 0-179 (360° divided by 2).
        *   Example: 0 is near red, 60 is near green, and 120 is near blue.
    *   **S (Saturation)**: Represents the vividness or purity of the color. Lower values make the color duller and closer to gray (achromatic), while higher values make the color richer and more vibrant.
        *   Typically represented in the range of 0-255 (or 0-100%).
    *   **V (Value, or Brightness)**: Represents the brightness of the color. Lower values make the color darker, and higher values make it brighter.
        *   Typically represented in the range of 0-255 (or 0-100%).

    By adjusting the HSV sliders on each analysis page, you can find the value range that best **distinguishes between healthy parts of the leaf (mainly green hues) and diseased parts (white/gray for powdery mildew, yellow/brown hues for downy mildew)**.
    This allows for a more accurate calculation of the lesion area percentage.
    ---
    """
)
