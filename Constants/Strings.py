import os.path


class Strings:
    """This class holds string variables which are used in the program. This simplifies changes.
    """
    editor_name: str = 'Whitebear editor'
    home_directory: str = os.path.expanduser('~')
    exception_access: str = 'Main directory not readable'
    exception_access_html: str = 'File can not be accessed'
    exception_index: str = 'index.html is not in directory'
    exception_not_white_bear: str = 'Not a white Bear web directory'
    exception_file_unrecognized: str = 'This is not a white-bear html file'
    exception_only_one_title_allowed: str = 'Wrong file format, title tag found twice'
    exception_meta_description_twice: str = 'Wrong file format, meta description found twice'
    exception_not_bool: str = 'Modified can only be of type bool'
    label_file: str = '&File'
    label_quit: str = '&Quit'
    label_quit_hint: str = 'Quit'
    label_about: str = '&About'
    label_about_hint: str = 'About'
    label_open: str = '&Open directory'
    label_open_hint: str = 'Open directory'
    label_page_list: str = 'Page list'
    label_choose_dir: str = 'Choose whitebear directory'
    text_about_contents: str = 'Unfinished whitebear web editor'
    label_about_window_name: str = 'About'
    label_menu_logo: str = "Menu logo"
