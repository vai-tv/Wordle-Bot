import cv2
import numpy as np
import time

import pyautogui
import pytesseract

from pynput.keyboard import Controller, Key

from entropy import WORDS, next_guess, update_colours

def screenshot_wordle():
    """
    Takes a screenshot of the Wordle game area.
    Returns a PIL Image object.
    """
    # Define the region to capture (left, top, width, height)
    region = (960, 400, 360, 430)
    screenshot = pyautogui.screenshot(region=region)
    return screenshot

def extract_wordle_grid(image):
    """
    Extracts Wordle letters using OCR.
    """

    config = (
        "--oem 3 "
        "--psm 6 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )

    image = image.convert("L") # PIL -> grayscale
    image = image.resize((image.width * 2, image.height * 2)) # Upscale for better OCR
    np_img = np.array(image, dtype=np.uint8) # PIL -> NumPy

    _, np_img = cv2.threshold(
        np_img, 175, 255, cv2.THRESH_BINARY
    )

    # Comment this out unless OCR actually fails
    kernel = np.ones((1, 1), np.uint8)
    np_img = cv2.morphologyEx(
        np_img, cv2.MORPH_CLOSE, kernel, iterations=3
    )

    # save image
    # cv2.imwrite("debug_ocr.png", np_img)

    # OCR
    text = pytesseract.image_to_string(np_img, config=config)

    # Process the text to form the grid
    grid = []
    for line in text.split('\n'):
        row = [char for char in line if char.isalpha()]
        if row:
            grid.append(row)
    
    return grid

def get_colours(grid, image):
    """
    Analyzes the screenshot to determine the colours of the letters in the Wordle grid.
    Returns a list of lists representing the colours (e.g., 'green', 'yellow', 'gray').
    """

    pixels = []
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            x = 20 + col * 70
            y = 20 + row * 70
            pixel = image.getpixel((x, y))
            pixels.append(pixel[:-1])  # Ignore alpha channel

    # Determine the colour of each letter
    colours = []
    for pixel in pixels:
        # Estimate the colour based on the pixel value
        avg = sum(pixel) / 3
        if avg < 75:  # dark
            colours.append('gray')
        else:  # light
            colours.append('green' if pixel[1] > pixel[0] and pixel[1] > pixel[2] else 'yellow')

    # Reshape the colours list to match the grid
    colours = [colours[i:i+len(grid[0])] for i in range(0, len(colours), len(grid[0]))]
    return colours

def letters_colours_to_gxy(grid, colours) -> tuple[list[tuple[str, int]], list[tuple[str, int]], list[tuple[str, int]]]:
    """
    Converts grid letters and their corresponding colours to a tuple of lists of tuples.
    Each tuple is (letter, pos) where pos is indexed from 0.
    """

    green = []
    yellow = []
    gray = []
    
    for row_idx, row in enumerate(grid):
        for col_idx, letter in enumerate(row):
            letter = letter.lower()
            colour = colours[row_idx][col_idx]
            if colour == 'green':
                green.append((letter, col_idx))
            elif colour == 'yellow':
                yellow.append((letter, col_idx))
            else:
                gray.append((letter, col_idx))
    
    return (green, yellow, gray)

def main():

    keyboard = Controller()

    while True:

        possible_words = WORDS.copy()
        green = {}
        yellow = {}
        gray = set()
        min_required = {}

        grid = []

        # screenshot = screenshot_wordle()
        # grid = extract_wordle_grid(screenshot)
        # print("Existing letters:", grid)

        # if grid:
        #     colours = get_colours(grid, screenshot)
        #     new_green, new_yellow, new_gray = letters_colours_to_gxy(grid, colours)
        #     green, yellow, gray, min_required = update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required)


        while True:
            guess, ent, possible_words = next_guess(possible_words, green, yellow, gray, min_required=min_required, show_progress=True)
            print(f"Next guess: {guess} (Entropy: {ent:.4f}, Possible words left: {len(possible_words)})\n")

            # send guess to Wordle
            keyboard.type(guess)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            time.sleep(3)

            # update colours and grid
            grid.append([char.upper() for char in guess])
            screenshot = screenshot_wordle()
            colours = get_colours(grid, screenshot)
            new_green, new_yellow, new_gray = letters_colours_to_gxy(grid, colours)
            green, yellow, gray, min_required = update_colours(new_green, new_yellow, new_gray, green, yellow, gray, min_required)

            if len(possible_words) == 1:
                time.sleep(2)
                pyautogui.click(1000, 850)
                break


if __name__ == '__main__':
    main()