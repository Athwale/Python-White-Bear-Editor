from wx import Colour
import os.path


class Numbers:
    RED_COLOR = Colour(242, 207, 206)
    GREEN_COLOR = Colour(201, 255, 199)
    YELLOW_COLOR = Colour(250, 255, 196)

    minimal_window_size_width: int = 1200
    minimal_window_size_height: int = 700
    initial_panel_size: int = 220
    minimal_panel_size: int = 150
    maximal_panel_size: int = 300
    text_field_font_size: int = 9
    widget_border_size: int = 5
    photo_column_width: int = 300

    # SEO values
    year_min: int = 2000
    year_max: int = 3000
    logo_image_size: int = 96
    main_image_width: int = 300
    main_image_height: int = 225
    text_image_max_size: int = 534
    keywords_min_length: int = 50
    keywords_max_length: int = 255
    description_min_length: int = 50
    description_max_length: int = 160
    image_alt_max_length: int = 125
    min_body_word_length: int = 250
    article_name_min_length: int = 3
    article_name_max_length: int = 255
    article_image_caption_min: int = 5
    article_image_caption_max: int = 255
    article_image_title_min: int = 5
    article_image_title_max: int = 512
    article_image_alt_min: int = 5
    article_image_alt_max: int = 125


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
    text_reload_from_disk: str = 'Reload file from disk?\nThis will discard all unsaved changes.'

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

    seo_error_keywords_length: str = 'Length must be: ' + str(Numbers.keywords_min_length) + ' - ' + str(
        Numbers.keywords_max_length) + ' characters long'
    seo_error_description_length: str = 'Length must be: ' + str(
        Numbers.description_min_length) + ' - ' + str(Numbers.description_max_length) + ' characters long'
    seo_error_name_length: str = 'Length must be: ' + str(Numbers.article_name_min_length) + ' - ' + str(
        Numbers.article_name_max_length) + ' characters long'
    seo_error_default_value: str = 'Default value can not be used'
    seo_error_date_format: str = 'Date format incorrect (example: 31. Ledna 2020)'
    seo_error_date_format_day: str = 'Date format incorrect, day must be: 1-31'
    seo_error_date_format_year: str = 'Date format incorrect, year must be: ' + str(Numbers.year_min) + ' - ' + str(
        Numbers.year_max)
    seo_error_image_caption_length: str = 'Length must be: ' + str(Numbers.article_image_caption_min) + ' - ' + str(
        Numbers.article_image_caption_max) + ' characters long'
    seo_error_link_title_length: str = 'Length must be: ' + str(Numbers.article_image_title_min) + ' - ' + str(
        Numbers.article_image_title_max) + ' characters long'
    seo_error_image_alt_length: str = 'Length must be: ' + str(Numbers.article_image_alt_min) + ' - ' + str(
        Numbers.article_image_alt_max) + ' characters long'
    seo_check: str = 'SEO Check:'

    label_menu_file: str = 'File'
    label_menu_item_open: str = 'Open directory...\tctrl+o'
    label_menu_item_open_hint: str = 'Open a whitebear web directory'
    label_menu_item_reload: str = 'Reload file from disk\tctrl+r'
    label_menu_item_reload_hint: str = 'Parse file again from disk'

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
    label_menu_logo_link_title_placeholder: str = ' Link title'
    label_article_image: str = 'Article image'
    label_article_image_alt: str = 'Image alt description'
    label_article_image_link_title: str = 'Image link title'
    label_article_image_caption: str = 'Image caption'
    label_article_date: str = 'Date'
    label_article_title: str = 'Article name'
    label_article_keywords: str = 'Meta keywords'
    label_article_description: str = 'Meta description'
    label_article_info: str = 'Article data'
    label_article_photo_column: str = 'Photos'

    status_loading: str = 'Loading'
    status_ready: str = 'Ready'
    status_error: str = 'Error'
    status_warning: str = 'Warning'
    status_valid: str = 'Valid:'
    status_invalid: str = 'Invalid:'
    status_articles: str = 'Articles:'
    status_ok: str = 'Ok'

    toolbar_new_file: str = 'New file'

    button_close: str = 'Close'