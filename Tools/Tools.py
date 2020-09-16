import wx
from wx.lib.agw.supertooltip import SuperToolTip

from Constants.Constants import Numbers


class Tools:

    @staticmethod
    def get_warning_tip(field: wx.TextCtrl, title: str) -> SuperToolTip:
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
