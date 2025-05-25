from PIL import Image, ImageTk
import tkinter as tk
import sys
import os.path

import linescan

"""
drawpoints
Render an animation that follows the given path of pixels, specified by
the input file. If an image file is given instead, scans lines on the image.
"""

# The number of pixels to draw per frame
COUNT = 30

def main(args):
	if len(args) < 2:
		print("Usage: python drawpoints.py imagefile|pointsfile")
		return

	file_path = args[1]
	if os.path.isfile(file_path):
		print("Reading data from", file_path)
	else:
		print(f"Error: No such file '{path}'")
		return

	try:
		# If possible, read data from an image file using linescan
		image = Image.open(file_path)

		print("Image file provided. Running linescan...\n")
		points = iter( linescan.main(["linescan", file_path]) )
	except OSError:
		# If that fails, read data from a text file
		image = None

		points_file = open(file_path, "r")
		points = map(lambda p: eval(p.rstrip()), points_file)

	RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
	BLACK, WHITE = (0, 0, 0), (255, 255, 255)

	# Create a window to host the animation
	root = tk.Tk()
	root.title("Line Animation")

	# The first line of output from linescan is the size of the input image
	size = next(points) if image is None else image.size

	# Create a blank background to draw the points onto
	white_image = Image.new("RGB", size, "white")
	tk_image = ImageTk.PhotoImage(white_image)

	label = tk.Label(root, image=tk_image)
	label.pack()

	def move():
		for _ in range(COUNT):
			point = next(points, None)

			if point is not None:
				white_image.putpixel(point, RED)
			else:
				print("Done")
				return

		tk_image.paste(white_image)
		root.after(30, move)

	move()
	root.mainloop()

if __name__ == '__main__':
	main(sys.argv)
