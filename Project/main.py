import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
import cv2

from image_processor import ImageProcessor


# main game window
class Game:

    def __init__(self):

        # create tkinter window
        self.root = tk.Tk()

        self.root.title("Spot the Difference")

        # object for image processing
        self.processor = ImageProcessor()

        # game values
        self.mistakes = 0
        self.total_found = 0

        # used for resizing images
        self.scale = 1

        self.setup_ui()

    def setup_ui(self):

        # top section for buttons
        top = tk.Frame(self.root)
        top.pack(pady=10)

        # load image button
        tk.Button(
            top,
            text="Load Image",
            command=self.load_image
        ).pack(side=tk.LEFT, padx=10)

        # reveal button
        tk.Button(
            top,
            text="Reveal",
            command=self.reveal
        ).pack(side=tk.LEFT, padx=10)

        # game info label
        self.info = tk.Label(
            self.root,
            text="Load an image to start"
        )

        self.info.pack()

        # frame for images
        frame = tk.Frame(self.root)
        frame.pack()

        # original image canvas
        self.canvas1 = tk.Canvas(
            frame,
            width=400,
            height=300,
            bg="gray"
        )

        self.canvas1.pack(side=tk.LEFT, padx=10)

        # modified image canvas
        self.canvas2 = tk.Canvas(
            frame,
            width=400,
            height=300,
            bg="gray"
        )

        self.canvas2.pack(side=tk.LEFT, padx=10)

        # detect mouse click on second image
        self.canvas2.bind("<Button-1>", self.click)

    def load_image(self):

        # open file explorer
        path = filedialog.askopenfilename()

        if not path:
            return

        # load selected image
        if not self.processor.load_image(path):

            messagebox.showerror(
                "Error",
                "Cannot load image"
            )

            return

        # generate differences
        self.processor.generate_differences()

        # reset mistakes
        self.mistakes = 0

        # display images
        self.show_images()

        self.update_info()

    def show_images(self):

        # convert images from BGR to RGB
        img1 = cv2.cvtColor(
            self.processor.original,
            cv2.COLOR_BGR2RGB
        )

        img2 = cv2.cvtColor(
            self.processor.modified,
            cv2.COLOR_BGR2RGB
        )

        # get image size
        h, w = img1.shape[:2]

        # resize image to fit window
        self.scale = 400 / w

        new_h = int(h * self.scale)

        img1 = cv2.resize(img1, (400, new_h))
        img2 = cv2.resize(img2, (400, new_h))

        # convert image for tkinter
        self.tk1 = ImageTk.PhotoImage(Image.fromarray(img1))
        self.tk2 = ImageTk.PhotoImage(Image.fromarray(img2))

        # update canvas height
        self.canvas1.config(height=new_h)
        self.canvas2.config(height=new_h)

        # display images
        self.canvas1.create_image(
            0,
            0,
            anchor="nw",
            image=self.tk1
        )

        self.canvas2.create_image(
            0,
            0,
            anchor="nw",
            image=self.tk2
        )

    def click(self, event):

        # convert click position to original image scale
        x = int(event.x / self.scale)
        y = int(event.y / self.scale)

        # check whether difference was clicked
        d = self.processor.check_click(x, y)

        if d:

            d.found = True

            self.total_found += 1

            # draw red circle
            self.draw_circle(d)

            # player wins if all found
            if self.processor.remaining() == 0:

                messagebox.showinfo(
                    "Win",
                    "You found all differences!"
                )

        else:

            self.mistakes += 1

            # end game after 3 wrong clicks
            if self.mistakes >= 3:

                messagebox.showwarning(
                    "Game Over",
                    "Too many mistakes!"
                )

        self.update_info()

    def draw_circle(self, d):

        # scale coordinates
        x = int(d.x * self.scale)
        y = int(d.y * self.scale)

        r = int(d.radius * self.scale)

        # draw circle on both images
        self.canvas1.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            outline="red",
            width=2
        )

        self.canvas2.create_oval(
            x - r,
            y - r,
            x + r,
            y + r,
            outline="red",
            width=2
        )

    def reveal(self):

        # reveal remaining differences
        for d in self.processor.differences:

            if not d.found:
                self.draw_circle(d)

    def update_info(self):

        # update game information text
        text = (
            f"Remaining: {self.processor.remaining()} | "
            f"Mistakes: {self.mistakes}/3 | "
            f"Total Found: {self.total_found}"
        )

        self.info.config(text=text)

    def run(self):

        # start tkinter loop
        self.root.mainloop()


# start game
if __name__ == "__main__":

    game = Game()

    game.run()