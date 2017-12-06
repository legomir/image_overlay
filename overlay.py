import struct
import time
import os

from PIL import Image, ImageFont, ImageDraw


class Overlay(object):
    """
    Generate overlay on given image
    """

    # default parameters
    text_padding = 0.03
    text_brightness = 1.0
    text_fill_opacity = 0.75
    text_alpha = 0.75

    font_size = 0.023
    help_font_size = 0.028
    outline_opacity = 0.1

    def __init__(self, imagepath):
        super(Overlay, self).__init__()
        self.imagepath = os.path.abspath(imagepath)
        self.source_img = Image.open(imagepath)
        self.out_img = Image.new(
            size=self.source_img.size,
            mode='RGBA',
            color=(0, 0, 0, 0)
        )

    def save(self, filename):
        self.out_img.save(filename)

    def draw_overlay(self):
        pass

    def draw_text(self, x, y):
        draw = ImageDraw.Draw(self.out_img)
        text_bbox = draw.textsize(
            'super text, enen larger',
            font=self.fonts['inconsolata_regular'],
        )

        container_x, container_y = scale_bbox(text_bbox, 1.05)
        start_x, start_y = int(x * 0.95), int(y * 0.95)

        draw.rectangle(
            (
                (start_x, start_y),
                (start_x + container_x, start_y + container_y)
            ),
            fill=(0, 0, 0, 90)
        )

        draw.text(
            (x, y),
            'super text, enen larger',
            font=self.fonts['inconsolata_regular'],
            fill=(255, 255, 255, 255)
        )

    @property
    def fonts(self):
        return {
            'inconsolata_regular': ImageFont.truetype(
                'fonts/Inconsolata-Regular.ttf',
                encoding='unic',
                size=int(self.source_img.height * self.font_size)
            )
        }

    @staticmethod
    def generate_timecode(time_format='%Y-%m-%d'):
        return time.strftime(time_format)


def read_dpx_image_size(filepath):
    """
    Parse width and height of dpx image base on information in header

    Args:
        filepath: path to file

    Returns:
        (width, heigth)
    """
    with open(filepath) as f:
        f.seek(0)
        b = f.read(4)
        magic = b.decode(encoding='UTF-8')
        if magic != "SDPX" and magic != "XPDS":
            return None
        endianness = ">" if magic == "SDPX" else "<"

        f.seek(772)
        width = struct.unpack(endianness + 'I', f.read(4))[0]
        heigth = struct.unpack(endianness + 'I', f.read(4))[0]

    return width, heigth


def scale_bbox(bbox, percent):
    """
    Scaling proportionaly bounding box

    Args:
        bbox: Tuple width and height of bbox
        percent: Percentage scale of bbox

    Returns:
        tuple of scale width and height
    """
    return tuple(int(x * percent) for x in bbox)


if __name__ == '__main__':
    imgpath = 'test_source.png'
    overlay = Overlay(imgpath)
    overlay.draw_text(10, 10)
    overlay.save('outimage.png')
