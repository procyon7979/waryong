# utils.py
import streamlit as st
from PIL import Image, UnidentifiedImageError
import cv2
import numpy as np
import io

@st.cache_data(show_spinner="이미지 처리 중...")
def calculate_disease_area_ratio(cache_key, image_bytes, lower_disease_hsv, upper_disease_hsv, lower_green_hsv, upper_green_hsv):
    # ... (이전 답변의 utils.py 내용과 동일) ...
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
    except UnidentifiedImageError:
        st.error(f"이미지 파일을 열 수 없거나 지원하지 않는 형식입니다. (키: {cache_key})")
        return 0.0, None, None
    except Exception as e:
        st.error(f"이미지 로드 실패 (키: {cache_key}): {e}")
        return 0.0, None, None

    original_pil_image_for_display = pil_image.copy()

    image_np_rgb = np.array(pil_image.convert('RGB'))
    if image_np_rgb.ndim == 2:
        image_np_rgb = cv2.cvtColor(image_np_rgb, cv2.COLOR_GRAY2RGB)
    elif image_np_rgb.shape[2] == 4:
        image_np_rgb = cv2.cvtColor(image_np_rgb, cv2.COLOR_RGBA2RGB)
        
    image_bgr = cv2.cvtColor(image_np_rgb, cv2.COLOR_RGB2BGR)
    hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    lower_disease_hsv_np = np.array(lower_disease_hsv, dtype=np.uint8)
    upper_disease_hsv_np = np.array(upper_disease_hsv, dtype=np.uint8)
    lower_green_hsv_np = np.array(lower_green_hsv, dtype=np.uint8)
    upper_green_hsv_np = np.array(upper_green_hsv, dtype=np.uint8)

    disease_mask = cv2.inRange(hsv_image, lower_disease_hsv_np, upper_disease_hsv_np)
    leaf_mask = cv2.inRange(hsv_image, lower_green_hsv_np, upper_green_hsv_np)
    
    disease_area = cv2.countNonZero(disease_mask)
    leaf_area = cv2.countNonZero(leaf_mask)
    
    ratio = 0.0
    if leaf_area > 0:
        ratio = (disease_area / leaf_area) * 100
    
    visualization_img_np = image_np_rgb.copy()
    visualization_img_np[disease_mask > 0] = [255, 0, 0]

    try:
        processed_image_pil = Image.fromarray(visualization_img_np)
    except Exception as e:
        st.error(f"처리된 이미지를 생성하는 데 실패했습니다 (키: {cache_key}): {e}")
        return ratio, original_pil_image_for_display, None
        
    return ratio, original_pil_image_for_display, processed_image_pil
