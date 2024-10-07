import streamlit as st
import os
import cv2
import numpy as np
import sqlite3
from PIL import Image

def compute_histogram(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def euclidean_distance(hist1, hist2):
    return np.linalg.norm(hist1 - hist2)

def get_histogram_from_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT image_path, histogram FROM histograms')
    results = c.fetchall()
    conn.close()
    return [(r[0], np.frombuffer(r[1], dtype=np.float32)) for r in results]


seg_test_path = 'seg_test'
seg_path = 'seg'

# Lấy danh sách các folder trong seg_test
subfolders = [f.name for f in os.scandir(seg_test_path) if f.is_dir()]
selected_folder = st.selectbox("Chọn folder", subfolders)

# Lấy danh sách ảnh trong folder đã chọn
images = [f for f in os.listdir(os.path.join(seg_test_path, selected_folder)) if f.endswith(('png', 'jpg', 'jpeg'))]
selected_image = st.selectbox("Chọn ảnh", images)

# Hiển thị ảnh đã chọn
image_path = os.path.join(seg_test_path, selected_folder, selected_image)
st.image(image_path, caption=f"Ảnh đã chọn: {selected_image}", use_column_width=False)

selected_hist = compute_histogram(image_path)
            
databases = [f for f in os.listdir() if f.endswith('_histograms.db')]

# Tìm 10 ảnh có histogram gần nhất từ các database
closest_images = []
for db in databases:
    histograms = get_histogram_from_db(db)
    for img_path, hist in histograms:
        distance = euclidean_distance(selected_hist, hist)
        
        # Thêm vào danh sách cho đủ 10 ảnh
        if len(closest_images) < 10:
            closest_images.append((img_path, distance))
            closest_images.sort(key=lambda x: x[1])  # Sắp xếp theo khoảng cách
        
        # Nếu đã có 10 ảnh, chỉ thêm nếu khoảng cách nhỏ hơn ảnh xa nhất trong danh sách
        else:
            if distance < closest_images[-1][1]:
                closest_images[-1] = (img_path, distance)
                closest_images.sort(key=lambda x: x[1])  # Sắp xếp lại theo khoảng cách


st.write("Top 10 ảnh gần nhất:")

columns = st.columns(5)
for i in range(5):
    with columns[i]:
        st.image(closest_images[i][0], caption=f"Khoảng cách: {closest_images[i][1]:.2f}", use_column_width=True)
        
columns = st.columns(5)
for i in range(5, 10):
    with columns[i - 5]:
        st.image(closest_images[i][0], caption=f"Khoảng cách: {closest_images[i][1]:.2f}", use_column_width=True)