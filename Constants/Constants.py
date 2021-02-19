import os.path

from wx import Colour


class Numbers:
    RED_COLOR = Colour(242, 207, 206)
    GREEN_COLOR = Colour(201, 255, 199)
    YELLOW_COLOR = Colour(250, 255, 196)
    BLUE_COLOR = Colour(145, 207, 255)

    # Turn link sanity check on/off.
    online_seo_test: bool = False

    three_click_timeout: int = 400
    photo_ratio: float = 4 / 3
    photo_ratio_tolerance: float = 0.01

    minimal_window_size_width: int = 1200
    minimal_window_size_height: int = 700
    initial_panel_size: int = 220
    minimal_panel_size: int = 150
    maximal_panel_size: int = 300
    text_field_font_size: int = 9
    widget_border_size: int = 3
    photo_column_width: int = 306
    edit_aside_image_dialog_width: int = 900
    edit_aside_image_dialog_height: int = 340
    edit_text_image_dialog_width: int = 1200
    edit_text_image_dialog_height: int = 300
    edit_video_dialog_width: int = 600
    edit_video_dialog_height: int = 210
    edit_link_dialog_height: int = 255
    edit_menu_item_dialog_height: int = 300
    add_image_dialog_width: int = 1000
    add_logo_dialog_width: int = 500
    add_logo_dialog_height: int = 220
    icon_width: int = 30
    icon_height: int = 30
    color_icon_width: int = 15
    color_icon_height: int = 15
    splashscreen_dialog_size: (int, int) = (300, 337)

    # Styling
    main_heading_size = 18
    heading_3_size: int = 16
    heading_4_size: int = 14
    paragraph_spacing: int = 20
    paragraph_font_size: int = 11
    image_spacing: int = 10
    list_spacing: int = 10
    list_left_indent: int = 50
    list_left_sub_indent: int = 45

    # SEO values
    year_min: int = 2000
    year_max: int = 3000
    menu_logo_image_size: int = 96
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
    menu_name_min_length: int = 3
    menu_name_max_length: int = 31
    article_image_caption_min: int = 5
    article_image_caption_max: int = 255
    article_image_title_min: int = 5
    article_image_title_max: int = 512
    article_image_alt_min: int = 5
    article_image_alt_max: int = 125
    video_width: int = 534
    video_height: int = 405
    original_image_max_width: int = 2000


