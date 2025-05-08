# from align import WIDTH_BG, HEIGHT_BG
import csv
import os
import subprocess
import time

import cv2
import numpy as np


WIDTH_BG = 1080
HEIGHT_BG = 1350
STACK_EFFECT = True  # previous images are kept in background
REVERSE_EFFECT = True  # clip reverses once end reached
AUDIO = False

def blit(image, background, pos):
    x_0, y_0 = pos
    h, w, _ = image.shape
    x_1 = x_0 + w
    y_1 = y_0 + h
    background[y_0:y_1, x_0:x_1, ::] = image
    return background

def constrain(image, x_max, x_min, y_max, y_min, width, height):
    image[::, 0:x_max, ::] *= 0
    image[::, int(width-x_min):WIDTH_BG, ::] *= 0
    image[0:y_max, ::, ::] *= 0
    image[y_min+height:HEIGHT_BG, ::, ::] *= 0
    return image

def positions_from_csv(filename):
    with open(filename, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        data = [row for row in reader]

    positions = []
    x_min = y_min = 1e6
    x_max = y_max = -1
    for datum in data:
        x = int(datum[0])
        y = int(datum[1])
        x_min = x if x < x_min else x_min
        x_max = x if x > x_max else x_max
        y_min = y if y < y_min else y_min
        y_max = y if y > y_max else y_max
        positions.append((x, y))
    
    return positions, (x_max, x_min, y_max, y_min)

input_fps = 5
output_fps = 30
frame_regex = "%03d.jpg"
codec = "libx264"

images_dir = "images/resized"
frames_dir = "frames"
os.makedirs(frames_dir, exist_ok=True)
frame_name = os.path.join(frames_dir, frame_regex)

images = sorted(os.listdir(images_dir))
positions, (x_max, x_min, y_max, y_min) = positions_from_csv("positions.csv")
assert len(images) == len(positions), f"{len(images)=} != {len(positions)=}"

bg = np.zeros((HEIGHT_BG, WIDTH_BG, 3), dtype=np.uint8)
for idx, (file, position) in enumerate(zip(images, positions)):
    ext = os.path.splitext(file)[-1]
    file_name = f"{idx:03}" + ext.lower()
    src = os.path.join(images_dir, file)
    dst = os.path.join(frames_dir, file_name)

    img = cv2.imread(src)
    h, w, _ = img.shape

    frame = blit(img, bg, pos=position)
    if STACK_EFFECT:
        bg = frame
    else:
        frame = constrain(frame, x_max, x_min, y_max, y_min, w, h)
        bg = np.zeros((HEIGHT_BG, WIDTH_BG, 3), dtype=np.uint8)

    cv2.imwrite(dst, frame)

# frames to video
timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
output_file = os.path.join("outputs", f"output_{timestamp}.mp4")
cmd = (
    "ffmpeg",
    "-framerate", str(input_fps),
    "-i", frame_name,
    "-c:v", codec,
    "-r", str(output_fps),
    "-pix_fmt", "yuv420p",
    output_file
)
subprocess.run(cmd)

if REVERSE_EFFECT:
    # reverse video
    output_file_reverse = os.path.join("outputs", f"output_{timestamp}_reverse.mp4")
    cmd = (
        "ffmpeg",
        "-i", output_file,
        "-vf", "reverse",
        output_file_reverse
    )
    subprocess.run(cmd)

    # join clips
    output_file_joined = os.path.join("outputs", f"output_{timestamp}_joined.mp4")
    with open("outputs/order.txt", "w") as txt_file:
        txt_file.write(f"file '{os.path.split(output_file)[-1]}'\n")
        txt_file.write(f"file '{os.path.split(output_file_reverse)[-1]}'")
    cmd = (
        "ffmpeg",
        "-f", "concat",
        "-i", "outputs/order.txt",
        "-c", "copy",
        output_file_joined
    )
    subprocess.run(cmd)

# add audio
if AUDIO:
    cmd = (
        "ffmpeg",
        "-i", "outputs/output.mp4",
        "-i", "assets/audio.mp3",
        "-c", "copy",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        os.path.join("outputs", f"output_w_sound_{timestamp}.mp4")
    )
    subprocess.run(cmd)