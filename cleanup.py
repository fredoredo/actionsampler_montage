import os
import shutil
import cv2

new_height = 1080

original_images_dir = "images/original"
images = sorted(os.listdir(original_images_dir))

renamed_images_dir = "renamed"
os.makedirs(renamed_images_dir, exist_ok=True)

for idx, file in enumerate(images):
    ext = os.path.splitext(file)[-1]
    file_name = f"{idx:03}" + ext.lower()
    src = os.path.join(original_images_dir, file)
    dst = os.path.join(renamed_images_dir, file_name)

    img = cv2.imread(src)
    h, w, _ = img.shape
    ratio = w / h
    height = int((new_height // 2) * 2)
    width = height * ratio
    width = int((width // 2) * 2)
    
    img = cv2.resize(img, (width, height), cv2.INTER_AREA)
    
    cv2.imwrite(dst, img)