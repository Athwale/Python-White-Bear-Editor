import wx

from Constants.Constants import Strings, Numbers
from Tools.Document.ArticleElements.Link import Link
from Tools.Tools import Tools


class EditLinkDialog(wx.Dialog):

    def __init__(self, parent, link: Link):
        """
        Display a dialog with information about the link where the user can edit it.
        :param parent: Parent frame.
        :param link: the Link instance to display.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_link,
                           size=(Numbers.edit_aside_image_dialog_width, Numbers.edit_link_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)
        self._link = link

        self.main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self.information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Link URL sub sizer
        self.url_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_url = wx.StaticText(self, -1, Strings.label_url + ': ')
        self.field_url = wx.ComboBox(self, -1, choices=self._link.get_loaded_pages(), style=wx.CB_DROPDOWN | wx.CB_SORT)
        # Fires when you type in the box
        self.Bind(wx.EVT_TEXT, self._combobox_handler, self.field_url)

        self.url_sub_sizer.Add(self.label_url, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.url_sub_sizer.Add((35, -1))
        self.url_sub_sizer.Add(self.field_url, proportion=1)
        self.information_sizer.Add(self.url_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_url_tip = Tools.get_warning_tip(self.field_url, Strings.label_url)

        # Link title sub sizer
        self.title_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_link_title = wx.StaticText(self, -1, Strings.label_link_title + ': ')
        self.field_link_title = wx.TextCtrl(self, -1)
        self.title_sub_sizer.Add(self.label_link_title, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.title_sub_sizer.Add((8, -1))
        self.title_sub_sizer.Add(self.field_link_title, proportion=1)
        self.information_sizer.Add(self.title_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_link_title_tip = Tools.get_warning_tip(self.field_link_title, Strings.label_link_title)

        # Link text sub sizer
        self.text_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_link_text = wx.StaticText(self, -1, Strings.label_text + ': ')
        self.field_link_text = wx.TextCtrl(self, -1)
        self.text_sub_sizer.Add(self.label_link_text, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.text_sub_sizer.Add((35, -1))
        self.text_sub_sizer.Add(self.field_link_text, proportion=1)
        self.information_sizer.Add(self.text_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self.field_link_text_tip = Tools.get_warning_tip(self.field_link_text, Strings.label_text)

        # Target blank checkbox
        self.checkbox_target_blank = wx.CheckBox(self, -1, label=Strings.label_open_in_new_page)
        self.checkbox_target_blank.SetValue(True)
        self.checkbox_target_blank.Disable()
        # Local link checkbox
        self.checkbox_local = wx.CheckBox(self, -1, label=Strings.label_link_local)
        self.checkbox_local.Disable()
        self.information_sizer.Add(self.checkbox_target_blank, flag=wx.TOP, border=Numbers.widget_border_size)
        self.information_sizer.Add(self.checkbox_local, flag=wx.TOP, border=Numbers.widget_border_size)

        # Buttons
        self.button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self.ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self.ok_button.SetDefault()
        self.delete_button = wx.Button(self, wx.ID_DELETE, Strings.button_remove_link)
        grouping_sizer.Add(self.ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self.cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self.delete_button)
        self.button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self.vertical_sizer.Add(self.information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                border=Numbers.widget_border_size)
        self.horizontal_sizer.Add(self.vertical_sizer, 1)
        self.main_vertical_sizer.Add(self.horizontal_sizer, 1, flag=wx.EXPAND)
        self.main_vertical_sizer.Add(self.button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                     border=Numbers.widget_border_size)
        self.SetSizer(self.main_vertical_sizer)
        self._display_dialog_contents()

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self.delete_button)

        self._original_text = self._link.get_text()[0]
        self._original_url = self._link.get_url()[0]
        self._original_title = self._link.get_title()[0]

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        if event.GetId() == wx.ID_DELETE:
            # Only OK and Cancel button close the dialog by default.
            event.Skip()
            self.EndModal(wx.ID_DELETE)
        elif event.GetId() == wx.ID_OK:
            # Save new information into image and rerun seo test.
            self._link.set_text(self.field_link_text.GetValue())
            self._link.set_title(self.field_link_title.GetValue())
            self._link.set_url(self.field_url.GetValue())

            if self._link.seo_test_self():
                event.Skip()
                return
            else:
                self._display_dialog_contents()
        else:
            # Restore original values
            self._link.set_url(self._original_url)
            self._link.set_title(self._original_title)
            self._link.set_text(self._original_text)
            self._link.set_modified(False)
            self._link.seo_test_self()
            event.Skip()

    # noinspection PyUnusedLocal
    def _combobox_handler(self, event: wx.CommandEvent) -> None:
        """
        Handle actions made in the combobox control.
        :param event: Not used.
        :return: None
        """
        if self.field_url.GetValue() in self._link.get_loaded_pages():
            self._link.set_local(True)
            self.checkbox_local.SetValue(True)
        else:
            self._link.set_local(False)
            self.checkbox_local.SetValue(False)

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        self.Disable()
        # Set image data
        field_to_value = {self.field_url: (self._link.get_url(), self.field_url_tip),
                          self.field_link_title: (self._link.get_title(), self.field_link_title_tip),
                          self.field_link_text: (self._link.get_text(), self.field_link_text_tip)}
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

        # Set checkbox local state
        self.checkbox_local.SetValue(self._link.is_local())
        self.Enable()
