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
    text_fill_scale = 1.06
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

        self._timecode = time.strftime('%Y-%m-%d')

    def save(self, filename):
        """
        Saving file to given destinition, extension is taken from filename\n
            :param filename: file destinition
        """
        self.out_img.save(filename)

    def save_composed(self, filename):
        source_rgba = Image.new(size=self.source_img.size, mode='RGBA')
        source_rgba.paste(self.source_img)
        out = Image.alpha_composite(source_rgba, self.out_img)

        out.save(filename)

    def draw_text_block(self, text, drawing_point):
        draw = ImageDraw.Draw(self.out_img)

        text_size_x, text_size_y = draw.textsize(
            text, font=self.fonts['inconsolata_regular'])

        fill_size_x = int(text_size_x *  self.text_fill_scale)
        fill_size_y = int(text_size_y *  self.text_fill_scale)

        x0, y0 = self._drawing_points(
            drawing_point,
            (fill_size_x, fill_size_y)
        )

        fill_opacity = int(self.text_fill_opacity * 255)
        draw.rectangle(
            [x0, y0, x0 + fill_size_x, y0 + fill_size_y],
            fill=(0, 0, 0, fill_opacity)
        )

        diff_x, diff_y = fill_size_x - text_size_x, fill_size_y - text_size_y
        x1, y1 = x0 + int(float(diff_x) / 2), y0 + int(float(diff_y) / 2)
        draw.text(
            (x1, y1),
            text,
            fill=(255, 255, 255, 255),
            font=self.fonts['inconsolata_regular']
        )

    @property
    def timecode(self):
        '''
        Holds timecode, only strings compatible with strftime can be assigned
        '''
        return self._timecode

    @timecode.setter
    def timecode(self, time_format='%Y-%m-%d'):
        self._timecode = time.strftime(time_format)

    @property
    def width(self):
        return self.source_img.width

    @property
    def height(self):
        return self.source_img.height

    @property
    def fonts(self):
        return {
            'inconsolata_regular': ImageFont.truetype(
                'fonts/Inconsolata-Regular.ttf',
                encoding='unic',
                size=int(self.source_img.height * self.font_size)
            )
        }

    def _drawing_points(self, corner, text_bbox):
        """
        Holds drawings point for every possible block postion.

        :param corner: specify corner by name, possible inputs:
                - 'up_left'
                - 'up_center'
                - 'up_right',
                - 'bottom_left'
                - 'bottom_center'
                - 'bottom_right'

        :param text_bbox: tuple that contains width and height of text block

        :returns: (start_point_x, start_point_y)
        """
        pad_height = int(self.height * self.text_padding)
        pad_width = int(self.width * self.text_padding)
        bbox_x, bbox_y = text_bbox
        center = int(self.width / 2)

        bottom_y = self.height - pad_height - bbox_y
        right_start = self.width - pad_width - bbox_x
        center_start = center - int(bbox_x / 2)

        corners = {
            'up_left': (pad_height, pad_height),
            'up_center': (center_start, pad_height),
            'up_right': (right_start, pad_height),
            'bottom_left': (pad_width, bottom_y),
            'bottom_center': (center_start, bottom_y),
            'bootom_right': (right_start, bottom_y),
        }

        return corners[corner]


def read_dpx_image_size(filepath):
    """
    Parse width and height of dpx image base on information in header

    :param filepath: path to file
    :returns: (width, heigth)
    """
    with open(filepath) as dpx_file:
        dpx_file.seek(0)
        dpx_bytes = dpx_file.read(4)
        magic = dpx_bytes.decode(encoding='UTF-8')
        if magic != "SDPX" and magic != "XPDS":
            return None
        endianness = ">" if magic == "SDPX" else "<"

        dpx_file.seek(772)
        width = struct.unpack(endianness + 'I', dpx_file.read(4))[0]
        heigth = struct.unpack(endianness + 'I', dpx_file.read(4))[0]

    return width, heigth


def scale_bbox(bbox, percent):
    """
    Scaling proportionaly bounding box

    :param bbox: Tuple width and height of bbox.
    :param percent: Percentage scale of bbox.

    :returns: tuple of scale width and height
    """
    return tuple(int(x * percent) for x in bbox)


if __name__ == '__main__':
    imgpath = 'test_image.jpg'
    img = Overlay(imgpath)
    img.draw_text_block('some stupid text', 'up_right')
    img.save_composed('test.png')
