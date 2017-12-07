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
    text_fill_scale = 1.03
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
        self.out_img.save(filename)

    def draw_block(self, text):
        draw = ImageDraw.Draw(self.out_img)

        text_bbox_x, text_bbox_y = draw.textsize(
            text, font=self.fonts['inconsolata_regular'])

        fill_size_x = int(text_bbox_x *  self.text_fill_scale)
        fill_size_y = int(text_bbox_y *  self.text_fill_scale)

    @property
    def timecode(self):
        '''
        Holds timecode, only strings compatible with strftime can be assigned
        '''
        return self._timecode

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

    @timecode.setter
    def timecode(self, time_format='%Y-%m-%d'):
        self._timecode = time.strftime(time_format)

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
        pad_height = int(self.height * self.text_fill_scale)
        pad_width = int(self.width * self.text_fill_scale)
        bbox_x, bbox_y = text_bbox
        center = int(self.width / 2)

        bottom_y = self.height - pad_height - bbox_y
        right_start = self.width - pad_width - bbox_x
        center_start = center - int(bbox_x / 2)

        corners = {
            'up_left': (pad_width, pad_height),
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
