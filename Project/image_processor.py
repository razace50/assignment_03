import cv2
import random
import math

from alterations import (
    BlurAlteration,
    BrightnessAlteration,
    ColorShiftAlteration
)


# stores information about each difference
class Difference:

    def __init__(self, x, y, radius):

        self.x = x
        self.y = y
        self.radius = radius

        # used to track whether user found it
        self.found = False

    def is_clicked(self, px, py):

        # distance between mouse click and difference center
        dist = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)

        return dist <= self.radius + 10


# handles image processing and difference generation
class ImageProcessor:

    def __init__(self):

        self.original = None
        self.modified = None

        # list to store all differences
        self.differences = []

    def load_image(self, path):

        # read image using OpenCV
        self.original = cv2.imread(path)

        return self.original is not None

    def generate_differences(self):

        # create duplicate image
        self.modified = self.original.copy()

        # clear old differences
        self.differences = []

        h, w = self.original.shape[:2]

        count = 0

        while count < 5:

            # random size and position
            r = random.randint(40, 70)

            x = random.randint(r + 30, w - r - 30)
            y = random.randint(r + 30, h - r - 30)

            # check if circles overlap
            overlap = False

            for d in self.differences:

                dist = math.sqrt((x - d.x) ** 2 + (y - d.y) ** 2)

                if dist < (r + d.radius + 20):
                    overlap = True
                    break

            if overlap:
                continue

            # randomly choose one image effect
            choice = random.choice([
                BlurAlteration,
                BrightnessAlteration,
                ColorShiftAlteration
            ])

            # apply selected effect
            alteration = choice(x, y, r)

            self.modified = alteration.apply(self.modified)

            # save difference info
            self.differences.append(Difference(x, y, r))

            count += 1

    def check_click(self, x, y):

        # check whether user clicked on a difference
        for d in self.differences:

            if not d.found and d.is_clicked(x, y):
                return d

        return None

    def remaining(self):

        # count how many differences are left
        return sum(1 for d in self.differences if not d.found)