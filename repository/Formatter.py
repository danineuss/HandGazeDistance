"""
This class is created to allow allow the ImageAnalyst to create the cool plot showing function which shows each pixel
value.

Inspired by: http://stackoverflow.com/questions/27704490/interactive-pixel-information-of-an-image-in-python
"""


class Formatter(object):
    def __init__(self, im):
        self.im = im

    def __call__(self, x, y):
        z = self.im.get_array()[int(y), int(x)]
        return 'x={:.01f}, y={:.01f}, z={:.01f}'.format(x, y, z)
