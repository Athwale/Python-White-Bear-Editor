from typing import List

import wx
from PIL import Image
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError, XMLSchemaParseError, ParserError
from wx.lib.agw.supertooltip import SuperToolTip

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Exceptions.UnrecognizedFileException import UnrecognizedFileException
from Resources.Fetch import Fetch


class Tools:

    @staticmethod
    def get_warning_tip(field, title: str) -> SuperToolTip:
        """
        Create and return an instance of SuperToolTip targeted for a specific TextCtrl and set up to show SEO warnings.
        :param field: The text field for the new tip.
        :param title: The header text of the tip.
        :return: Set up SuperToolTip
        """
        tip = SuperToolTip(None, footer='   ')
        tip.SetHeader(title)
        tip.SetTarget(field)
        tip.SetTopGradientColor(Numbers.YELLOW_COLOR)
        tip.SetMiddleGradientColor(Numbers.YELLOW_COLOR)
        tip.SetBottomGradientColor(Numbers.YELLOW_COLOR)
        tip.SetTextColor(wx.BLACK)
        return tip

    @staticmethod
    def validate(html_string: str, schema: str) -> (bool, List[str]):
        """
        Validate a document against a xml schema.
        :param html_string: Html document as string.
        :param schema: The name of the schema to use.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raises UnrecognizedFileException if html parse fails.
        :raises UnrecognizedFileException if xml schema is incorrect.
        """
        errors = []
        try:
            xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path(schema)))
            xml_doc = html.fromstring(html_string)
            is_valid = xmlschema.validate(xml_doc)
        except XMLSchemaParseError as e:
            raise UnrecognizedFileException(f'{Strings.exception_schema_syntax_error}:\n{e}')
        except XMLSyntaxError as e:
            raise UnrecognizedFileException(f'{Strings.exception_html_syntax_error}:\n{e}')
        except ParserError as e:
            raise UnrecognizedFileException(f'{Strings.exception_html_syntax_error}:\n{e}')
        for error in xmlschema.error_log:
            errors.append(error.message)
        return is_valid, errors

    @staticmethod
    def create_image(text: str) -> wx.Bitmap:
        """
        Create an image containing the text.
        :param text: The text to put into the image.
        :return: The image with the text.
        """
        dc = wx.MemoryDC()
        font: wx.Font = dc.GetFont()
        font.SetPointSize(Numbers.heading_3_size)
        dc.SetFont(font)
        size = dc.GetTextExtent(text)

        bitmap = wx.Bitmap(width=size[0] + 10, height=size[1] + 10)
        dc.SelectObject(bitmap)
        dc.Clear()
        dc.SetTextForeground(wx.BLACK)

        dc.DrawText(text, 5, 5)

        return bitmap

    @staticmethod
    def set_field_background(field: wx.TextCtrl, color: wx.Colour) -> None:
        """
        Set background color for a field.
        :param field: wx.TextCtrl.
        :param color: The wx.Color to set.
        :return: None
        """
        field.SetBackgroundColour(color)
        style_carrier = wx.TextAttr()
        # Set color for the current text separately, it does not work with just background color
        field.GetStyle(0, style_carrier)
        style_carrier.SetBackgroundColour(color)
        field.SetStyle(0, len(field.GetValue()), style_carrier)

    @staticmethod
    def optimize_image(img_path: str) -> None:
        """
        Optimize and overwrite jpg and png images.
        :param img_path: Full path to the image on disk.
        :return: None
        """
        img = Image.open(img_path)
        img.save(img_path, optimize=True, quality=Numbers.image_quality)

    @staticmethod
    def inplace_rescale(image: wx.Image, target_width: int, target_height: int, border: int) -> None:
        """
        Rescale image in place to fit into a defined size. The image will retain original aspect ratio.
        :param image: Image to rescale
        :param target_width: Width of the new image.
        :param target_height: Height of the new image.
        :param border: Leave space for a border.
        :return: None
        """
        width_scale = target_width / image.GetWidth()
        height_scale = target_height / image.GetHeight()
        bounded_scale = min(width_scale, height_scale)
        width = int(image.GetWidth() * bounded_scale) - border
        height = int(image.GetHeight() * bounded_scale) - border
        width = width if width > 0 else 1
        height = height if height > 0 else 1
        image.Rescale(width, height, quality=wx.IMAGE_QUALITY_HIGH)