import os
import cv2
import numpy as np
import sqlite3

def compute_histogram(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def save_histogram_to_db(db_path, image_path, histogram):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
  
    c.execute('''
    CREATE TABLE IF NOT EXISTS histograms (
        image_path TEXT PRIMARY KEY,
        histogram BLOB
    )
    ''')
    hist_blob = histogram.tobytes()
    
    c.execute('INSERT OR REPLACE INTO histograms (image_path, histogram) VALUES (?, ?)', (image_path, hist_blob))
    conn.commit()
    conn.close()

folder_path = 'seg'
for subdir, _, files in os.walk(folder_path):
    if files: 
        folder_name = os.path.basename(subdir)
        db_path = f'{folder_name}_histograms.db'
        
        for file in files:
            if file.endswith(('png', 'jpg', 'jpeg')):
                image_path = os.path.join(subdir, file)
                hist = compute_histogram(image_path)
                save_histogram_to_db(db_path, image_path, hist)
