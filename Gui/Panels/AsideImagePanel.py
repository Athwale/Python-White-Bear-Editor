from typing import List

import wx
import wx.lib.scrolledpanel

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.EditAsideImageDialog import EditAsideImageDialog
from Gui.Panels.ImagePanel import ImagePanel
from Tools.Document.AsideImage import AsideImage
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle


class AsideImagePanel(wx.lib.scrolledpanel.ScrolledPanel):
    """
    This class displays a scrollable panel which contains aside images of a loaded whitebear article.
    """

    def __init__(self, parent):
        """
        Constructor for the AsideImagePanel which has special functionality
        :param parent: The main window of the editor.
        """
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent, -1)
        self._document = None
        self._images: List[AsideImage] = []
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)
        self.Bind(wx.EVT_MENU, self.on_image_modify)
        self.Bind(wx.EVT_BUTTON, self.on_image_modify)

    def on_image_modify(self, event: wx.CommandEvent):
        """
        Move image up one position.
        :param event: Used to distinguish between up/down buttons. And contains reference to the image that is being
        moved.
        :return: None
        """
        img_index = self._images.index(event.GetClientData())
        # Rearrange the images in the list
        if event.GetId() == wx.ID_UP:
            if img_index == 0:
                return
            self._images[img_index], self._images[img_index - 1] = self._images[img_index - 1], self._images[img_index]
            self._document.set_modified(True)
        elif event.GetId() == wx.ID_DOWN:
            if img_index + 1 == len(self._images):
                return
            self._images[img_index], self._images[img_index + 1] = self._images[img_index + 1], self._images[img_index]
            self._document.set_modified(True)
        # Remove image from list
        elif event.GetId() == wx.ID_DELETE:
            result = wx.MessageBox(Strings.text_remove_image, Strings.status_warning, wx.YES_NO | wx.ICON_WARNING)
            if result == wx.YES:
                del self._images[img_index]
            self._document.set_modified(True)
        else:
            # Modify image data
            edit_dialog = EditAsideImageDialog(self, self._images[img_index])
            _ = edit_dialog.ShowModal()
            edit_dialog.Destroy()
        self._show_images()
        # Pass the event into the main frame to change document color in the file list to blue.
        if self._document.is_modified():
            # Send an event to the main gui to signal document color change
            color_evt = wx.CommandEvent(wx.wxEVT_COLOUR_CHANGED, self.GetId())
            color_evt.SetEventObject(self)
            wx.PostEvent(self.GetEventHandler(), color_evt)

    def load_document_images(self, doc: WhitebearDocumentArticle) -> None:
        """
        Load images from an article into the panel.
        :param doc: The document to show images from.
        :return: None
        """
        self._document = doc
        self.clear_panel()
        self._images = self._document.get_aside_images()
        self._show_images()

    def clear_panel(self) -> None:
        """
        Clear loaded bitmaps and free memory.
        :return: None
        """
        for child in self.GetChildren():
            child.Destroy()

    def _show_images(self) -> None:
        """
        Show the list of images on the panel.
        :return: None
        """
        self.Hide()
        # First clear already displayed images
        self.clear_panel()

        # Create and show new images
        for img in self._images:
            image_panel = ImagePanel(self)
            image_panel.set_image(img)
            self._sizer.Add(image_panel, flag=wx.ALL, border=Numbers.widget_border_size)

        self.SetupScrolling(scroll_x=False, scrollIntoView=True)
        self.Layout()
        self.Show()
