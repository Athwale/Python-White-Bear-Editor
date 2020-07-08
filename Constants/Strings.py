import os.path


class Strings:
    """
    This class holds string variables which are used in the program. This simplifies changes.
    """
    home_directory: str = os.path.expanduser('~')
    editor_config_file: str = os.path.join(home_directory, '.whitebearEditor.conf')
    editor_name: str = 'Whitebear editor'
    editor_version: str = '0.1'
    text_about_contents: str = 'Unfinished whitebear web editor.' \
                               '\nhttps://github.com/Athwale/Python-White-Bear-Editor\n' \
                               'version: ' + editor_version
    exception_access: str = 'Main directory not readable'
    exception_access_html: str = 'File can not be accessed'
    exception_index: str = 'index.html is not in directory'
    exception_not_white_bear: str = 'Not a white Bear web directory'
    exception_file_unrecognized: str = 'This is not a white-bear html file'
    exception_only_one_title_allowed: str = 'Wrong file format, title tag found twice'
    exception_meta_description_twice: str = 'Wrong file format, meta description found twice'
    exception_not_bool: str = 'Modified can only be of type bool'
    exception_conf_inaccessible: str = '.whitebearEditor.conf inaccessible'
    label_file: str = '&File'
    label_quit: str = '&Quit'
    label_quit_hint: str = 'Quit'
    label_about: str = '&About'
    label_about_hint: str = 'About'
    label_open: str = '&Open directory'
    label_open_hint: str = 'Open directory'
    label_page_list: str = 'Page list'
    label_choose_dir: str = 'Choose whitebear directory'
    label_about_window_name: str = 'About'
    label_menu_logo: str = 'Menu logo'
    label_menu_logo_name_placeholder: str = 'Logo name'
    label_menu_logo_alt_placeholder: str = ' Alt description'
    label_menu_logo_title_placeholder: str = ' Link title'
    label_article_image: str = 'Article image'
    label_article_image_alt: str = 'Alt description'
    label_article_image_title: str = 'Image title'
    label_article_image_name: str = 'Image name'
    label_article_date: str = 'Date'
    label_article_title: str = 'Article name'
    label_article_keywords: str = 'Meta keywords'
    label_article_description: str = 'Meta description'
    label_article_info: str = 'Article data'
    label_photo_column: str = 'Photos'
    status_ready: str = 'Ready'
