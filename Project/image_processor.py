import math
import random
import cv2

from alterations import (
    BlurAlteration,
    BrightnessAlteration,
    ColorShiftAlteration
)


class Difference:
    """
    Keeps track of a single difference region.
    """

    # Extra space allowed around the circle
    # so the game feels more fair to play.
    CLICK_TOLERANCE = 12

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius

        # Becomes True once player finds it
        self.found = False

    def is_clicked(self, click_x, click_y):
        """
        Check if the player clicked close enough
        to this difference.
        """

        distance = math.sqrt(
            (click_x - self.x) ** 2 +
            (click_y - self.y) ** 2
        )

        return distance <= (
            self.radius + self.CLICK_TOLERANCE
        )


class ImageProcessor:
    """
    Handles image loading and creates all
    spot-the-difference regions.
    """

    DIFFERENCE_COUNT = 5

    def __init__(self):

        self.original_image = None
        self.modified_image = None

        # Stores all generated differences
        self.differences = []

    def load_image(self, path):
        """
        Load the selected image using OpenCV.
        """

        self.original_image = cv2.imread(path)

        return self.original_image is not None

    def generate_differences(self):
        """
        Generate 5 random non-overlapping
        difference regions.
        """

        # Copy original image so edits
        # do not affect the original.
        self.modified_image = (
            self.original_image.copy()
        )

        # Remove old differences if a new
        # image is loaded.
        self.differences.clear()

        height, width = (
            self.original_image.shape[:2]
        )

        # Available alteration effects
        alteration_types = [
            BlurAlteration,
            BrightnessAlteration,
            ColorShiftAlteration
        ]

        while len(self.differences) < self.DIFFERENCE_COUNT:

            # Random circle size
            radius = random.randint(35, 60)

            # Random position
            x = random.randint(
                radius + 20,
                width - radius - 20
            )

            y = random.randint(
                radius + 20,
                height - radius - 20
            )

            # Skip if region overlaps another
            if self.overlaps_existing(x, y, radius):
                continue

            # Pick random alteration type
            alteration_class = random.choice(
                alteration_types
            )

            # Create alteration object
            alteration = alteration_class(
                x,
                y,
                radius
            )

            # Apply effect to modified image
            self.modified_image = alteration.apply(
                self.modified_image
            )

            # Store difference info
            difference = Difference(
                x,
                y,
                radius
            )

            self.differences.append(difference)

            # Save modified image automatically
            cv2.imwrite(
                "modified_output.png",
                self.modified_image
            )

    def overlaps_existing(self, x, y, radius):
        """
        Make sure difference regions
        do not overlap.
        """

        for difference in self.differences:

            distance = math.sqrt(
                (x - difference.x) ** 2 +
                (y - difference.y) ** 2
            )

            minimum_distance = (
                radius +
                difference.radius +
                25
            )

            if distance < minimum_distance:
                return True

        return False

    def check_click(self, x, y):
        """
        Check whether the player's click
        matches any remaining difference.
        """

        for difference in self.differences:

            if not difference.found:

                if difference.is_clicked(x, y):
                    return difference

        return None

    def remaining_differences(self):
        """
        Count how many differences
        are still not found.
        """

        return sum(
            1
            for difference in self.differences
            if not difference.found
        )