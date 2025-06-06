# pages/1_흰가루병_분석.py
import streamlit as st
from PIL import Image
import io
import pandas as pd
from utils import calculate_disease_area_ratio
from streamlit_cropper import st_cropper

st.set_page_config(page_title="흰가루병 분석", layout="wide")
st.title("⚪ 흰가루병 분석")
st.markdown("흰가루병 의심 오이 잎 사진을 업로드하고 병반 면적률을 실시간 분석하세요.")

DISEASE_TYPE_NAME = "흰색 반점"
DEFAULT_LOWER_DISEASE_HSV = [0, 0, 180]
DEFAULT_UPPER_DISEASE_HSV = [180, 80, 255]
DEFAULT_LOWER_LEAF_HSV = [35, 40, 40]
DEFAULT_UPPER_LEAF_HSV = [85, 255, 255]

SESSION_KEY_PREFIX = "pm_" # 흰가루병 페이지 접두사

uploaded_files = st.file_uploader(
    "흰가루병 오이 잎 사진 업로드 (여러 장 가능)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"{SESSION_KEY_PREFIX}uploader"
)

# 전체 이미지용 HSV 설정 세션
if f"{SESSION_KEY_PREFIX}hsv_settings_main" not in st.session_state:
    st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"] = {}
# 크롭퍼 표시 여부 세션
if f"{SESSION_KEY_PREFIX}show_cropper" not in st.session_state:
    st.session_state[f"{SESSION_KEY_PREFIX}show_cropper"] = {}
# 크롭 영역용 HSV 설정 세션
if f"{SESSION_KEY_PREFIX}hsv_settings_cropped" not in st.session_state:
    st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"] = {}

results_for_csv = []

def get_disease_grade(ratio):
    if ratio == 0: return 0
    elif 0 < ratio < 5.1: return 1
    elif 5.1 <= ratio < 20.1: return 2
    elif 20.1 <= ratio < 50.1: return 3
    else: return 4

