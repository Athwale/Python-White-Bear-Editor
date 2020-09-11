import wx

from Constants.Constants import Numbers
from Constants.Constants import Strings
from Tools.Document.AsideImage import AsideImage


class ImagePanel(wx.Panel):
    """

    """

    def __init__(self, *args, **kw):
        """
        Constructor for the image panel.
        """
        # TODO respond to left click
        super().__init__(*args, **kw)
        self._image = None

        # Create layout
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))
        self._label = wx.StaticText(self, -1, Strings.label_image)
        self._sizer.Add(self._bitmap)
        self._sizer.Add(self._label)
        self._sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))

        # Create popup context menu
        self._menu = wx.Menu()
        self._menu_item_up = wx.MenuItem(self._menu, wx.ID_UP, Strings.label_menu_up)
        self._menu_item_down = wx.MenuItem(self._menu, wx.ID_DOWN, Strings.label_menu_down)
        self._menu_item_edit = wx.MenuItem(self._menu, wx.ID_EDIT, Strings.label_menu_edit_image)
        self._menu_item_remove = wx.MenuItem(self._menu, wx.ID_DELETE, Strings.label_menu_remove)
        self._menu.Append(self._menu_item_up)
        self._menu.Append(self._menu_item_down)
        self._menu.Append(self._menu_item_edit)
        self._menu.Append(self._menu_item_remove)

        self.Bind(wx.EVT_CONTEXT_MENU, self.on_show_popup)
        self.Bind(wx.EVT_MENU, self.on_menu_click)
        self.SetSizer(self._sizer)
        self.Layout()

    def on_menu_click(self, event: wx.CommandEvent):
        """
        When the image is moved, we add the AsideImage instance into the event so that the containing panel knows
        which image is being moved.
        :param event: The CommandEvent from the button.
        :return: None
        """
        event.SetClientData(self._image)
        event.Skip()

    def on_show_popup(self, event):
        """
        Display the context pop up menu.
        :param event: Used to get menu coordinates.
        :return: None
        """
        self.PopupMenu(self._menu, self.ScreenToClient(event.GetPosition()))

    def set_image(self, image: AsideImage) -> None:
        """
        Set a new image into this panel.
        :param image: The image to set.
        :return: None
        """
        # TODO implement background color change if image has errors
        self._image = image
        self._label.SetLabelText(self._image.get_image_caption()[0])
        self._bitmap.SetBitmap(wx.Bitmap(self._image.get_image()))
        self.SetBackgroundColour(self._image.get_status_color())
        self.Layout()
