import wx
import wx.richtext as rt


class RichTextFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.text_attr = None

        self.make_menu_bar()
        self.CreateStatusBar()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.rtc = rt.RichTextCtrl(self, style=wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER)
        self.style_control = rt.RichTextStyleComboCtrl(self, -1)
        self.style_control.SetRichTextCtrl(self.rtc)
        self.style_control.SetStyleSheet(self.rtc.GetStyleSheet())

        self.sizer.Add(self.style_control)
        self.sizer.Add(self.rtc, 1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)

        self.add_rtc_handlers()
        self.Bind(wx.EVT_TEXT_URL, self.on_url)
        self.Bind(rt.EVT_RICHTEXT_LEFT_CLICK, self.on_left_click)
        self.Bind(rt.EVT_RICHTEXT_RIGHT_CLICK, self.on_right_click)

        # Register field type
        self.field_type = rt.RichTextFieldTypeStandard('imageFieldType', bitmap=wx.Bitmap(
            wx.Image('/home/omejzlik/PycharmProjects/Python-White-Bear-Editor/Resources/main_image_missing.png',
                     wx.BITMAP_TYPE_PNG)), displayStyle=rt.RichTextFieldTypeStandard.RICHTEXT_FIELD_STYLE_RECTANGLE)
        rt.RichTextBuffer.AddFieldType(self.field_type)

    def on_left_click(self, evt: wx.richtext.RichTextEvent):
        print(evt.GetContainer().GetName())
        evt.Skip()

    def on_right_click(self, evt):
        print(evt.GetContainer().GetName())
        evt.Skip()

    def add_rtc_handlers(self):
        # This would normally go in your app's OnInit method.  I'm
        # not sure why these file handlers are not loaded by
        # default by the C++ rich text code, I guess it's so you
        # can change the name or extension if you wanted like this
        rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler(name="XML", ext="xml", type=99))

    def on_file_open(self, evt):
        # This gives us a string suitable for the file dialog based on
        # the file handlers that are loaded
        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=False)
        print(wildcard)
        print(types)
        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=wildcard,
                            style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                file_type = types[dlg.GetFilterIndex()]
                self.rtc.LoadFile(path, file_type)
        dlg.Destroy()

    def set_font_style(self, font_color=None, font_bg_color=None, font_face=None, font_size=None,
                       font_bold=None, font_italic=None, font_underline=None):
        if font_color:
            self.text_attr.SetTextColour(font_color)
        if font_bg_color:
            self.text_attr.SetBackgroundColour(font_bg_color)
        if font_face:
            self.text_attr.SetFontFaceName(font_face)
        if font_size:
            self.text_attr.SetFontSize(font_size)
        if font_bold is not None:
            if font_bold:
                self.text_attr.SetFontWeight(wx.FONTWEIGHT_BOLD)
            else:
                self.text_attr.SetFontWeight(wx.FONTWEIGHT_NORMAL)
        if font_italic is not None:
            if font_italic:
                self.text_attr.set_font_style(wx.FONTSTYLE_ITALIC)
            else:
                self.text_attr.set_font_style(wx.FONTSTYLE_NORMAL)
        if font_underline is not None:
            if font_underline:
                self.text_attr.SetFontUnderlined(True)
            else:
                self.text_attr.SetFontUnderlined(False)
        self.rtc.SetDefaultStyle(self.text_attr)

    def on_url(self, evt):
        print(self.rtc.GetNumberOfLines())
        link = self.rtc.GetRange(evt.GetURLStart(), evt.GetURLEnd() + 1)
        wx.MessageBox(evt.GetString() + ' ' + link, "URL Clicked")

    def on_file_save(self, evt):
        if not self.rtc.GetFilename():
            self.on_file_save_as(evt)
            return
        self.rtc.SaveFile()

    def on_insert_image(self, evt):
        field = self.rtc.WriteField('imageFieldType', rt.RichTextProperties())
        field.SetName('image1')
        #print(field.GetName())

    def on_insert_link(self, evt):
        url_style = rt.RichTextAttr()
        url_style.SetTextColour(wx.BLUE)
        url_style.SetFontUnderlined(True)

        self.rtc.BeginStyle(url_style)
        self.rtc.BeginURL('www.google.com')
        self.rtc.WriteText('google')
        self.rtc.EndURL()
        self.rtc.EndStyle()

    def on_file_save_as(self, evt):
        wildcard, types = rt.RichTextBuffer.GetExtWildcard(save=True)

        dlg = wx.FileDialog(self, "Choose a filename",
                            wildcard=wildcard,
                            style=wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if path:
                file_type = types[dlg.GetFilterIndex()]
                ext = rt.RichTextBuffer.FindHandlerByType(file_type).GetExtension()
                if not path.endswith(ext):
                    path += '.' + ext
                self.rtc.SaveFile(path, file_type)
        dlg.Destroy()

    def on_file_exit(self, evt):
        self.Close(True)

    def on_bold(self, evt):
        self.rtc.ApplyBoldToSelection()

    def on_colour(self, evt):
        colour_data = wx.ColourData()
        attr = wx.TextAttr()
        attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
        if self.rtc.GetStyle(self.rtc.GetInsertionPoint(), attr):
            colour_data.SetColour(attr.GetTextColour())

        colour = wx.RED
        if not self.rtc.HasSelection():
            self.rtc.BeginTextColour(colour)
        else:
            r = self.rtc.GetSelectionRange()
            attr.SetFlags(wx.TEXT_ATTR_TEXT_COLOUR)
            attr.SetTextColour(colour)
            self.rtc.SetStyle(r, attr)

    def on_update_bold(self, evt):
        evt.Check(self.rtc.IsSelectionBold())

    def forward_event(self, evt):
        # The RichTextCtrl can handle menu and update events for undo,
        # redo, cut, copy, paste, delete, and select all, so just
        # forward the event to it.
        self.rtc.ProcessEvent(evt)

    def make_menu_bar(self):
        def do_bind(item, handler, update_ui=None):
            self.Bind(wx.EVT_MENU, handler, item)
            if update_ui is not None:
                self.Bind(wx.EVT_UPDATE_UI, update_ui, item)

        file_menu = wx.Menu()
        do_bind(file_menu.Append(-1, "&Open\tCtrl+O", "Open a file"),
                self.on_file_open)
        do_bind(file_menu.Append(-1, "&Save\tCtrl+S", "Save a file"),
                self.on_file_save)
        do_bind(file_menu.Append(-1, "&Save As...\tF12", "Save to a new file"),
                self.on_file_save_as)
        do_bind(file_menu.Append(-1, "E&xit\tCtrl+Q", "Quit this program"),
                self.on_file_exit)

        edit_menu = wx.Menu()
        do_bind(edit_menu.Append(wx.ID_SELECTALL, "Select A&ll\tCtrl+A"),
                self.forward_event, self.forward_event)
        do_bind(edit_menu.Append(wx.ID_CUT, "Cut"), self.forward_event, self.forward_event)
        do_bind(edit_menu.Append(wx.ID_COPY, 'Copy', ), self.forward_event, self.forward_event)
        do_bind(edit_menu.Append(wx.ID_PASTE, 'Paste'), self.forward_event, self.forward_event)
        do_bind(edit_menu.Append(wx.ID_UNDO, 'Undo'), self.forward_event, self.forward_event)
        do_bind(edit_menu.Append(wx.ID_REDO, 'Redo'), self.forward_event, self.forward_event)
        do_bind(edit_menu.Append(-1, 'Color'), self.on_colour)
        do_bind(edit_menu.Append(-1, 'Insert image\tCtrl+i'), self.on_insert_image)
        do_bind(edit_menu.Append(-1, 'Insert link'), self.on_insert_link)

        format_menu = wx.Menu()
        do_bind(format_menu.AppendCheckItem(-1, "&Bold\tCtrl+B"),
                self.on_bold, self.on_update_bold)

        mb = wx.MenuBar()
        mb.Append(file_menu, "&File")
        mb.Append(edit_menu, "&Edit")
        mb.Append(format_menu, "F&ormat")
        self.SetMenuBar(mb)


class MyApp(wx.App):
    """
    Main class for running the gui
    """

    def __init__(self):
        wx.App.__init__(self)
        self.frame = None

    def OnInit(self):
        self.frame = RichTextFrame(None, -1, "RichTextCtrl", size=(900, 500), style=wx.DEFAULT_FRAME_STYLE)
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

    def OnExit(self):
        print('_Done_')
        return True


if __name__ == "__main__":
    # Redirect allows the gui to show a window with std and err text output, or if set, send it to a file.
    app = MyApp()
    app.MainLoop()
