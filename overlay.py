import struct
import time
import os
import functools

from PIL import Image, ImageFont, ImageDraw


class Overlay(object):
    """
    Generate overlay on given image
    """

    # default parameters
    padding = 0.03
    font_size = 0.023
    text_brightness = 1.0
    text_fill_opacity = 0.75
    text_fill_scale = 1.06
    text_alpha = 0.75

    icon_scale = 0.1

    def __init__(self, imagepath):
        super(Overlay, self).__init__()

        self.imagepath = os.path.abspath(imagepath)
        self.source_img = Image.open(imagepath)

        self.out_img = Image.new(
            size=self.source_img.size,
            mode='RGBA',
            color=(0, 0, 0, 0)
        )

        self._date = time.strftime('%Y-%m-%d')

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

    def draw_logo(self, logo_path, drawing_point):
        logo = Image.open(logo_path)
        new_size = int(self.source_img.height * self.icon_scale)
        logo.thumbnail((new_size, new_size))

        drawing_point = self._drawing_points(drawing_point, logo.size)
        self.out_img.paste(logo, drawing_point, logo)

    @property
    def date(self):
        '''
        Holds date, only strings compatible with strftime can be assigned
        '''
        return self._date

    @date.setter
    def date(self, time_format='%Y-%m-%d'):
        self._date = time.strftime(time_format)

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

    def _drawing_points(self, corner, bbox):
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
        pad_height = int(self.height * self.padding)
        pad_width = int(self.width * self.padding)
        bbox_x, bbox_y = bbox
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


class Frame(object):
    """
    Basic class for representing frame values
    """
    def __init__(self, frame_num, offset=0, padding=4):
        """
        docstring here
            :param frame_num: frame_number (int)
            :param offset=0: offseting frames(int)
            :param padding=4: how many 0 fill on string representation
        """
        super(Frame, self).__init__()
        assert frame_num + offset > 0
        self.frame_num = frame_num
        self.offset = offset
        self.padding = padding

    def __repr__(self):
        return 'Frame({}, offset={}, padding={})'.format(
            self.frame_num, self.offset, self.padding
        )

    def __str__(self):
        return str(self.frame_num + self.offset).zfill(self.padding)

    @classmethod
    def from_dict(cls, dictionary):
        """
        Shorthand to create Frame object from dictionary
            :param dictionary: dictionary that contains frame data
        """
        keys = ('offset', 'padding')
        d = {k: v for k, v in dictionary.items() if k in keys}
        if d:
            return cls(dictionary['number'], **d)
        return cls(dictionary['number'])


class Timecode(object):
    possible_fps = (24, 25, 30, 48, 60)

    """docstring for Timecode."""
    def __init__(self, hour=0, minut=0, second=0, frame=1, fps=24):
        super(Timecode, self).__init__()

        self.hour = hour
        self.minut = minut
        self.second = second
        self.frame = frame
        self.fps = fps

    @property
    def hour(self):
        return self._hour

    @hour.setter
    def hour(self, num):
        try:
            num = int(num)
        except TypeError as e:
            raise e

        if num < 0 or num > 23:
            raise ValueError(
                'this value should be beetwen int beetwen 0 and 23')

        self._hour = num

    @property
    def minute(self):
        return self._minute

    @minute.setter
    def minute(self, num):
        try:
            num = int(num)
        except TypeError as e:
            raise e

        if num < 0 or num > 59:
            raise ValueError(
                'this value should be beetwen int beetwen 0 and 59')

        self._minute = num


    @property
    def second(self):
        return self._minute

    @second.setter
    def second(self, num):
        try:
            num = int(num)
        except TypeError as e:
            raise e

        if num < 0 or num > 59:
            raise ValueError(
                'this value should be beetwen int beetwen 0 and 59')

        self._second = num

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, num):
        try:
            num = int(num)
        except TypeError as e:
            raise e

        if num not in self.possible_fps:
            msg = 'invalid value, value must be one of {}'.format(
                ' ,'.join(str(x) for x in self.possible_fps)
            )
            raise ValueError(msg)

        self._fps = num

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, num):
        try:
            num = int(num)
        except TypeError as e:
            raise e

        if num < 0 or num > self._fps:
            msg = 'Value must be 1 and {}'.format(self.fps)
            raise ValueError(msg)

        self._frame = num

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
    temp = Timecode()
    temp.fps = 30
