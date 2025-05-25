from PIL import Image, ImageDraw
import sys

"""
linescan
Reads a raster image and tries to identify the black or white of lines in it.
If an output (text) file is given, it writes each pixel to the file.

Usage: python line-scanner.py inputfile [outputfile]

NOTE: The first line of the output file is the SIZE of the input image.
It is NOT the location of the first pixel. That data starts on line 2.
"""

# The limit, in percentage of brightness (from 0 to 1 as 0% to 100%),
# for determining "dark" pixels. This percentage represents the distance
# from the given color to pure black. 0 = only black, 0.5 = black and grays.
THRESHOLD = 0.5

RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
BLACK, WHITE     = (0, 0, 0), (255, 255, 255)

def color_dist(a, b):
	"""Calculate the distance between 2 colors."""
	if a == b: return 0

	max_dist = 441 # the distance between black and white

	r1, b1, g1 = a[:3]
	r2, b2, g2 = b[:3]

	r = (r2 - r1) ** 2
	g = (g2 - g2) ** 2
	b = (b2 - b1) ** 2
	d = (r + g + b) ** 0.5
	return d / max_dist

def find_next(pixels, size, start, reverse=False, inverted=False):
	"""Find the next (or previous) black pixel from the starting point."""
	width, height = size
	x, y = start

	index = width*y+x
	max_index = width * height - 1

	target = WHITE if inverted else BLACK

	while 0 <= index <= max_index:
		x2 = index % width
		y2 = index // width

		# skip transparent pixels
		pixel = pixels[x2, y2]
		if len(pixel) == 4 and pixel[3] == 0:
			continue

		dist = color_dist(pixel, target)
		if dist < THRESHOLD:
			return (x2, y2)

		index += -1 if reverse else 1

	return None

def flood_fill(pixels, size, start, inverted=False, fill=RED):
	"""Replace all adjacent dark/light pixels in the image."""
	width, height = size
	x, y = start

	stack = [(x, y)]
	visited = set()
	out = []

	target = WHITE if inverted else BLACK

	while stack:
		x, y = stack.pop()
		if (x, y) in visited:
			continue

		visited.add( (x, y) )
		out.append( (x, y) )

		if 0 <= x < width and 0 <= y < height:
			pixel = pixels[x, y]
			dist = color_dist(pixel, target)

			if dist < THRESHOLD:
				pixels[x, y] = fill

				neighbors = [
					(x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
					(x - 1, y    ),             (x + 1, y    ),
					(x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
				]

				for nx, ny in neighbors:
					if (nx, ny) not in visited:
						stack.append( (nx, ny) )

	return out

def main(args):
	"""Opens an image file and scans lines in it."""

	try:
		path = args[1]
		img = Image.open(path)
		print("Loading image", path)
		print(img.format, img.size, img.mode)
	except IndexError:
		print("Usage: python line-scanner.py inputfile [outputfile]")
		return
	except FileNotFoundError:
		print(f"Error: No such file '{path}'")
		return
	except OSError:
		print(f"Error: Failed to open image file '{path}'")
		return

	# Same as with open() but allows me to perform actions on the object first
	# After this block ends, the file is automatically closed.
	with img:
		mode = img.mode
		pixels = img.load()

		# Determine if we're dealing with a black or white background
		first_pixel = pixels[0, 0]
		colors = len(first_pixel)
		brightness = sum(first_pixel) / len(first_pixel)
		inverted = (brightness < 127)

		print("First pixel:", first_pixel)
		print("Brightness:", brightness)
		print("Inverted:", inverted)
		print()

		# Find first dark (or light) pixel starting from the top-left corner
		first_target = find_next(
			pixels, img.size, (0, 0), inverted=inverted
		)

		x, y = first_target
		color = "light" if inverted else "dark"
		print(f"Found {color} pixel at {first_target}: {mode} {pixels[x, y]}")

		visited = flood_fill(
			pixels, img.size, first_target, inverted=inverted, fill=BLUE
		)

		count = len(visited)
		print(f"found {count} {color} pixels")

		if len(args) >= 3:
		    path = args[2]
		    with open(path, "w") as output:
		        output.write( str(img.size) + "\n" )
		        output.write( "\n".join(map(str, visited)) )
		        output.write("\n")

		        print(f"Done. Points written to {path}")
		else:
		    print("Pass an output file to save results.")

		img.show()
		return visited

if __name__ == '__main__':
	main(sys.argv)

