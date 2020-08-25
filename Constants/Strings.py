import os.path

from Constants.Numbers import Numbers


class Strings:
    """
    This class holds string variables which are used in the program. This simplifies changes.
    """
    cz_months = '|'.join(
        ['Ledna', 'Února', 'Března', 'Dubna', 'Května', 'Června', 'Července', 'Srpna', 'Září', 'Října', 'Listopadu',
         'Prosince'])
    home_directory: str = os.path.expanduser('~')
    editor_config_file: str = os.path.join(home_directory, '.whitebearEditor.conf')
    editor_output_debug_file: str = os.path.join(home_directory, 'whitebearEditor.log')
    editor_name: str = 'Whitebear editor'
    editor_version: str = '0.1'

    column_pages = 'Name'

    text_about_contents: str = '<p>Unfinished whitebear web editor.<br>' \
                               '<i>https://github.com/Athwale/Python-White-Bear-Editor</i><br>' \
                               'version: <b>' + editor_version + '</b></p>'

    exception_access: str = 'Main directory not readable'
    exception_access_html: str = 'File can not be accessed'
    exception_index: str = 'index.html is not in directory'
    exception_not_white_bear: str = 'Not a white Bear web directory'
    exception_file_unrecognized: str = 'Unrecognized or malformed white-bear html file:'
    exception_conf_inaccessible: str = '.whitebearEditor.conf inaccessible'
    exception_resource_not_found: str = 'Resource not found'
    exception_html_syntax_error: str = 'Syntax error in html file'
    exception_parse_multiple_descriptions: str = 'Only one meta description tag is allowed'
    exception_parse_multiple_keywords: str = 'Only one meta keywords tag is allowed'
    exception_last_document_missing: str = 'Last open document not found'
    exception_menu_item_missing: str = 'Menu item missing'

    seo_error_keywords_length: str = 'Meta keywords must be: ' + str(Numbers.keywords_min_length) + ' - ' + str(
        Numbers.keywords_max_length) + ' characters long'

    label_menu_file: str = 'File'
    label_menu_item_open: str = 'Open directory...\tctrl+o'
    label_menu_item_open_hint: str = 'Open a whitebear web directory'

    label_menu_item_quit: str = 'Quit\tctrl+q'
    label_menu_item_quit_hint: str = 'Quit editor'

    label_menu_help: str = 'Help'
    label_menu_item_about: str = 'About'
    label_menu_item_about_hint: str = 'About whitebear editor'

    label_dialog_choose_wb_dir: str = 'Choose whitebear directory'
    label_dialog_about: str = 'About'

    label_article_menu_logo: str = 'Menu logo'
    label_article_menu_logo_name_placeholder: str = 'Menu item name'
    label_article_menu_logo_alt_placeholder: str = ' Alt description'
    label_article_menu_logo_title_placeholder: str = ' Link title'
    label_article_image: str = 'Article image'
    label_article_image_alt: str = 'Image alt description'
    label_article_image_title: str = 'Image link title'
    label_article_image_name: str = 'Image caption'
    label_article_date: str = 'Date'
    label_article_title: str = 'Article name'
    label_article_keywords: str = 'Meta keywords'
    label_article_description: str = 'Meta description'
    label_article_info: str = 'Article data'
    label_article_photo_column: str = 'Photos'

    status_loading: str = 'Loading'
    status_ready: str = 'Ready'
    status_error: str = 'Error'
    status_valid: str = 'Valid:'
    status_invalid: str = 'Invalid:'
    status_articles: str = 'Articles:'

    toolbar_new_file: str = 'New file'

    button_close: str = 'Close'
