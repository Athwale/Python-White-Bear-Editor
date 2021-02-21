from typing import List

import wx
from wx.lib.agw.supertooltip import SuperToolTip

from Constants.Constants import Numbers
from lxml import etree
from lxml import html
from lxml.etree import XMLSyntaxError

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
        Validate a document against an xml schema.
        :param html_string: Html document as string.
        :param schema: The name of the schema to use.
        :return: Tuple of boolean validation result and optional list of error messages.
        :raise UnrecognizedFileException if html parse fails.
        """
        errors = []
        try:
            xmlschema = etree.XMLSchema(etree.parse(Fetch.get_resource_path(schema)))
            xml_doc = html.fromstring(html_string)
            is_valid = xmlschema.validate(xml_doc)
        except XMLSyntaxError as e:
            raise UnrecognizedFileException(Strings.exception_html_syntax_error + '\n' + str(e))
        for error in xmlschema.error_log:
            errors.append(error.message)
        return is_valid, errors
