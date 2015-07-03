from PIL import Image
from collections import defaultdict

im = Image.open('test.png')
by_color = defaultdict(int)
for pixel in im.getdata():
	by_color[pixel] += 1

print len(by_color)