class Strings:
    """
    This class holds string variables which are used in the program. This simplifies changes.
    """
    color_black: str = 'black'
    cz_months = '|'.join(
        ['Ledna', 'Února', 'Března', 'Dubna', 'Května', 'Června', 'Července', 'Srpna', 'Září', 'Října', 'Listopadu',
         'Prosince'])
    extension_jpg: str = '.jpg'
    extension_png: str = '.png'
    image_extensions: str = 'JPG files (*' + extension_jpg + ')|*' + extension_jpg + \
                            '|PNG files (*' + extension_png + ')|*' + extension_jpg + ''
    image_jpg_only: str = 'JPG files (*' + extension_jpg + ')|*' + extension_jpg
    home_directory: str = os.path.expanduser('~')
    editor_config_file: str = os.path.join(home_directory, '.whitebearEditor.conf')
    editor_output_debug_file: str = os.path.join(home_directory, 'whitebearEditor.log')
    editor_name: str = 'Whitebear editor'
    page_name: str = 'white-bear'
    editor_version: str = '0.1'
    url_stub: str = 'https://www.'
    folder_images: str = 'images'
    folder_logos: str = 'logos'
    folder_originals: str = 'original'
    folder_thumbnails: str = 'thumbnails'

    text_about_contents: str = '<p>Unfinished whitebear web editor.<br>' \
                               '<i>https://github.com/Athwale/Python-White-Bear-Editor</i><br>' \
                               'version: <b>' + editor_version + '</b></p>'
    text_reload_from_disk: str = 'Reload file from disk?\nThis will discard all unsaved changes.'
    text_remove_image: str = 'Remove image from side panel?'

    exception_access: str = 'Main directory not readable'
    exception_access_html: str = 'File can not be accessed'
    exception_access_css: str = 'File styles.css missing'
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
    exception_unrecognized_color: str = 'Unrecognized CSS color'
    exception_wrong_style: str = 'Unrecognized style'
    exception_incorrect_url: str = 'Incorrect url'

    seo_error_keywords_length: str = 'Length must be: ' + str(Numbers.keywords_min_length) + ' - ' + str(
        Numbers.keywords_max_length) + ' characters long'
    seo_error_description_length: str = 'Length must be: ' + str(
        Numbers.description_min_length) + ' - ' + str(Numbers.description_max_length) + ' characters long'
    seo_error_name_length: str = 'Length must be: ' + str(Numbers.article_name_min_length) + ' - ' + str(
        Numbers.article_name_max_length) + ' characters long'
    seo_error_menu_name_length: str = 'Length must be: ' + str(Numbers.menu_name_min_length) + ' - ' + str(
        Numbers.menu_name_max_length) + ' characters long'
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
    seo_error_url_nonexistent: str = 'Target page does not exist'
    seo_error_url_malformed: str = 'Url syntax error'
    seo_error_video_size_wrong: str = 'The size of the video element is incorrect'
    seo_check: str = 'SEO Check:'

    warning_name_incorrect: str = 'Incorrect name\nDo not use file extension\nDo not use special characters'
    warning_file_exists: str = 'File already exists. Overwrite?'
    warning_aside_impossible: str = 'Aspect ratio must be 4/3 for aside or main image'
    warning_wrong_image_folder: str = 'Images must come from whitebear thumbnails folder'
    warning_wrong_logo_folder: str = 'Menu image must come from whitebear logos folder'
    warning_wrong_logo_size: str = 'Menu image must be ' + str(Numbers.menu_logo_image_size) + 'x' + \
                                   str(Numbers.menu_logo_image_size) + 'px'
    warning_not_square: str = 'Menu image must be square'

    label_menu_file: str = 'File'
    label_menu_item_new: str = 'New document...\tctrl+n'
    label_menu_item_new_hint: str = 'Create a new document'
    label_menu_item_open: str = 'Open directory...\tctrl+o'
    label_menu_item_open_hint: str = 'Open a whitebear web directory'
    label_menu_item_save: str = 'Save document\tctrl+s'
    label_menu_item_save_hint: str = 'Save current document'
    label_menu_item_reload: str = 'Reload file from disk'
    label_menu_item_reload_hint: str = 'Parse file again from disk'
    label_menu_item_upload: str = 'Upload all changes...'
    label_menu_item_upload_hint: str = 'Upload all modified documents'

    label_menu_item_quit: str = 'Quit\tctrl+q'
    label_menu_item_quit_hint: str = 'Quit editor'

    label_menu_help: str = 'Help'
    label_menu_item_about: str = 'About'
    label_menu_item_about_hint: str = 'About whitebear editor'

    label_menu_edit: str = 'Edit'
    label_menu_item_undo: str = 'Undo\tctrl+u'
    label_menu_item_undo_hint: str = 'Undo last change'
    label_menu_item_redo: str = 'Redo\tctrl+r'
    label_menu_item_redo_hint: str = 'Redo last change'
    label_menu_item_cut: str = 'Cut\tctrl+x'
    label_menu_item_cut_hint: str = 'Cut'
    label_menu_item_copy: str = 'Copy\tctrl+c'
    label_menu_item_copy_hint: str = 'Copy'
    label_menu_item_paste: str = 'Paste\tctrl+v'
    label_menu_item_paste_hint: str = 'Paste'
    label_menu_item_select_all: str = 'Select all\tctrl+a'
    label_menu_item_select_all_hint: str = 'Select all'

    label_menu_add: str = 'Add'
    label_menu_item_add_text_image: str = 'Add image to collection\tctrl+i'
    label_menu_item_add_text_image_hint: str = 'Add text image'
    label_menu_item_add_logo: str = 'Add menu logo to collection\tctrl+l'
    label_menu_item_add_logo_hint: str = 'Add menu logo'
    label_menu_item_add_side_image: str = 'Add aside image into document\tctrl+p'
    label_menu_item_add_side_image_hint: str = 'Insert aside image'

    # Pop up menu items
    label_menu_up: str = 'Move up'
    label_menu_down: str = 'Move Down'
    label_menu_remove: str = 'Remove'

    label_dialog_choose_wb_dir: str = 'Choose whitebear directory'
    label_dialog_about: str = 'About'
    label_dialog_edit_image: str = 'Edit image'
    label_dialog_edit_link: str = 'Edit link'
    label_dialog_edit_video: str = 'Edit video'
    label_dialog_edit_menu_item: str = 'Edit menu item'
    label_dialog_add_image: str = 'Add image'
    label_dialog_add_logo: str = 'Add menu logo'

    label_article_menu_logo: str = 'Menu logo'
    label_article_menu_logo_name_placeholder: str = 'Menu item name'
    label_article_menu_logo_alt_placeholder: str = 'Alt description'
    label_menu_logo_link_title_placeholder: str = 'Link title'
    label_menu_item_name: str = 'Menu name'
    label_article_image: str = 'Article image'
    label_article_image_alt: str = 'Image alt description'
    label_article_image_link_title: str = 'Image link title'
    label_video_link_title: str = 'Video link title'
    label_article_image_caption: str = 'Image caption'
    label_article_date: str = 'Date'
    label_article_title: str = 'Article name'
    label_article_keywords: str = 'Meta keywords'
    label_article_description: str = '   Meta description'
    label_article_info: str = 'Article metadata'
    label_article_photo_column: str = 'Photos'
    label_image: str = 'Image'
    label_image_path: str = 'Full image'
    label_image_thumbnail_path: str = 'Thumbnail'
    label_caption: str = 'Caption'
    label_link_title: str = 'Link title'
    label_alt_description: str = 'Alt description'
    label_none: str = 'None'
    label_open_in_new_page: str = 'Opens in new page'
    label_url: str = 'URL'
    label_text: str = 'Text'
    label_target: str = 'Target'
    label_size: str = 'Size'
    label_name: str = 'Name'
    label_link_local: str = 'WhiteBear page'
    label_thumbnail_size: str = 'Thumbnail size'
    label_original_size: str = 'Original size'
    label_full_size: str = 'Full image size'
    label_video_size: str = 'Video size'
    label_filelist: str = 'Files'
    label_styles: str = 'Styles'
    label_logo: str = 'logo'
    label_select_image: str = 'Select image'
    label_target_section: str = 'Section'
    label_text_image: str = 'Text image (width ' + str(Numbers.text_image_max_size) + 'px)'
    label_aside_image: str = 'Aside/Main image (' + str(Numbers.main_image_width) + 'x' + \
                             str(Numbers.main_image_height) + 'px)'
    label_image_name: str = 'Image name'
    label_url_error: str = 'URL Error'
    label_red_url_warning: str = 'Document contains incorrect URL'

    status_loading: str = 'Loading and testing'
    status_ready: str = 'Ready'
    status_error: str = 'Error'
    status_warning: str = 'Warning'
    status_valid: str = 'Valid:'
    status_invalid: str = 'Invalid:'
    status_articles: str = 'Articles:'
    status_ok: str = 'Ok'
    status_none: str = 'None'
    status_found: str = 'Found'

    style_paragraph: str = 'Paragraph'
    style_heading_3: str = 'Title 3'
    style_heading_4: str = 'Title 4'
    style_list: str = 'List'
    style_image: str = 'Image'
    style_url: str = 'Url'
    style_clear: str = 'Clear'

    toolbar_new_file: str = 'New file'
    toolbar_bold: str = 'Bold'
    toolbar_insert_img: str = 'Insert image'
    toolbar_insert_video: str = 'Insert video'
    toolbar_insert_link: str = 'Insert link'
    toolbar_save: str = 'Save'
    toolbar_color: str = 'Color text'

    button_close: str = 'Close'
    button_cancel: str = 'Cancel'
    button_ok: str = 'Ok'
    button_remove_link: str = 'Remove link'
    button_browse: str = 'Browse'
    button_save: str = 'Save'

    undo_last_action: str = 'Last action'
    undo_bold: str = 'Undo bold text'

    flag_no_save: str = 'dont_save'
    field_type: str = 'type'
    field_video: str = 'video'
    field_image: str = 'image'
