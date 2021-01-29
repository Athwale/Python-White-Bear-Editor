import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.WhitebearDocument import WhitebearDocument
from Tools.Tools import Tools


class AddImageDialog(wx.Dialog):

    def __init__(self, parent, doc: WhitebearDocument):
        """
        Display a dialog with information about the image where the user can edit it.
        :param parent: Parent frame.
        :param doc: The currently opened document.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_add_image,
                           size=(Numbers.add_image_dialog_width, Numbers.edit_text_image_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.information_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_path = None
        self._image_name = None
        self._doc = doc

        # Disk locations
        self.original_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_original_path = wx.StaticText(self, -1, Strings.label_image_original_path + ': ')
        self.content_image_original_path = wx.StaticText(self, -1, Strings.label_none)
        self.original_disk_location_sub_sizer.Add(self.label_image_original_path,
                                                  flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.original_disk_location_sub_sizer.Add((15, -1))
        self.original_disk_location_sub_sizer.Add(self.content_image_original_path,
                                                  flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.original_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        self.full_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_full_path = wx.StaticText(self, -1, Strings.label_image_path + ': ')
        self.content_image_full_path = wx.StaticText(self, -1, Strings.label_none)
        self.full_disk_location_sub_sizer.Add(self.label_image_full_path, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.full_disk_location_sub_sizer.Add(self.content_image_full_path,
                                              flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.full_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        self.thumb_disk_location_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_image_thumbnail_path + ': ')
        self.content_image_thumbnail_path = wx.StaticText(self, -1, Strings.label_none)
        self.thumb_disk_location_sub_sizer.Add(self.label_image_thumbnail_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.thumb_disk_location_sub_sizer.Add(self.content_image_thumbnail_path,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.thumb_disk_location_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Original size
        self.image_original_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_original_size = wx.StaticText(self, -1, Strings.label_original_size + ': ')
        self.content_image_original_size = wx.StaticText(self, -1, Strings.label_none)
        self.image_original_size_sub_sizer.Add(self.label_image_original_size,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.image_original_size_sub_sizer.Add((16, -1))
        self.image_original_size_sub_sizer.Add(self.content_image_original_size,
                                               flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.image_original_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Thumbnail size
        self.image_thumbnail_size_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_thumbnail_size + ': ')
        self.content_image_thumbnail_size = wx.StaticText(self, -1, Strings.label_none)
        self.image_thumbnail_size_sub_sizer.Add(self.label_image_thumbnail_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.image_thumbnail_size_sub_sizer.Add(self.content_image_thumbnail_size,
                                                flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.information_sizer.Add(self.image_thumbnail_size_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                   border=Numbers.widget_border_size)

        # Image name sub sizer
        self.name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_image_name = wx.StaticText(self, -1, Strings.label_name + ': ')
        self.field_image_link_name = wx.TextCtrl(self, -1)
        self.name_sub_sizer.Add(self.label_image_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.name_sub_sizer.Add((5, -1))
        self.name_sub_sizer.Add(self.field_image_link_name, proportion=1)
        self.information_sizer.Add(self.name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        # TODO this, not empty, no /
        self.field_image_link_title_tip = Tools.get_warning_tip(self.field_image_link_name,
                                                                Strings.label_article_image_link_title)

        # Image preview
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        placeholder_image: wx.Image = wx.Image(Numbers.main_image_width, Numbers.main_image_height)
        placeholder_image.Replace(0, 0, 0, 245, 255, 255)
        self._bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(placeholder_image))
        self.image_sizer.Add(self._bitmap, flag=wx.ALL, border=1)

        # Adjust dialog height to fit entire image.
        #if self._image.get_thumbnail_size()[1] > self.image_sizer.GetSize()[1]:
        #    self.SetSize(self.GetSize()[0], self._image.get_thumbnail_size()[1] + 120)

        # Buttons
        self.button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self.ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self.browse_button = wx.Button(self, wx.ID_OPEN, Strings.button_browse)
        self.ok_button.SetDefault()
        grouping_sizer.Add(self.ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self.cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self.browse_button)
        self.button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self.vertical_sizer.Add(self.information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                border=Numbers.widget_border_size)
        self.horizontal_sizer.Add(self.vertical_sizer, 1)
        self.horizontal_sizer.Add(self.image_sizer, flag=wx.TOP | wx.RIGHT, border=Numbers.widget_border_size)
        self.main_vertical_sizer.Add(self.horizontal_sizer, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                     border=Numbers.widget_border_size)
        self.SetSizer(self.main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.browse_button)

        # Ask for an image.
        self._image_path, self._image_name = self._ask_for_image()
        self._convert_image()

    def _ask_for_image(self) -> (str, str):
        """
        Show a file picker dialog to get an image from the user.
        :return: (file path, file name)
        """
        with wx.FileDialog(self, Strings.label_select_image, Strings.home_directory, wildcard=Strings.image_extensions,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                return dlg.GetPath(), dlg.GetFilename()

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_OPEN:
            self._image_path, self._image_name = self._ask_for_image()
            self._convert_image()
        event.Skip()

    def _convert_image(self) -> None:
        """
        Copy the selected image into the right place and make a thumbnail.
        :return: None
        """
        print(self._image_path)
        print(self._image_name)
        print(self._doc.get_working_directory())


    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui along with field values and errors.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self.field_image_link_name: (self._image.get_link_title(), self.field_image_link_title_tip),
                          self.field_image_alt: (self._image.get_image_alt(), self.field_image_alt_tip)}
        for field, value in field_to_value.items():
            tip = value[1]
            if value[0][1]:
                tip.SetMessage(Strings.seo_check + '\n' + value[0][1])
                tip.EnableTip(True)
                field.SetBackgroundColour(Numbers.RED_COLOR)
            else:
                tip.SetMessage(Strings.seo_check + '\n' + Strings.status_ok)
                tip.DoHideNow()
                field.SetBackgroundColour(Numbers.GREEN_COLOR)
            field.SetValue(value[0][0])

        # Set images
        self._bitmap.SetBitmap(wx.Bitmap(self._image.get_image()))
        # Set disk paths
        full_path = self._image.get_original_image_path()
        self.SetTitle(Strings.label_dialog_edit_image + ': ' + self._image.get_full_filename())
        if full_path:
            self.content_image_full_path.SetLabelText(full_path)
        else:
            self.content_image_full_path.SetLabelText(self._image.get_full_filename())

        # Set thumbnail size
        thumbnail_size = self._image.get_thumbnail_size()
        if thumbnail_size:
            self.content_image_thumbnail_size.SetLabelText(
                str(thumbnail_size[0]) + ' x ' + str(thumbnail_size[1]) + ' px')
        else:
            self.content_image_thumbnail_size.SetLabelText(Strings.status_error)

        # Set original size
        original_size = self._image.get_original_size()
        if original_size:
            self.content_image_original_size.SetLabelText(
                str(original_size[0]) + ' x ' + str(original_size[1]) + ' px')
        else:
            self.content_image_original_size.SetLabelText(Strings.status_error)

        thumb_path = self._image.get_thumbnail_image_path()
        if thumb_path:
            self.content_image_thumbnail_path.SetLabelText(thumb_path)
        else:
            self.content_image_thumbnail_path.SetLabelText(self._image.get_thumbnail_filename())
        self.Enable()
