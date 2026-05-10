import cv2
import numpy as np


class Alteration:
    """
    Base class for all image alterations.
    """

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

    def create_mask(self, image_shape):
        """Create circular mask for alteration region."""

        mask = np.zeros(image_shape[:2], dtype=np.uint8)

        cv2.circle(
            mask,
            (self.x, self.y),
            self.radius,
            255,
            -1
        )

        return mask

    def apply(self, image):
        raise NotImplementedError


class BlurAlteration(Alteration):
    """Apply blur effect."""

    def apply(self, image):
        result = image.copy()

        mask = self.create_mask(result.shape)

        blurred = cv2.GaussianBlur(result, (81, 81), 0)

        result[mask == 255] = blurred[mask == 255]

        return result


class BrightnessAlteration(Alteration):
    """Increase brightness in selected region."""

    def apply(self, image):
        result = image.copy()

        mask = self.create_mask(result.shape)

        brighter = cv2.convertScaleAbs(
            result,
            alpha=1.6,
            beta=90
        )

        result[mask == 255] = brighter[mask == 255]

        return result


class ColorShiftAlteration(Alteration):
    """Shift image colors in selected region."""

    def apply(self, image):
        result = image.copy()

        mask = self.create_mask(result.shape)

        hsv_image = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)

        hsv_image[:, :, 0] = (hsv_image[:, :, 0] + 90) % 180

        shifted = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

        result[mask == 255] = shifted[mask == 255]

        return result
