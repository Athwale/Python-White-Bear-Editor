import os
from typing import Dict

import wx

from Constants.Constants import Strings, Numbers
from Tools.ConfigManager import ConfigManager
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu
from Tools.Tools import Tools


class EditMenuDialog(wx.Dialog):

    def __init__(self, parent, menus: Dict[str, WhitebearDocumentMenu], work_dir: str):
        """
        Display a dialog that allows editing additional data used in html generation.
        Default main title, author, contact, keywords, main page meta description. script, main page red/black text
        :param parent: The parent frame.
        :param menus: A dictionary of filename.html, WhitebearDocumentMenu
        :param work_dir: Working directory of the editor.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_edit_menu,
                           size=(Numbers.edit_menu_dialog_width, Numbers.edit_menu_dialog_height),
                           style=wx.CAPTION)

        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._menus = menus
        self._menu = None
        self._save_all = False
        self._work_dir = work_dir

        self._main_horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._left_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._right_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Menu list
        choices = list(self._menus.keys())
        self._menu_list = wx.ListBox(self, -1, size=(Numbers.minimal_panel_size, -1), choices=choices,
                                     style=wx.LB_SINGLE)
        if self._menus:
            self._menu_list.SetSelection(0)
        self._add_button = wx.Button(self, wx.ID_ADD, Strings.button_add)
        self._left_vertical_sizer.Add(self._menu_list, 1, flag=wx.TOP | wx.LEFT, border=Numbers.widget_border_size)
        self._left_vertical_sizer.Add(self._add_button, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
                                      border=Numbers.widget_border_size)

        # Page name sub sizer
        self._page_name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_page_name = wx.StaticText(self, -1, Strings.label_menu_name + ': ')
        self._field_page_name = wx.TextCtrl(self, -1)
        self._page_name_sub_sizer.Add(self._label_page_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._page_name_sub_sizer.Add((2, -1))
        self._page_name_sub_sizer.Add(self._field_page_name, proportion=1)
        self._information_sizer.Add(self._page_name_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_page_name_tip = Tools.get_warning_tip(self._field_page_name, Strings.label_menu_name)
        self._field_page_name_tip.SetMessage(Strings.label_menu_name)

        # Keywords sub sizer
        self._meta_keywords_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_meta_keywords = wx.StaticText(self, -1, Strings.label_default_keywords + ': ')
        self._field_meta_keywords = wx.TextCtrl(self, -1)
        self._meta_keywords_sub_sizer.Add(self._label_meta_keywords, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._meta_keywords_sub_sizer.Add((15, -1))
        self._meta_keywords_sub_sizer.Add(self._field_meta_keywords, proportion=1)
        self._information_sizer.Add(self._meta_keywords_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)
        self._field_keywords_tip = Tools.get_warning_tip(self._field_meta_keywords, Strings.label_article_keywords)
        self._field_keywords_tip.SetMessage(Strings.label_menu_meta_keywords)

        # --------------------------------------------------------------------------------------------------------------
        # Description sub sizer
        self._meta_description_sub_sizer = wx.BoxSizer(wx.VERTICAL)
        self._label_meta_description = wx.StaticText(self, -1, Strings.label_meta_description + ': ')
        self._field_meta_description = wx.TextCtrl(self, -1, size=(-1, 121), style=wx.TE_MULTILINE)
        self._meta_description_sub_sizer.Add(self._label_meta_description, flag=wx.ALIGN_LEFT)
        self._meta_description_sub_sizer.Add(3, 3)
        self._meta_description_sub_sizer.Add(self._field_meta_description, proportion=1, flag=wx.EXPAND)
        self._information_sizer.Add(self._meta_description_sub_sizer, 1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM,
                                    border=Numbers.widget_border_size)
        self._field_description_tip = Tools.get_warning_tip(self._field_meta_description,
                                                            Strings.label_meta_description)
        self._field_description_tip.SetMessage(Strings.label_menu_meta_description)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_save)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button.SetDefault()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._right_vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                       border=Numbers.widget_border_size)
        self._main_horizontal_sizer.Add(self._left_vertical_sizer, flag=wx.EXPAND)
        self._main_horizontal_sizer.Add(self._right_vertical_sizer, 1, flag=wx.EXPAND)
        self._right_vertical_sizer.Add(self._button_sizer, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                       border=Numbers.widget_border_size)
        self.SetSizer(self._main_horizontal_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_BUTTON, self._handle_new_menu_button, self._add_button)
        self.Bind(wx.EVT_LISTBOX, self._menu_list_handler, self._menu_list)
        for field in [self._field_page_name, self._field_meta_keywords, self._field_meta_description]:
            self.Bind(wx.EVT_TEXT, self._text_handler, field)

        if not self._menus:
            # Disable all but the new menu button.
            self._field_page_name.Disable()
            self._field_meta_keywords.Disable()
            self._field_meta_description.Disable()
            self._ok_button.Disable()

        self._display_dialog_contents()

    # noinspection PyUnusedLocal
    def _text_handler(self, event: wx.CommandEvent) -> None:
        """
        Run seo test on keywords and description when the text changes and prevent saving the values if seo fails.
        :param event: Not used.
        :return: None
        """
        if not self._seo_test():
            self._ok_button.Disable()
            self._menu_list.Disable()
            self._add_button.Disable()
        else:
            self._ok_button.Enable()
            self._menu_list.Enable()
            self._add_button.Enable()

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, run seo check on the new values and display results. Prevent closing if seo failed.
        :param event: The button event
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            self._save()

    def _save(self) -> None:
        """
        Save the changed data into the menu instance.
        :return: None
        """
        self._menu: WhitebearDocumentMenu
        # Must be separate, it is not run if used directly in the expression.
        result = self._menu.set_page_name(self._field_page_name.GetValue())
        self._save_all = self._save_all or result
        keywords_list = [word.strip() for word in self._field_meta_keywords.GetValue().split(',')]
        self._menu.set_keywords(keywords_list)
        self._menu.set_description(self._field_meta_description.GetValue())

    # noinspection PyUnusedLocal
    def _menu_list_handler(self, event: wx.CommandEvent) -> None:
        """
        Handles clicks onto menu names in the list box.
        :param event: Not used.
        :return: None
        """
        self._save()
        self._display_dialog_contents()

    def _display_dialog_contents(self) -> None:
        """
        Display the image that this dialog edits in the gui.
        :return: None
        """
        if self._menus:
            self.Disable()
            # Cancel is only available if we have no menus, otherwise force the user to fill it up correctly.
            self._cancel_button.Disable()
            self._menu: WhitebearDocumentMenu = self._menus[self._menu_list.GetString(self._menu_list.GetSelection())]
            self._field_page_name.SetValue(self._menu.get_page_name()[0])
            self._field_meta_keywords.SetValue(self._menu.get_keywords_string()[0])
            self._field_meta_description.SetValue(self._menu.get_description()[0])
            self._seo_test()
            self.Enable()

    def _seo_test(self) -> bool:
        """
        SEO test meta keywords and meta description.
        :return: True if seo is ok.
        """
        result = True
        # Keywords test.
        correct, message, color = self._menu.seo_test_keywords(self._field_meta_keywords.GetValue())
        result = result and correct
        self._field_meta_keywords.SetBackgroundColour(color)
        self._field_keywords_tip.SetMessage(Strings.seo_check + '\n' + message)

        # Description test.
        correct, message, color = self._menu.seo_test_description(self._field_meta_description.GetValue())
        result = result and correct
        self._set_field_background(self._field_meta_description, color)
        self._field_description_tip.SetMessage(Strings.seo_check + '\n' + message)

        # Test name
        correct, message, color = self._menu.seo_test_name(self._field_page_name.GetValue())
        result = result and correct
        self._field_page_name.SetBackgroundColour(color)
        self._field_page_name_tip.SetMessage(Strings.seo_check + '\n' + message)

        return result

    @staticmethod
    def _set_field_background(field: wx.TextCtrl, color: wx.Colour) -> None:
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

    # noinspection PyUnusedLocal
    def _handle_new_menu_button(self, event: wx.CommandEvent) -> None:
        """
        Create a new menu and allow editing it.
        :param event: Not used
        :return: None
        """
        name_dialog = wx.TextEntryDialog(self, Strings.label_file_name + ':', caption=Strings.label_menu_file_name,
                                         value="")
        if name_dialog.ShowModal() == wx.ID_OK:
            file_name = name_dialog.GetValue()
            # Test file name format.
            wrong_name: bool = False
            for c in file_name:
                if not c.isalnum():
                    wrong_name = True
                if c == '-':
                    wrong_name = False
            if wrong_name:
                wx.MessageBox(Strings.warning_name_incorrect, Strings.status_error, wx.OK | wx.ICON_ERROR)
                return
            # Test whether file already exists
            file_name = file_name + Strings.extension_html
            path = os.path.join(self._work_dir, file_name)
            if os.path.exists(path):
                wx.MessageBox(Strings.warning_file_exists, Strings.status_error, wx.OK | wx.ICON_ERROR)
                return

            # Create a folder under logos, thumbnails and originals.
            # todo problem with folders named by sections, when name changes folders remain the same, create and rename
            # todo folders according to the name field.
            for directory in [os.path.join(Strings.folder_images, Strings.folder_logos, name_dialog.GetValue()),
                              os.path.join(Strings.folder_images, Strings.folder_originals, name_dialog.GetValue()),
                              os.path.join(Strings.folder_images, Strings.folder_thumbnails, name_dialog.GetValue())]:
                dir_path = os.path.join(self._work_dir, directory)
            if not os.path.exists(dir_path):
                # Create those directories that are missing.
                os.mkdir(dir_path)

            # Create new menu document
            new_menu = WhitebearDocumentMenu(path, self._menus)
            new_menu.set_keywords(self._config_manager.get_global_keywords().split(', '))
            self._menus[file_name] = new_menu
            self._menu_list.Insert(file_name, self._menu_list.GetCount())
            self._menu_list.SetSelection(self._menu_list.GetCount() - 1)
            self._display_dialog_contents()
            self._save_all = True
            # At this point at least one menu exists and the controls can be enabled.
            self._field_page_name.SetValue(name_dialog.GetValue())
            self._field_page_name.Enable()
            self._field_meta_keywords.Enable()
            self._field_meta_description.Enable()
        name_dialog.Destroy()

    def save_all(self) -> bool:
        """
        Returns True if menu name was changed or new menu created, in that case all documents must be re-exported to
        reflect the new change.
        :return: True if re-export of all document is needed.
        """
        return self._save_all
