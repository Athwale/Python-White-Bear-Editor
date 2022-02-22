from typing import List

import wx
import wx.lib.scrolledpanel

from Constants.Constants import Events
from Constants.Constants import Strings
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
        self._doc = None
        self._img_index = 0
        self._images: List[AsideImage] = []
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)
        self.Bind(wx.EVT_MENU, self._on_image_modify)
        self.Bind(wx.EVT_BUTTON, self._on_image_modify)

    def _on_image_modify(self, event: wx.CommandEvent):
        """
        Move image up/down one position, remove or edit them.
        :param event: Used to distinguish between up/down buttons. And contains reference to the image that is being
        moved.
        :return: None
        """
        self._img_index = self._images.index(event.GetClientData())
        # Rearrange the images in the list
        if event.GetId() == wx.ID_UP:
            if self._img_index == 0:
                return
            self._images[self._img_index], self._images[self._img_index - 1] = \
                self._images[self._img_index - 1], self._images[self._img_index]
            set_modified = True
        elif event.GetId() == wx.ID_DOWN:
            if self._img_index + 1 == len(self._images):
                return
            self._images[self._img_index], self._images[self._img_index + 1] = \
                self._images[self._img_index + 1], self._images[self._img_index]
            set_modified = True
        # Remove image from list
        elif event.GetId() == wx.ID_DELETE:
            result = wx.MessageBox(Strings.text_remove_image, Strings.status_warning, wx.YES_NO | wx.ICON_WARNING)
            if result == wx.YES:
                del self._images[self._img_index]
            set_modified = True
        else:
            # Modify image data
            edit_dialog = EditAsideImageDialog(self, self._images[self._img_index], self._doc.get_working_directory())
            edit_dialog.ShowModal()
            set_modified = edit_dialog.was_modified()
            edit_dialog.Destroy()
        self.show_images()

        # Pass the event into the main frame to change document color in the file list. Always send the event because
        # that runs spellcheck on the rest of the frame in case we learned new words, but indicate whether we made
        # any changes to set the document modified.
        color_evt = Events.SidepanelChangedEvent(self.GetId())
        if set_modified:
            color_evt.SetInt(1)
        else:
            color_evt.SetInt(0)
        wx.PostEvent(self.GetEventHandler(), color_evt)

    def load_document_images(self, doc: WhitebearDocumentArticle) -> None:
        """
        Load images from an article into the panel.
        :param doc: The document to show images from.
        :return: None
        """
        self._doc = doc
        self.clear_panel()
        self._images = self._doc.get_aside_images()
        self.show_images()

    def clear_panel(self) -> None:
        """
        Clear loaded bitmaps and free memory.
        :return: None
        """
        for child in self.GetChildren():
            child.Destroy()

    def reset(self) -> None:
        """
        Clear the panel and show nothing.
        :return: None
        """
        self._images.clear()
        self.show_images()

    def show_images(self) -> None:
        """
        Show the list of images on the panel.
        :return: None
        """
        # First clear already displayed images
        self.clear_panel()

        # Create and show new images
        for img in self._images:
            image_panel = ImagePanel(self)
            image_panel.set_image(img)
            self._sizer.Add(image_panel, 1, flag=wx.EXPAND | wx.ALIGN_LEFT)

        self.SetupScrolling(scroll_x=False, scrollIntoView=True, scrollToTop=False)
        # This makes the scrollbar space on the right disappear while the collapsible scrollbar still appears.
        self.SetScrollbar(wx.VERTICAL, 0, 0, 0)

    def update_image_backgrounds(self) -> None:
        """
        Update background color of all images based on their seo status.
        :return: None
        """
        for child in self.GetChildren():
            # The child can also be the edit dialog fi this method is run while it is open.
            if isinstance(child, ImagePanel):
                child: ImagePanel
                child.update_image()
