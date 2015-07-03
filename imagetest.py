from PIL import Image

im = Image.open('image.png')
from collections import defaultdict
by_color = defaultdict(int)
for pixel in im.getdata():
	by_color[pixel] += 1

print len(by_color),by_color