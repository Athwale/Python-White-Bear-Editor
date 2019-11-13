import os.path


class Strings:
    """This class holds string variables which are used in the program. This simplifies changes.
    """
    editor_name = 'Whitebear editor'
    home_directory = os.path.expanduser('~')
    exception_access = 'Main directory not readable'
    exception_access_html = 'File can not be accessed'
    exception_index = 'index.html is not in directory'
    exception_not_white_bear = 'Not a white Bear web directory'
    exception_file_unrecognized = 'This is not a white-bear html file'
    exception_only_one_title_allowed = 'Wrong file format, title tag found twice'
    exception_meta_description_twice = 'Wrong file format, meta description found twice'
    label_file = '&File'
    label_quit = '&Quit'
    label_quit_hint = 'Quit'
    label_about = '&About'
    label_about_hint = 'About'
    label_open = '&Open directory'
    label_open_hint = 'Open directory'
    label_page_list = 'Page list'
    label_choose_dir = 'Choose whitebear directory'
    text_about_contents = 'Unfinished whitebear web editor'
    label_about_window_name = 'About'