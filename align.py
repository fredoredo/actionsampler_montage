import csv
import os
import sys

import numpy as np
import pygame as pg


SHOW_ALL = False
WIDTH_BG = 1080  # background width should be > image width
HEIGHT_BG = 1350  # background height should be > image height
# X_OFFSET = 30
# Y_OFFSET = -20


class ImageObject:
    def __init__(self, image: pg.Rect, position: tuple):
        self.image = image
        self.width = image.get_rect().width
        self.height = image.get_rect().height
        self.pos = image.get_rect().move(position[0], position[1])

    def move(self, pixels=1, up=False, down=False, left=False, right=False):
        if right:
            self.pos.right += pixels  # TODO: change to left
        if left:
            self.pos.right -= pixels
        if down:
            self.pos.top += pixels
        if up:
            self.pos.top -= pixels
        if self.pos.top > HEIGHT_BG - self.height:
            self.pos.top = HEIGHT_BG - self.height
        if self.pos.top < 0:
            self.pos.top = 0
        if self.pos.left > WIDTH_BG - self.width:
            self.pos.left = WIDTH_BG - self.width
        if self.pos.left < 0:
            self.pos.left = 0
    
    def set_alpha(self, setting: int = 1):
        """
        sets alpha/transparency/opacity of image surface
        1 = 100% opacity
        2 = 50% opacity
        3 = 0% opacity
        """
        assert isinstance(setting, int)
        if setting == 1:
            self.image.set_alpha(255)
        elif setting == 2:
            self.image.set_alpha(127)
        elif setting == 3:
            self.image.set_alpha(0)
        else:
            raise ValueError


class ImageGroup:
    def __init__(self, images: list | None = None):
        if images:
            self.images = images
        else:
            self.images = []
        self.idx = 0
    
    def append(self, image: ImageObject):
        self.images.append(image)
    
    def move(self, pixels: int = 1, up=False, down=False, left=False, right=False):
        """
        move all images in group by equal amount
        """
        dir_args = {
            "up": up,
            "down": down,
            "left": left,
            "right": right
        }
        for image in self.images:
            image.move(pixels, **dir_args)
    
    def get_current(self):
        return self.images[self.idx]

    def next(self):
        if self.idx < len(self.images) - 1:
            self.images[self.idx].set_alpha(1)  # set opacity 100%
            self.idx += 1
            self.images[self.idx].set_alpha(2)  # set opacity 50%
            return self.images[self.idx]
        else:
            self.images[self.idx].set_alpha(1)
            return False
    
    def previous(self):
        if self.idx > 0:
            self.idx -= 1
            self.images[self.idx].set_alpha(2)  # set opacity 50%
            return self.images[self.idx]
        else:
            return False
    
    def show(self, screen):
        """shows all images up to current (included)"""
        for image in self.images[:self.idx+1]:
            screen.blit(image.image, image.pos)
    
    def show_all(self, surface):
        """shows all images"""
        for image in self.images:
            surface.blit(image.image, image.pos)
        
    def clear(self, screen, background):
        for image in self.images[:self.idx+1]:
            screen.blit(background, image.pos, image.pos)
    
    def get_positions(self):
        return [image.pos for image in self.images]


def make_black_background(shape: tuple):
    background = np.zeros(shape, dtype=np.uint8)
    background = pg.surfarray.make_surface(background)
    return background

def get_basename(file_path, sep = "_"):
    _, base_name = os.path.split(file_path)
    base_name, _ = os.path.splitext(base_name)
    base_name, _ = base_name.split(sep)
    return base_name

