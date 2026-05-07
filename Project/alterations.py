import cv2
import numpy as np


# Base class for all image modifications
class Alteration:

    def __init__(self, x, y, radius):

        # position of the difference
        self.x = x
        self.y = y

        # size of the area
        self.radius = radius

    def apply(self, image):
        pass


# -----------------------------------
# Blur Difference
# -----------------------------------
class BlurAlteration(Alteration):

    def apply(self, image):

        # make a copy so original image stays unchanged
        result = image.copy()

        # create empty mask
        mask = np.zeros(result.shape[:2], dtype=np.uint8)

        # draw circular area for effect
        cv2.circle(mask, (self.x, self.y), self.radius, 255, -1)

        # apply blur
        blurred = cv2.GaussianBlur(result, (51, 51), 0)

        # copy blurred part only inside the circle
        result[mask == 255] = blurred[mask == 255]

        return result


# -----------------------------------
# Brightness Difference
# -----------------------------------
class BrightnessAlteration(Alteration):

    def apply(self, image):

        # duplicate image
        result = image.copy()

        # create circular mask
        mask = np.zeros(result.shape[:2], dtype=np.uint8)

        cv2.circle(mask, (self.x, self.y), self.radius, 255, -1)

        # increase brightness
        bright = cv2.convertScaleAbs(result, alpha=1.5, beta=80)

        # replace selected area only
        result[mask == 255] = bright[mask == 255]

        return result


# -----------------------------------
# Color Shift Difference
# -----------------------------------
class ColorShiftAlteration(Alteration):

    def apply(self, image):

        # copy original image
        result = image.copy()

        # make mask
        mask = np.zeros(result.shape[:2], dtype=np.uint8)

        cv2.circle(mask, (self.x, self.y), self.radius, 255, -1)

        # convert image into HSV
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

        # shift colors
        hsv[:, :, 0] = (hsv[:, :, 0] + 90) % 180

        # convert back to BGR
        shifted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # apply modified region only
        result[mask == 255] = shifted[mask == 255]

        return result