import os
import cv2

WIDTH = int(0.9 * 1080)

src_dir = "images/original"
dst_dir = "images/resized"

for filename in os.listdir(src_dir):
    img_path = os.path.join(src_dir, filename)
    img = cv2.imread(img_path)

    h_old, w_old, _ = img.shape
    ratio = w_old / h_old
    w = WIDTH
    h = int(w / ratio)

    img = cv2.resize(img, (w, h), cv2.INTER_AREA)

    cv2.imwrite(os.path.join(dst_dir, filename), img)