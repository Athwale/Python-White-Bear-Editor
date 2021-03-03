import os
from typing import List, Dict
from datetime import date

import wx

from Constants.Constants import Strings, Numbers
from Gui.Dialogs.EditAsideImageDialog import EditAsideImageDialog
from Gui.Dialogs.EditMenuItemDialog import EditMenuItemDialog
from Resources.Fetch import Fetch
from Tools.ConfigManager import ConfigManager
from Tools.Document.AsideImage import AsideImage
from Tools.Document.MenuItem import MenuItem
from Tools.Document.WhitebearDocumentArticle import WhitebearDocumentArticle
from Tools.Document.WhitebearDocumentCSS import WhitebearDocumentCSS
from Tools.Document.WhitebearDocumentIndex import WhitebearDocumentIndex
from Tools.Document.WhitebearDocumentMenu import WhitebearDocumentMenu
from Tools.Tools import Tools


class NewFileDialog(wx.Dialog):

    def __init__(self, parent, menus: Dict[str, WhitebearDocumentMenu], articles: Dict[str, WhitebearDocumentArticle],
                 css: WhitebearDocumentCSS, index: WhitebearDocumentIndex):
        """
        Display a dialog that allows editing additional data used in html generation.
        Default main title, author, contact, keywords, main page meta description. script, main page red/black text
        :param parent: The parent frame.
        :param menus: Currently loaded dictionary of menus.
        :param articles: Currently loaded dictionary of articles.
        :param css: Currently loaded css document.
        :param index: Currently loaded index document.
        """
        wx.Dialog.__init__(self, parent, title=Strings.label_dialog_new_document,
                           size=(Numbers.new_file_dialog_width, Numbers.new_file_dialog_height),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self._config_manager: ConfigManager = ConfigManager.get_instance()
        self._doc = None
        self._menus = menus
        self._articles = articles
        self._css_document = css
        self._index = index
        self._article_image = None
        self._menu_item = None
        self._document_path = None

        self._main_vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._horizontal_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        self._information_sizer = wx.BoxSizer(wx.VERTICAL)

        # Name sub sizer
        self._name_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_file_name = wx.StaticText(self, -1, Strings.label_name + ': ')
        self._field_name = wx.TextCtrl(self, -1)
        self._name_sub_sizer.Add(self._label_file_name, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._name_sub_sizer.Add(8, -1)
        self._name_sub_sizer.Add(self._field_name, proportion=1)
        self._information_sizer.Add(self._name_sub_sizer, flag=wx.EXPAND | wx.TOP, border=Numbers.widget_border_size)
        self._field_name_tip = Tools.get_warning_tip(self._field_name, Strings.label_article_title)
        self._field_name.SetBackgroundColour(Numbers.RED_COLOR)
        self._field_name_tip.SetMessage(Strings.warning_empty)

        choices: List[str] = [menu.get_page_name()[0] for menu in self._menus.values()]
        # Category sub sizer
        self._category_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._label_category = wx.StaticText(self, -1, Strings.label_target_section + ': ')
        self._box_menu = wx.ComboBox(self, -1, choices=choices, style=wx.CB_DROPDOWN | wx.CB_SORT | wx.CB_READONLY)
        self._box_menu.SetSelection(0)
        self._category_sub_sizer.Add(self._label_category, flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self._category_sub_sizer.Add(self._box_menu, proportion=1)
        self._information_sizer.Add(self._category_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Image buttons
        self._image_buttons_sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._menu_logo_button = wx.Button(self, wx.ID_FILE1, style=wx.BU_EXACTFIT | wx.BORDER_NONE,
                                           size=wx.Size(Numbers.menu_logo_image_size, Numbers.menu_logo_image_size))
        self._menu_logo_button.Disable()
        self._menu_logo_button.SetBitmap(wx.Bitmap(wx.Image(Fetch.get_resource_path('menu_image.png'),
                                                            wx.BITMAP_TYPE_PNG)))
        self._main_image_button = wx.Button(self, wx.ID_FILE2, style=wx.BU_EXACTFIT | wx.BORDER_NONE)
        self._main_image_button.Disable()
        self._main_image_button.SetBitmap(wx.Bitmap(wx.Image(Fetch.get_resource_path('article_image.png'),
                                                             wx.BITMAP_TYPE_PNG)))
        self._image_buttons_sub_sizer.Add(self._main_image_button, 1, flag=wx.EXPAND)
        self._image_buttons_sub_sizer.Add(Numbers.widget_border_size, Numbers.widget_border_size)
        self._image_buttons_sub_sizer.Add(self._menu_logo_button, 1, flag=wx.EXPAND)
        self._information_sizer.Add(self._image_buttons_sub_sizer, flag=wx.EXPAND | wx.TOP,
                                    border=Numbers.widget_border_size)

        # Buttons
        self._button_sizer = wx.BoxSizer(wx.VERTICAL)
        grouping_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._cancel_button = wx.Button(self, wx.ID_CANCEL, Strings.button_cancel)
        self._ok_button = wx.Button(self, wx.ID_OK, Strings.button_ok)
        self._ok_button.SetDefault()
        self._ok_button.Disable()
        grouping_sizer.Add(self._ok_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        grouping_sizer.Add(self._cancel_button)
        grouping_sizer.Add((Numbers.widget_border_size, Numbers.widget_border_size))
        self._button_sizer.Add(grouping_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

        # Putting the sizers together
        self._vertical_sizer.Add(self._information_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP,
                                 border=Numbers.widget_border_size)
        self._horizontal_sizer.Add(self._vertical_sizer, 1)
        self._main_vertical_sizer.Add(self._horizontal_sizer, 1, flag=wx.EXPAND)
        self._main_vertical_sizer.Add(self._button_sizer, 0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
                                      border=Numbers.widget_border_size)
        self.SetSizer(self._main_vertical_sizer)

        # Bind handlers
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._ok_button)
        self.Bind(wx.EVT_BUTTON, self._handle_buttons, self._cancel_button)
        self.Bind(wx.EVT_TEXT, self._handle_name_change, self._field_name)
        self.Bind(wx.EVT_BUTTON, self._handle_image_buttons, self._main_image_button)
        self.Bind(wx.EVT_BUTTON, self._handle_image_buttons, self._menu_logo_button)

    def _handle_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle button clicks, check if target file exists and prevent overwriting it.
        :param event: The button event, used to distinguish between buttons.
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_OK:
            # Add the new menu item into the correct menu document instance.
            for menu in self._menus.values():
                if menu.get_page_name()[0] == self._box_menu.GetValue():
                    menu.add_item(self._menu_item)
            # Create the document once all is set. Add item into menu, let document determine section.
            self._doc = WhitebearDocumentArticle(self._document_path, self._menus, self._articles, self._css_document)
            self._doc.set_index_document(self._index)
            self._doc.determine_menu_section_and_menu_item()
            self._doc.set_article_image(self._article_image)
            self._doc.set_date(self._get_current_date())
            self._doc.set_keywords(self._config_manager.get_global_keywords().split(','))
            self._doc.seo_test_self()

    @staticmethod
    def _get_current_date() -> str:
        """
        Return czech date string formatted for the article.
        :return: Czech date string formatted for the article.
        """
        month_dict = {k: v for k, v in zip(range(1, 13), Strings.cz_months.split('|'))}
        today = date.today()
        day = today.strftime("%-d")
        month = today.strftime("%-m")
        year = today.strftime("%Y")
        return day + '. ' + month_dict[int(month)] + ' ' + year

    def _get_document_path(self) -> bool:
        """
        Get the disk path for the new html file.
        :return: True if path is acceptable. False if target already exists.
        """
        # Check for file existence.
        # We must have at least one parsed menu which has a working directory at this point, otherwise we would
        # not be in this dialog.
        working_dir: str = next(iter(self._menus.values())).get_working_directory()
        file_name: str = self._field_name.GetValue() + Strings.extension_html

        path = os.path.join(working_dir, file_name)
        if os.path.exists(path):
            return False
        else:
            self._document_path = path
            return True

    def _handle_image_buttons(self, event: wx.CommandEvent) -> None:
        """
        Handle image button clicks.
        :param event: The button event, used to distinguish between buttons.
        :return: None
        """
        event.Skip()
        if event.GetId() == wx.ID_FILE1:
            # Create menu item.
            if not self._menu_item:
                menu_item: MenuItem = MenuItem(self._box_menu.GetValue(),
                                               name='',
                                               title='',
                                               image_alt='',
                                               href=self._field_name.GetValue() + Strings.extension_html,
                                               disk_path='',
                                               img_filename=Strings.status_none)
                menu_item.seo_test_self()
            else:
                menu_item = self._menu_item
            edit_dialog = EditMenuItemDialog(self, menu_item, self._config_manager.get_working_dir(),
                                             self._box_menu.GetValue())
            # We first need to show the dialog so that the name label can calculate it's size and then switch to modal.
            edit_dialog.Show()
            edit_dialog.display_dialog_contents()
            result = edit_dialog.ShowModal()
            edit_dialog.Destroy()
            if result == wx.ID_OK:
                # Display the image. Disable section and name fields and enable main image button.
                self._menu_logo_button.SetBitmap(wx.Bitmap(menu_item.get_image()))
                self._field_name.Disable()
                self._box_menu.Disable()
                self._main_image_button.Enable()
                self._menu_item = menu_item
        elif event.GetId() == wx.ID_FILE2:
            # Create article image.
            if not self._article_image:
                image = AsideImage(self._box_menu.GetValue(),
                                   caption='',
                                   title='',
                                   image_alt='',
                                   original_image_path='',
                                   thumbnail_path='', full_filename=Strings.status_none,
                                   thumbnail_filename=Strings.status_none)
                image.seo_test_self()
            else:
                image = self._article_image
            edit_dialog = EditAsideImageDialog(self, image, self._config_manager.get_working_dir(),
                                               self._box_menu.GetValue())
            result = edit_dialog.ShowModal()
            edit_dialog.Destroy()
            if result == wx.ID_OK:
                self._main_image_button.SetBitmap(wx.Bitmap(image.get_image()))
                self._ok_button.Enable()
                self._article_image = image

    # noinspection PyUnusedLocal
    def _handle_name_change(self, event: wx.CommandEvent) -> None:
        """
        Disable OK button if the name field is empty.
        :param event: Not used
        :return: None
        """
        new_name = self._field_name.GetValue()
        wrong_name: bool = False
        for c in new_name:
            if not c.isalnum():
                wrong_name = True
            if c == '-':
                wrong_name = False
        if wrong_name or not self._get_document_path() or not self._field_name.GetValue():
            self._field_name.SetBackgroundColour(Numbers.RED_COLOR)
            if wrong_name:
                self._field_name_tip.SetMessage(Strings.warning_name_incorrect)
            if not self._get_document_path():
                self._field_name_tip.SetMessage(Strings.warning_file_exists)
            if not self._field_name.GetValue():
                self._field_name_tip.SetMessage(Strings.warning_empty)
            self._field_name_tip.EnableTip(True)
            self._field_name_tip.Show(True)
            self._ok_button.Disable()
            self._main_image_button.Disable()
            self._menu_logo_button.Disable()
        else:
            self._field_name_tip.SetMessage(Strings.status_ok)
            self._field_name_tip.DoHideNow()
            self._field_name.SetBackgroundColour(Numbers.GREEN_COLOR)
            self._menu_logo_button.Enable()

    def get_new_document(self) -> WhitebearDocumentArticle:
        """
        Return the new document created in this dialog.
        :return: The new document created in this dialog.
        """
        return self._doc
