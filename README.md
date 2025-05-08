# ActionSampler Photo Alignment and Montages
Visually align and create montages out of your ActionSampler Photos. While intended for images taken with [Lomography's ActionSampler camera](https://microsites.lomography.com/actionsampler/), this can be used with any sequence of images.

https://github.com/user-attachments/assets/ea8469b2-03eb-4901-b367-9ab7954556af

## How To Use
> Note: installation guide [below](#install).

1. Place all your images in a target folder. Make sure files are named according to any alpha-numerical order. Name format should be in the form `basename_n`, where `basename` is the same between images of a group, and `n` is the identifier in the sequence. Standard image formats are supported (`.jpg`, `.png`, etc.).
2. Run `conda activate opencv-env`. Run `resize.py` which resizes images to a desired width. Aspect ratio is preserved. Use code editor to modify values/directories.
3. Run `conda deactivate` followed by `conda activate pygame-env`. Run `align.py` - this launches the utility for visual alignment of images. [More info below](#align.py).
4. Run `conda deactivate` and `conda activate opencv-env`. Run `montage.py`.
5. Use code editor to modify any values within scripts.

### Align.py
Below are keybindings and directions on how to use the aligment tool.
#### Keybindings
- Keys <kbd>W</kbd>, <kbd>A</kbd>, <kbd>S</kbd>, <kbd>D</kbd> for coarse image movement.
- Arrow keys for fine image movement (1px at a time).
- Keys <kbd>1</kbd>, <kbd>2</kbd>, <kbd>3</kbd> set images to 100%, 50%, 0% opacity, respectively.
- <kbd>Space</kbd> commits the current image's position and moves to the next.
- <kbd>Backspace</kbd> uncommits the previous image which can be modified once again.
#### Typical Workflow
1. Move image around with <kbd>W</kbd>, <kbd>A</kbd>, <kbd>S</kbd>, <kbd>D</kbd>.
2. Once close to the optimal position use arrow keys.
3. Check that alignment looks good by alternating between 100% and 0% opacity (keys <kbd>1</kbd> and <kbd>3</kbd>).
4. Go to the next image with <kbd>Space</kbd>.
5. If not satisfied go back with <kbd>Backspace</kbd>. Can go back any number of images.

## Install
1. Clone repository in desired local directory.
2. Create Conda environments. If not installed, Conda installation guide: https://www.anaconda.com/docs/getting-started/miniconda/install
   > Note: a single environment is entirely possible, the two environments setup is a product of lazy development.
   ```
   conda create -n pygame-env python=3.11
   conda activate pygame-env
   pip install pygame
   ```
   ```
   conda create -n opencv-env python=3.12
   conda activate opencv-env
   conda install -c conda-forge opencv
   ```
   