if uploaded_files:
    st.markdown("---")
    for idx, uploaded_file_obj in enumerate(uploaded_files):
        file_specific_key = f"{SESSION_KEY_PREFIX}{uploaded_file_obj.name}_{uploaded_file_obj.size}_{idx}"
        image_file_bytes = uploaded_file_obj.getvalue()

        # 전체 이미지 HSV 설정 초기화
        if file_specific_key not in st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"]:
            st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key] = {
                'lower_disease': list(DEFAULT_LOWER_DISEASE_HSV),
                'upper_disease': list(DEFAULT_UPPER_DISEASE_HSV),
            }
        current_hsv_settings_main = st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]

        # 크롭퍼 표시 상태 초기화
        if file_specific_key not in st.session_state[f"{SESSION_KEY_PREFIX}show_cropper"]:
            st.session_state[f"{SESSION_KEY_PREFIX}show_cropper"][file_specific_key] = False
        
        # 크롭 영역 HSV 설정 초기화 (크롭 시작 시 또는 필요시)
        if file_specific_key not in st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"]:
            st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key] = {
                'lower_disease': list(DEFAULT_LOWER_DISEASE_HSV), # 기본값은 전체 이미지와 동일하게 시작
                'upper_disease': list(DEFAULT_UPPER_DISEASE_HSV),
            }

        # --- 1. 전체 이미지 HSV 조절 및 결과 ---
        with st.expander(f"🛠️ {uploaded_file_obj.name} - 전체 이미지 {DISEASE_TYPE_NAME} HSV 조절 및 결과 비교", expanded=True):
            st.markdown(f"#### 전체 이미지 '{DISEASE_TYPE_NAME}' HSV 범위 조절")
            
            # 전체 이미지용 슬라이더
            lmh_val = current_hsv_settings_main['lower_disease'][0]
            lms_val = current_hsv_settings_main['lower_disease'][1]
            lmv_val = current_hsv_settings_main['lower_disease'][2]
            umh_val = current_hsv_settings_main['upper_disease'][0]
            ums_val = current_hsv_settings_main['upper_disease'][1]
            umv_val = current_hsv_settings_main['upper_disease'][2]

            col_mlh, col_mls, col_mlv = st.columns(3)
            with col_mlh: new_lmh = st.slider(f"Main Lower H", 0, 180, lmh_val, key=f"{file_specific_key}_mlh")
            with col_mls: new_lms = st.slider(f"Main Lower S", 0, 255, lms_val, key=f"{file_specific_key}_mls")
            with col_mlv: new_lmv = st.slider(f"Main Lower V", 0, 255, lmv_val, key=f"{file_specific_key}_mlv")
            
            col_muh, col_mus, col_muv = st.columns(3)
            with col_muh: new_umh = st.slider(f"Main Upper H", 0, 180, umh_val, key=f"{file_specific_key}_muh")
            with col_mus: new_ums = st.slider(f"Main Upper S", 0, 255, ums_val, key=f"{file_specific_key}_mus")
            with col_muv: new_umv = st.slider(f"Main Upper V", 0, 255, umv_val, key=f"{file_specific_key}_muv")

            st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]['lower_disease'] = [new_lmh, new_lms, new_lmv]
            st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]['upper_disease'] = [new_umh, new_ums, new_umv]

            if st.button("↩️ 전체 이미지 HSV 초기화", key=f"{file_specific_key}_reset_main_hsv"):
                st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]['lower_disease'] = list(DEFAULT_LOWER_DISEASE_HSV)
                st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]['upper_disease'] = list(DEFAULT_UPPER_DISEASE_HSV)
                st.rerun()

            # 전체 이미지 분석
            final_hsv_main = st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]
            ratio_main, original_main, processed_main = calculate_disease_area_ratio(
                f"{file_specific_key}_main_{final_hsv_main['lower_disease']}_{final_hsv_main['upper_disease']}",
                image_file_bytes, final_hsv_main['lower_disease'], final_hsv_main['upper_disease'],
                DEFAULT_LOWER_LEAF_HSV, DEFAULT_UPPER_LEAF_HSV
            )
            st.markdown("---")
            st.markdown("#### 🎨 전체 이미지 원본 vs. 조절 후 결과")
            col_img1_main, col_img2_main = st.columns(2)
            with col_img1_main:
                if original_main: st.image(original_main, caption="원본", use_container_width=True)
            with col_img2_main:
                if processed_main: st.image(processed_main, caption=f"전체 이미지 {DISEASE_TYPE_NAME} 표시", use_container_width=True)
            
            grade_main = get_disease_grade(ratio_main)
            st.markdown(f"**전체 병반 면적률: <span style='font-size:18px; font-weight:bold;'>{ratio_main:.2f}%</span>**", unsafe_allow_html=True)
            st.markdown(f"**전체 병반 등급: <span style='font-size:18px; font-weight:bold;'>{grade_main}</span>**", unsafe_allow_html=True)
            st.markdown("##### 현재 적용된 전체 이미지 HSV 값")
            st.json({f"Lower {DISEASE_TYPE_NAME}": final_hsv_main['lower_disease'], f"Upper {DISEASE_TYPE_NAME}": final_hsv_main['upper_disease']})

        # --- 2. 사각형 크롭 영역 분석 기능 ---
        st.markdown("---")
        st.subheader(f"✂️ {uploaded_file_obj.name} - 선택 영역 분석 (사각형 크롭)")

        if st.button(f"'{uploaded_file_obj.name}' 사진에서 영역 선택 시작", key=f"{file_specific_key}_start_crop"):
            st.session_state[f"{SESSION_KEY_PREFIX}show_cropper"][file_specific_key] = True
            # 크롭 시작 시, 크롭 영역 HSV를 해당 질병의 기본값으로 리셋
            st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key] = {
                'lower_disease': list(DEFAULT_LOWER_DISEASE_HSV),
                'upper_disease': list(DEFAULT_UPPER_DISEASE_HSV),
            }
            st.rerun()

        if st.session_state[f"{SESSION_KEY_PREFIX}show_cropper"].get(file_specific_key, False):
            st.info("이미지 위에서 분석할 사각형 영역을 선택하세요.")
            pil_bg_image = Image.open(io.BytesIO(image_file_bytes)).convert("RGB")
            
            cropped_img_pil = st_cropper(
                pil_bg_image, realtime_update=True, box_color='blue',
                aspect_ratio=None, key=f"{file_specific_key}_cropper"
            )

            if cropped_img_pil:
                st.image(cropped_img_pil, caption="선택된 영역 미리보기", width=200)

                # --- 2a. 크롭 영역에 대한 독립적인 HSV 조절 ---
                st.markdown(f"#### ✂️ 선택 영역 '{DISEASE_TYPE_NAME}' HSV 범위 조절")
                current_hsv_settings_cropped = st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key]
                
                lch_val = current_hsv_settings_cropped['lower_disease'][0]
                lcs_val = current_hsv_settings_cropped['lower_disease'][1]
                lcv_val = current_hsv_settings_cropped['lower_disease'][2]
                uch_val = current_hsv_settings_cropped['upper_disease'][0]
                ucs_val = current_hsv_settings_cropped['upper_disease'][1]
                ucv_val = current_hsv_settings_cropped['upper_disease'][2]

                col_clh, col_cls, col_clv = st.columns(3)
                with col_clh: new_lch = st.slider(f"Crop Lower H", 0, 180, lch_val, key=f"{file_specific_key}_clh")
                with col_cls: new_lcs = st.slider(f"Crop Lower S", 0, 255, lcs_val, key=f"{file_specific_key}_cls")
                with col_clv: new_lcv = st.slider(f"Crop Lower V", 0, 255, lcv_val, key=f"{file_specific_key}_clv")
                
                col_cuh, col_cus, col_cuv = st.columns(3)
                with col_cuh: new_uch = st.slider(f"Crop Upper H", 0, 180, uch_val, key=f"{file_specific_key}_cuh")
                with col_cus: new_ucs = st.slider(f"Crop Upper S", 0, 255, ucs_val, key=f"{file_specific_key}_cus")
                with col_cuv: new_ucv = st.slider(f"Crop Upper V", 0, 255, ucv_val, key=f"{file_specific_key}_cuv")

                st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key]['lower_disease'] = [new_lch, new_lcs, new_lcv]
                st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key]['upper_disease'] = [new_uch, new_ucs, new_ucv]

                if st.button("↩️ 선택 영역 HSV 초기화", key=f"{file_specific_key}_reset_crop_hsv"):
                    st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key]['lower_disease'] = list(DEFAULT_LOWER_DISEASE_HSV)
                    st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key]['upper_disease'] = list(DEFAULT_UPPER_DISEASE_HSV)
                    st.rerun()
                
                # --- 2b. 크롭된 영역 분석 및 결과 표시 (독립 HSV 사용) ---
                cropped_img_byte_arr = io.BytesIO()
                cropped_img_pil.save(cropped_img_byte_arr, format="PNG")
                cropped_image_file_bytes = cropped_img_byte_arr.getvalue()

                hsv_for_cropped_analysis = st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_cropped"][file_specific_key]

                cropped_ratio, _, cropped_processed_pil = calculate_disease_area_ratio(
                    cache_key=f"{file_specific_key}_crop_{hsv_for_cropped_analysis['lower_disease']}_{hsv_for_cropped_analysis['upper_disease']}",
                    image_bytes=cropped_image_file_bytes,
                    lower_disease_hsv=hsv_for_cropped_analysis['lower_disease'],
                    upper_disease_hsv=hsv_for_cropped_analysis['upper_disease'],
                    lower_green_hsv=DEFAULT_LOWER_LEAF_HSV,
                    upper_green_hsv=DEFAULT_UPPER_LEAF_HSV
                )

                st.markdown("---")
                st.markdown("#### ✂️ 선택 영역 분석 결과 (독립 HSV 조절 적용)")
                col_crop_res1, col_crop_res2 = st.columns(2)
                with col_crop_res1:
                    st.image(cropped_img_pil, caption="선택된 영역 (원본)", use_container_width=True)
                with col_crop_res2:
                    if cropped_processed_pil:
                        st.image(cropped_processed_pil, caption=f"선택 영역 {DISEASE_TYPE_NAME} 표시", use_container_width=True)
                    else:
                        st.warning(f"선택 영역 {DISEASE_TYPE_NAME} 표시 이미지 생성 불가")
                
                cropped_grade = get_disease_grade(cropped_ratio)
                st.markdown(f"**선택 영역 병반 면적률: <span style='font-size:18px; font-weight:bold;'>{cropped_ratio:.2f}%</span>**", unsafe_allow_html=True)
                st.markdown(f"**선택 영역 병반 등급: <span style='font-size:18px; font-weight:bold;'>{cropped_grade}</span>**", unsafe_allow_html=True)
                st.markdown("##### 현재 적용된 선택 영역 HSV 값")
                st.json({
                    f"Lower Crop {DISEASE_TYPE_NAME}": hsv_for_cropped_analysis['lower_disease'],
                    f"Upper Crop {DISEASE_TYPE_NAME}": hsv_for_cropped_analysis['upper_disease']
                })
            else:
                st.info("이미지 위에서 분석할 사각형 영역을 선택해주세요.")
        
        # CSV 저장은 전체 이미지 분석 결과 기준
        final_hsv_for_csv = st.session_state[f"{SESSION_KEY_PREFIX}hsv_settings_main"][file_specific_key]
        ratio_for_csv, _, _ = calculate_disease_area_ratio(
            f"{file_specific_key}_csv_{final_hsv_for_csv['lower_disease']}_{final_hsv_for_csv['upper_disease']}",
            image_file_bytes, final_hsv_for_csv['lower_disease'], final_hsv_for_csv['upper_disease'],
            DEFAULT_LOWER_LEAF_HSV, DEFAULT_UPPER_LEAF_HSV
        )
        grade_for_csv = get_disease_grade(ratio_for_csv)
        results_for_csv.append({
            "파일명": uploaded_file_obj.name, "질병 종류": "흰가루병",
            "병반 면적률 (%)": f"{ratio_for_csv:.2f}", "병반 등급": grade_for_csv,
            f"Lower {DISEASE_TYPE_NAME} (H,S,V)": str(final_hsv_for_csv['lower_disease']),
            f"Upper {DISEASE_TYPE_NAME} (H,S,V)": str(final_hsv_for_csv['upper_disease'])
        })
        st.markdown("---")

    if results_for_csv:
        st.markdown("## 📊 전체 결과 요약 및 다운로드 (흰가루병)")
        df_results = pd.DataFrame(results_for_csv)
        st.dataframe(df_results)
        csv_output = df_results.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 흰가루병 결과 저장", data=csv_output,
            file_name="흰가루병_분석결과.csv", mime="text/csv",
            key=f"{SESSION_KEY_PREFIX}download_csv"
        )

if st.button("🏠 처음으로 돌아가기", key=f"{SESSION_KEY_PREFIX}home_button"):
    st.switch_page("DCHapp.py")