def load_image(file_path, offsets: tuple = (0, 0), position: tuple | None = None):
    img = pg.image.load(file_path).convert()
    width = img.get_rect().width
    height = img.get_rect().height
    x_off, y_off = offsets
    if position:
        x, y = position
        x += x_off
        y += y_off
    else:
        x = (WIDTH_BG // 2) - (width // 2) + x_off
        y = (HEIGHT_BG // 2) - (height // 2) + y_off
    return ImageObject(img, (x, y))

def load_all_images(image_paths: list | tuple, offsets: tuple = (0,0), positions_file: str | None = None):
    positions = []
    if positions_file:
        # TODO: replace lines below with "positions_from_csv()" from montage.py
        assert ".csv" in positions_file, f"{positions_file} is not a CSV file"
        with open(positions_file, "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            data = [row for row in reader]
        for datum in data:
            x = int(datum[0])
            y = int(datum[1])
            positions.append((x, y))

    grouped_images = []
    current_basename = None
    for idx, image_path in enumerate(image_paths):
        basename = get_basename(image_path)
        if basename != current_basename:
            current_basename = basename
            group = ImageGroup()
            grouped_images.append(group)
            if positions_file:
                group.append(load_image(image_path, offsets, positions[idx]))
            else:
                group.append(load_image(image_path, offsets))
        else:
            if positions_file:
                group.append(load_image(image_path, offsets, positions[idx]))
            else:
                group.append(load_image(image_path, offsets))
    return grouped_images

imgs_dir = "images/resized"
# positions_file = "positions.csv"
positions_file = None
imgs_paths = sorted(os.listdir(imgs_dir))
imgs_paths = [os.path.join(imgs_dir, filename) for filename in imgs_paths]

screen = pg.display.set_mode((WIDTH_BG, HEIGHT_BG))
clock = pg.time.Clock()
bg_shape = (HEIGHT_BG, WIDTH_BG, 3)
background = make_black_background(bg_shape)
screen.blit(background, (0, 0))

# load images into groups
groups = load_all_images(imgs_paths, positions_file=positions_file)
idx_group = 0
img = groups[idx_group].get_current()

running = True
while running:
    groups[idx_group].clear(screen, background)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.KEYUP:
            # next image
            if event.key == pg.K_SPACE:
                img = groups[idx_group].next()
                if not img:  # handle next group/end of groups
                    if idx_group == len(groups) - 1:
                        running = False
                        continue
                    idx_group += 1
                    img = groups[idx_group].get_current()
                if SHOW_ALL:
                    background = make_black_background(bg_shape)
                    for group in groups[:idx_group]:
                        group.show_all(background)
                    screen.blit(background, (0,0))
                    # groups[idx_group].show_all_previous(background)

            # previous image
            if event.key == pg.K_BACKSPACE:
                img = groups[idx_group].previous()
                if not img:
                    if idx_group > 0:
                        idx_group -= 1
                    img = groups[idx_group].get_current()
                if SHOW_ALL:
                    background = make_black_background(bg_shape)
                    for group in groups[:idx_group]:
                        group.show_all(background)
                    screen.blit(background, (0,0))
                    # groups[idx_group].show_all_previous(background)     
            # precise movement (once per key press)
            if event.key == pg.K_UP:
                img.move(up=True)
            if event.key == pg.K_DOWN:
                img.move(down=True)
            if event.key == pg.K_LEFT:
                img.move(left=True)
            if event.key == pg.K_RIGHT:
                img.move(right=True)
            # transperency control
            if event.key == pg.K_1:
                img.set_alpha(1)
            if event.key == pg.K_2:
                img.set_alpha(2)
            if event.key == pg.K_3:
                img.set_alpha(3)
        
    # faster less precise movement
    keys = pg.key.get_pressed()
    # move group
    if keys[pg.K_LCTRL] or keys[pg.K_RCTRL]:
        if keys[pg.K_w]:
            groups[idx_group].move(pixels=5, up=True)
        if keys[pg.K_a]:
            groups[idx_group].move(pixels=5, left=True)
        if keys[pg.K_d]:
            groups[idx_group].move(pixels=5, right=True)
        if keys[pg.K_s]:
            groups[idx_group].move(pixels=5, down=True)
    else:
        if keys[pg.K_w]:
            img.move(pixels=5, up=True)
        if keys[pg.K_a]:
            img.move(pixels=5, left=True)
        if keys[pg.K_d]:
            img.move(pixels=5, right=True)
        if keys[pg.K_s]:
            img.move(pixels=5, down=True)

    groups[idx_group].show(screen)
    pg.display.update()
    clock.tick(20)  # fps

positions = []
for group in groups:
    for image in group.images:
        positions.append((image.pos.left, image.pos.top))

# NOTE: the following overwrites the target csv file
with open("positions.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerows(positions)
