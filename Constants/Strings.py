import os.path


class Strings:
    """
    This class holds string variables which are used in the program. This simplifies changes.
    """
    home_directory: str = os.path.expanduser('~')
    editor_config_file: str = os.path.join(home_directory, '.whitebearEditor.conf')
    editor_output_debug_file: str = os.path.join(home_directory, 'whitebearEditor.log')
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
    exception_resource_not_found: str = 'Resource not found'

    label_menu_file: str = '&File'
    label_menu_item_open: str = '&Open directory'
    label_menu_item_open_hint: str = 'Open a whitebear web directory'

    label_menu_item_quit: str = '&Quit'
    label_menu_item_quit_hint: str = 'Quit editor'

    label_menu_help: str = '&Help'
    label_menu_item_about: str = '&About'
    label_menu_item_about_hint: str = 'About whitebear editor'

    label_dialog_choose_wb_dir: str = 'Choose whitebear directory'
    label_dialog_about: str = 'About'

    label_article_menu_logo: str = 'Menu logo'
    label_article_menu_logo_name_placeholder: str = 'Logo name'
    label_article_menu_logo_alt_placeholder: str = ' Alt description'
    label_article_menu_logo_title_placeholder: str = ' Link title'
    label_article_image: str = 'Article image'
    label_article_image_alt: str = 'Alt description'
    label_article_image_title: str = 'Image title'
    label_article_image_name: str = 'Image name'
    label_article_date: str = 'Date'
    label_article_title: str = 'Article name'
    label_article_keywords: str = 'Meta keywords'
    label_article_description: str = 'Meta description'
    label_article_info: str = 'Article data'
    label_article_photo_column: str = 'Photos'

    status_loading: str = 'Loading'
    status_ready: str = 'Ready'
    status_error: str = 'Error'

    toolbar_new_file: str = 'New file'

    button_close: str = 'Close'
