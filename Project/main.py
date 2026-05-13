import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
import cv2

from image_processor import ImageProcessor


class SpotDifferenceGame:
    """
    This class basically runs the whole game window and handles all the GUI stuff.
    """

    MAX_MISTAKES = 3
    DISPLAY_WIDTH = 500

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Spot the Difference")

        self.processor = ImageProcessor()

        self.scale = 1.0
        self.game_over = False

        self.setup_variables()
        self.setup_ui()

    def setup_variables(self):
        """Just resetting everything back to zero for a new game."""

        self.found_count = 0
        self.mistakes = 0

    def setup_ui(self):
        """Creates all buttons, labels, and image display areas."""

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        load_button = tk.Button(
            top_frame,
            text="Load Image",
            width=15,
            command=self.load_image
        )
        load_button.pack(side=tk.LEFT, padx=10)

        reveal_button = tk.Button(
            top_frame,
            text="Reveal Remaining",
            width=15,
            command=self.reveal_remaining
        )
        reveal_button.pack(side=tk.LEFT, padx=10)

        self.info_label = tk.Label(
            self.root,
            text="Load an image to start the game",
            font=("Arial", 11)
        )
        self.info_label.pack(pady=5)

        image_frame = tk.Frame(self.root)
        image_frame.pack(padx=10, pady=10)

        self.original_canvas = tk.Canvas(
            image_frame,
            width=self.DISPLAY_WIDTH,
            height=400,
            bg="lightgray",
            cursor="target"
        )
        self.original_canvas.pack(side=tk.LEFT, padx=10)

        self.modified_canvas = tk.Canvas(
            image_frame,
            width=self.DISPLAY_WIDTH,
            height=400,
            bg="lightgray"
        )
        self.modified_canvas.pack(side=tk.LEFT, padx=10)

        self.modified_canvas.bind("<Button-1>", self.handle_click)

    def load_image(self):
        """Lets the user pick an image file from their computer."""

        file_path = filedialog.askopenfilename(
            title="choose an Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp")]
        )

        if not file_path:
            return

        success = self.processor.load_image(file_path)

        if not success:
            messagebox.showerror(
                "Error",
                "Unable to load image file."
            )
            return

        self.processor.generate_differences()

        self.reset_round()
        self.display_images()
        self.update_status()

    def reset_round(self):
        """Clears everything so the game can restart properly."""

        self.setup_variables()

        self.game_over = False

        self.original_canvas.delete("all")
        self.modified_canvas.delete("all")

    def display_images(self):
        """Shows both images side by side and makes sure they fit properly."""

        original_rgb = cv2.cvtColor(
            self.processor.original_image,
            cv2.COLOR_BGR2RGB
        )

        modified_rgb = cv2.cvtColor(
            self.processor.modified_image,
            cv2.COLOR_BGR2RGB
        )

        height, width = original_rgb.shape[:2]

        self.scale = self.DISPLAY_WIDTH / width

        new_height = int(height * self.scale)

        resized_original = cv2.resize(
    original_rgb,
    (self.DISPLAY_WIDTH, new_height),
    interpolation=cv2.INTER_AREA
)

        resized_modified = cv2.resize(
            modified_rgb,
            (self.DISPLAY_WIDTH, new_height)
        )

        self.tk_original = ImageTk.PhotoImage(
            Image.fromarray(resized_original)
        )

        self.tk_modified = ImageTk.PhotoImage(
            Image.fromarray(resized_modified)
        )

        self.original_canvas.config(height=new_height)
        self.modified_canvas.config(height=new_height)

        self.original_canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.tk_original
        )

        self.modified_canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.tk_modified
        )

    def handle_click(self, event):
        """Manage what happens when the player clicks on the image."""

        if self.game_over:
            return

        image_x = int(event.x / self.scale)
        image_y = int(event.y / self.scale)

        difference = self.processor.check_click(image_x, image_y)

        if difference and not difference.found:
            difference.found = True
            self.found_count += 1




            self.draw_marker(difference, "red")

            if self.processor.remaining_differences() == 0:
                self.update_status()

                messagebox.showinfo(
                    "Congratulations",
                    f"You found all {self.total_differences} differences!"
                )

                self.game_over = True
                return

        else:
            self.mistakes += 1

            if self.mistakes >= self.MAX_MISTAKES:
                self.game_over = True

                messagebox.showwarning(
                    "Game Over",
                    "You reached 3 mistakes."
                )

        self.update_status()

    def draw_marker(self, difference, color):
        """Draws a circle around the spot where a difference is found."""

        x = int(difference.x * self.scale)
        y = int(difference.y * self.scale)
        radius = int(difference.radius * self.scale)

        for canvas in [self.original_canvas, self.modified_canvas]:
            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                outline=color,
                width=5
            )

    def reveal_remaining(self):
        """Shows all the differences that are still not found."""

        for difference in self.processor.differences:
            if not difference.found:
                difference.found = True
                self.draw_marker(difference, "blue")

        self.update_status(force_zero=True)

    def update_status(self, force_zero=False):
        """Updates the text showing how many differences are left."""

        if force_zero:
            remaining = 0
        else:
            remaining = self.processor.remaining_differences()

        self.info_label.config(
            text=(
                f"Found: {self.found_count}/5    "
                f"Remaining: {remaining}    "
                f"Mistakes: {self.mistakes}/3"
            )
        )

    def run(self):
        """Starts the game loop (keeps the window running)."""

        self.root.mainloop()


if __name__ == "__main__":
    game = SpotDifferenceGame()
    game.run()
