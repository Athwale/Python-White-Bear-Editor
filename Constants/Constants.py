import os.path

import wx.lib.newevent
from wx import Colour


class Events:
    TextChangedEvent, EVT_DOCUMENT_TEXT_CHANGED = wx.lib.newevent.NewCommandEvent()
    SidepanelChangedEvent, EVT_DOCUMENT_IMAGES_CHANGED = wx.lib.newevent.NewCommandEvent()
    SpellcheckEvent, EVT_SPELLCHECK_DONE = wx.lib.newevent.NewCommandEvent()
    RecolorAllEvent, EVT_RECOLOR_ALL = wx.lib.newevent.NewCommandEvent()


class Numbers:
    ID_MENU_LOGO = wx.NewId()
    ID_MAIN_IMAGE = wx.NewId()
    ID_SIDE_IMAGE = wx.NewId()
    ID_SPELLCHECK_TEST = wx.NewId()
    ID_IMAGE_LINK = wx.NewId()
    ID_IMAGE_ALT = wx.NewId()
    ID_NEW_DIR = wx.NewId()
    ID_UPLOAD = wx.NewId()
    ID_EXPORT_ALL = wx.NewId()
    ID_EDIT_ROBOTS = wx.NewId()
    ID_EDIT_CSS = wx.NewId()
    ID_EDIT_MENU = wx.NewId()
    ID_NONE_ITEM = wx.NewId()

    RED_COLOR = Colour(242, 207, 206)
    GREEN_COLOR = Colour(201, 255, 199)
    DARK_GREEN_COLOR = Colour(21, 112, 49)
    YELLOW_COLOR = Colour(250, 255, 196)
    BLUE_COLOR = Colour(145, 207, 255)
    LIGHT_GREY_COLOR = Colour(235, 235, 235)

    blank_character = '\u2800'
    private_key_permissions: oct = 0o600
    connection_timeout: int = 5
    put_timeout: int = 20
    online_test_timeout: int = 10
    context_chars: int = 40

    three_click_timeout: int = 600
    spellcheck_timeout: int = 3000
    test_timeout: int = 200
    photo_ratio: float = 4 / 3
    photo_ratio_tolerance: float = 0.01

    min_keywords: int = 3
    minimal_window_size_width: int = 1200
    minimal_window_size_height: int = 700
    initial_panel_size: int = 220
    minimal_panel_size: int = 150
    maximal_panel_size: int = 300
    small_font_size: int = 9
    widget_border_size: int = 3
    photo_column_width: int = 306
    edit_aside_image_dialog_width: int = 900
    edit_aside_image_dialog_height: int = 365
    edit_text_image_dialog_width: int = 1200
    edit_text_image_dialog_height: int = 300
    edit_video_dialog_width: int = 600
    edit_video_dialog_height: int = 230
    edit_link_dialog_width: int = 900
    edit_link_dialog_height: int = 295
    edit_menu_item_dialog_height: int = 315
    add_image_dialog_width: int = 1000
    add_image_dialog_height: int = 360
    add_logo_dialog_width: int = 500
    add_logo_dialog_height: int = 235
    page_setup_dialog_width: int = 900
    page_setup_dialog_height: int = 860
    new_file_dialog_width: int = 600
    new_file_dialog_height: int = 440
    edit_menu_dialog_width: int = 600
    edit_menu_dialog_height: int = 352
    about_dialog_width: int = 550
    about_dialog_height: int = 250
    saving_dialog_width: int = 350
    upload_dialog_height: int = 630
    upload_dialog_width: int = 800
    plain_text_dialog_height: int = 630
    plain_text_dialog_width: int = 800
    upload_filelist_width: int = 300
    saving_dialog_height: int = 85
    icon_width: int = 34
    icon_height: int = 34
    color_icon_width: int = 20
    color_icon_height: int = 20
    splashscreen_dialog_size: (int, int) = (350, 350)
    spellcheck_dialog_width: int = 500
    spellcheck_dialog_height: int = 357
    spellcheck_setup_dialog_width: int = 570
    spellcheck_setup_dialog_height: int = 257

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
    aside_thumbnail_width: int = 211
    aside_thumbnail_height: int = 158
    video_width: int = 534
    video_height: int = 405
    original_image_max_width: int = 2000
    min_news: int = 0
    max_news: int = 30
    default_news: int = 3
    max_index_images: int = 4
    default_max_length: int = 256


class Strings:
    """
    This class holds string variables which are used in the program. This simplifies changes.
    """
    color_black: str = 'black'
    blank: str = '_blank'
    cz_months = '|'.join(
        ['Ledna', 'Února', 'Března', 'Dubna', 'Května', 'Června', 'Července', 'Srpna', 'Září', 'Října', 'Listopadu',
         'Prosince'])
    menu_title_stump: str = 'Menu'
    author: str = 'Whitebear'
    extension_jpg: str = '.jpg'
    extension_png: str = '.png'
    extension_html: str = '.html'
    extension_dict: str = '.dic'
    extension_excl: str = '.exc'
    contact_file: str = 'contact.png'
    contact_default_alt: str = 'kontakt'
    home_page: str = 'Hlavní strana'
    image_extensions: str = f'JPG and PNG files (*{extension_jpg};*{extension_png})|*.[jJ][pP][gG];*.[pP][nN][gG]|' \
                            f'PNG files (*{extension_png})|*{extension_png}'
    image_jpg_only: str = 'JPG files (*' + extension_jpg + ')|*' + extension_jpg
    html_wildcard: str = 'HTML files (*' + extension_html + ')|*' + extension_html
    default_file: str = 'untitled'
    home_directory: str = os.path.expanduser('~')
    editor_config_file: str = os.path.join(home_directory, '.config', 'whitebearEditor.yml')
    editor_output_debug_file: str = os.path.join(home_directory, 'whitebearEditor.log')
    editor_name: str = 'Whitebear editor'
    page_name: str = 'white-bear'
    url_stub: str = 'https://www.'
    folder_images: str = 'images'
    folder_logos: str = 'logos'
    folder_originals: str = 'original'
    folder_thumbnails: str = 'thumbnails'
    folder_files: str = 'files'
    article: str = 'article'
    menu: str = 'menu'
    index: str = 'index'
    file: str = 'File'
    robots_file: str = 'robots.txt'
    css_file: str = 'styles.css'
    file_background: str = 'background.jpg'
    file_header: str = 'logo-nadpis.png'
    test_url: str = 'http://www.example.com'

    # Sitemap settings
    sitemap_file: str = 'sitemap.xml'
    sitemap_keyword: str = 'Sitemap:'
    sitemap_xmlns: str = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    change_frequency: str = 'monthly'

    editor_version: str = '0.2'
    text_about_contents: str = '<p>Unfinished whitebear web editor.<br>' \
                               '<i>https://github.com/Athwale/Python-White-Bear-Editor</i><br>' \
                               'version: <b>' + editor_version + '</b></p>'
    text_reload_from_disk: str = 'Reload file from disk?\nThis will discard all unsaved changes.'
    text_remove_image: str = 'Remove image from side panel?'

    exception_access: str = 'Working directory not accessible'
    exception_access_html: str = 'File can not be accessed'
    exception_access_css: str = 'File styles.css missing'
    exception_index: str = 'index.html is not in directory'
    exception_not_white_bear: str = 'Not a white Bear web directory'
    exception_file_unrecognized: str = 'Unrecognized or malformed white-bear html file:'
    exception_conf_inaccessible: str = 'Configuration file is inaccessible'
    exception_resource_not_found: str = 'Resource not found'
    exception_html_syntax_error: str = 'Syntax error in html file'
    exception_schema_syntax_error: str = 'Syntax error in xsd file'
    exception_parse_multiple_descriptions: str = 'Only one meta description tag is allowed'
    exception_parse_multiple_keywords: str = 'Only one meta keywords tag is allowed'
    exception_parse_multiple_authors: str = 'Only one meta author tag is allowed'
    exception_last_document_missing: str = 'Last open document not found'
    exception_menu_item_missing: str = 'Menu item missing'
    exception_unrecognized_color: str = 'Unrecognized CSS color'
    exception_wrong_style: str = 'Unrecognized style'
    exception_incorrect_url: str = 'Incorrect url'
    exception_default_value_not_set: str = 'Page setup is incomplete'
    exception_bug: str = 'BUG Generated html failed validation'
    exception_sftp_fail: str = 'Transfer failed'
    exception_broken_html: str = 'Corrupted html code'
    exception_reserved_blue: str = 'Blue color reserved for urls detected in CSS'

    seo_error_length: str = 'Required length'
    seo_error_keywords_length: str = f'Length must be: {Numbers.keywords_min_length} -' \
                                     f' {Numbers.keywords_max_length} characters long'
    seo_error_keywords_format: str = 'Must be a comma separated list'
    seo_error_keywords_amount: str = 'Too few keywords'
    seo_error_description_length: str = f'Length must be: {Numbers.description_min_length} - ' \
                                        f'{Numbers.description_max_length} characters long'
    seo_error_name_length: str = f'Length must be: {Numbers.article_name_min_length} - ' \
                                 f'{Numbers.article_name_max_length} characters long'
    seo_error_menu_name_length: str = f'Length must be: {Numbers.menu_name_min_length} - ' \
                                      f'{Numbers.menu_name_max_length} characters long'
    seo_error_default_value: str = 'Default value can not be used'
    seo_error_date_format: str = 'Date format incorrect (example: 31. Ledna 2020)'
    seo_error_date_format_day: str = 'Date format incorrect, day must be: 1 - 31'
    seo_error_date_format_year: str = f'Date format incorrect, year must be: {Numbers.year_min} - {Numbers.year_max}'
    seo_error_image_caption_length: str = f'Length must be: {Numbers.article_image_caption_min} - ' \
                                          f'{Numbers.article_image_caption_max} characters long'
    seo_error_link_title_length: str = f'Length must be: {Numbers.article_image_title_min} - ' \
                                       f'{Numbers.article_image_title_max} characters long'
    seo_error_image_alt_length: str = f'Length must be: {Numbers.article_image_alt_min} - ' \
                                      f'{Numbers.article_image_alt_max} characters long'
    seo_error_url_nonexistent: str = 'Target page does not exist'
    seo_error_url_malformed: str = 'Url syntax error'
    seo_error_video_size_wrong: str = 'The size of the video element is incorrect'
    seo_error_video_embed: str = 'Url is not an embedded video'
    seo_error_index_length: str = 'Index page seo error text length wrong'
    seo_error_index_empty: str = 'Index page seo error text not set'
    seo_error_not_empty: str = 'Can not be empty'
    seo_check: str = 'Test:'

    spelling_error: str = 'Spellcheck warning'

    warning_name_incorrect: str = 'Incorrect name\nDo not use file extension\nDo not use special characters'
    warning_file_exists_overwrite: str = 'File already exists. Overwrite?'
    warning_file_exists: str = 'File already exists'
    warning_aside_impossible: str = 'Aspect ratio must be 4/3 for aside or main image'
    warning_wrong_image_folder: str = 'Images must come from whitebear thumbnails folder'
    warning_wrong_logo_folder: str = 'Menu image must come from whitebear logos folder'
    warning_wrong_logo_size: str = f'Menu image must be {Numbers.menu_logo_image_size}x{Numbers.menu_logo_image_size}px'
    warning_not_square: str = 'Menu image must be square'
    warning_can_not_save: str = 'Can not save to disk.'
    warning_empty: str = 'Name can not be empty'
    warning_last_document_not_found: str = 'Last document not found'
    warning_delete_document: str = 'Delete file:'
    warning_can_not_delete: str = 'Unable to delete'
    warning_must_be_empty: str = 'New directory must be empty'
    warning_new_dir_created: str = 'New directory created.\n' \
                                   'Please add custom files.\n' \
                                   'favicon.ico, 404.html, google tracking page...'
    warning_unsaved: str = 'At least one document is not saved or uploaded.\nQuit anyway?'
    warning_new_dir_unsaved: str = 'At least one document is not saved.\nContinue?'
    warning_file_inaccessible: str = 'Can not access file'
    warning_incorrect_format: str = 'Incorrect format'
    warning_incorrect_ip_format: str = 'Incorrect IP format'
    warning_incorrect_port: str = 'Incorrect port number'
    warning_keyfile_inaccessible: str = 'Key file inaccessible'
    warning_keyfile_permissions: str = 'Key file must have 600 permissions'
    warning_rsa_passphrase: str = 'RSA passphrase'
    warning_rsa_passphrase_wrong: str = 'Wrong password'
    warning_rsa_encryption_fail: str = 'Encryption failure'
    warning_server_folders_repaired: str = 'Server folder structure repaired'
    warning_upload_unfinished: str = 'Upload has not finished.\nDo you want to force disconnect?\nThis may ' \
                                     'leave damaged files on the server.'
    warning_paste_into_url: str = 'Can not paste multiple paragraphs into url'
    warning_fatal_invalidity: str = '(Some required file(s) invalid)'
    warning_no_mistake: str = 'Self test OK'
    warning_errors_in_document: str = 'Problems found in'
    warning_main_image: str = 'Main article image'
    warning_aside_image: str = 'Side images'
    warning_text_image: str = 'Images in text'
    warning_text_video: str = 'Videos in text'
    warning_text_link: str = 'Url in text'
    warning_menu_item: str = 'Menu logo'
    warning_text_spelling: str = 'Website text spellcheck'
    warning_menu_page: str = 'Menu page'
    warning_index: str = 'Index page (Page setup)'
    warning_file_missing: str = 'File not found:'

    label_menu_file: str = 'File'
    label_menu_file_recent: str = 'Open recent directory'
    label_menu_item_new: str = 'New document...\tctrl+n'
    label_menu_item_new_hint: str = 'Create a new document'
    label_menu_item_open: str = 'Open directory...\tctrl+o'
    label_menu_item_open_hint: str = 'Open a whitebear web directory'
    label_menu_item_save: str = 'Save document\tctrl+s'
    label_menu_item_save_hint: str = 'Save current document'
    label_menu_item_upload: str = 'Upload all changes...\tctrl+u'
    label_menu_item_upload_hint: str = 'Upload all modified documents'
    label_menu_item_save_as: str = 'Save as...'
    label_menu_item_save_as_hint: str = 'Save as new file'
    label_menu_item_page_setup: str = 'Page setup...'
    label_menu_item_page_setup_hint: str = 'Edit main page and default values'
    label_menu_item_edit_menu: str = 'Edit menu...'
    label_menu_item_edit_menu_hint: str = 'Edit menu pages'
    label_menu_item_export_all: str = 'Export all...'
    label_menu_item_export_all_hint: str = 'Export all document into html'
    label_menu_item_delete: str = 'Delete article...'
    label_menu_item_delete_hint: str = 'Delete article and regenerate directory'
    label_menu_item_new_dir: str = 'New WhiteBear directory...'
    label_menu_item_new_dir_hint: str = 'Create a new WhiteBear directory'
    label_menu_item_online_test: str = 'Online url test'
    label_menu_item_online_test_hint: str = 'Test url existence online'

    label_menu_help: str = 'Help'
    label_menu_item_about: str = 'About...'
    label_menu_item_about_hint: str = 'About whitebear editor'

    label_menu_edit: str = 'Edit'
    label_menu_item_undo: str = 'Undo\tctrl+y'
    label_menu_item_undo_hint: str = 'Undo last change'
    label_menu_item_redo: str = 'Redo\tctrl+z'
    label_menu_item_redo_hint: str = 'Redo last change'
    label_menu_item_cut: str = 'Cut\tctrl+x'
    label_menu_item_cut_hint: str = 'Cut'
    label_menu_item_copy: str = 'Copy\tctrl+c'
    label_menu_item_copy_hint: str = 'Copy'
    label_menu_item_paste: str = 'Paste\tctrl+v'
    label_menu_item_paste_hint: str = 'Paste'
    label_menu_item_select_all: str = 'Select all\tctrl+a'
    label_menu_item_select_all_hint: str = 'Select all'
    label_menu_item_spellcheck: str = 'Check spelling...\tctrl+t'
    label_menu_item_spellcheck_hint: str = 'Run spellcheck'
    label_menu_item_spellcheck_setup: str = 'Spellcheck settings...'
    label_menu_item_spellcheck_setup_hint: str = 'Spellcheck settings'
    label_menu_item_spelling_test: str = 'Enable spellcheck'
    label_menu_item_spelling_test_hint: str = 'Enable/disable spellcheck'
    label_menu_item_edit_robots: str = 'Edit robots.txt...'
    label_menu_item_edit_robots_hint: str = 'Edit robots.txt'
    label_menu_item_edit_css: str = 'Edit styles.css...'
    label_menu_item_edit_css_hint: str = 'Edit styles.css'

    label_menu_add: str = 'Add'
    label_menu_item_add_text_image: str = 'Add image to collection...\tctrl+i'
    label_menu_item_add_text_image_hint: str = 'Add text image'
    label_menu_item_add_logo: str = 'Add menu logo to collection...\tctrl+l'
    label_menu_item_add_logo_hint: str = 'Add menu logo...'
    label_menu_item_add_side_image: str = 'Add aside image into document...\tctrl+p'
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
    label_dialog_add_image: str = 'Add image to collection'
    label_dialog_add_logo: str = 'Add menu logo'
    label_dialog_save_file: str = 'Save file'
    label_dialog_page_setup: str = 'Page setup and default values'
    label_dialog_new_document: str = 'New document'
    label_dialog_edit_menu: str = 'Edit menu'
    label_dialog_spellcheck: str = 'Spellcheck'
    label_dialog_spellcheck_main: str = 'Spellcheck: main text'
    label_dialog_spellcheck_setup: str = 'Spelling setup'
    label_dialog_edit_file: str = 'Edit file'
    label_dialog_self_test: str = 'Self test'

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
    label_article_description: str = 'Meta description'
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
    label_select_file: str = 'Select file'
    label_target_section: str = 'Section'
    label_text_image: str = f'Text image (width {Numbers.text_image_max_size}px)'
    label_aside_image: str = f'Aside/Main image ({Numbers.main_image_width}x{Numbers.main_image_height}px)'
    label_image_name: str = 'Image name'
    label_url_error: str = 'URL Error'
    label_red_url_warning: str = 'Document contains incorrect URL'
    label_global_title: str = 'Main title'
    label_main_title_tip: str = 'Title text for the\nwhite-bear page logo'
    label_author: str = 'Author'
    label_author_tip: str = 'Contents of meta author tag'
    label_contact: str = 'Contact'
    label_contact_tip: str = 'Will be displayed as an\nimage on home page'
    label_default_keywords: str = 'Keywords'
    label_default_keywords_tip: str = 'Default global meta keywords'
    label_main_meta_description: str = 'Home page meta description'
    label_menu_meta_keywords: str = 'Menu meta keywords'
    label_menu_meta_description: str = 'Menu meta description'
    label_main_description_tip: str = 'Home page meta description\ntag content'
    label_meta_description: str = 'Meta description'
    label_script: str = 'Script'
    label_script_tip: str = 'Global contents of <script> tag\nin <head>. Usually a Google\nanalytics script'
    label_main_page_text: str = 'Home page text'
    label_main_page_text_tip: str = 'Home page black text,\ndisplayed first under main\npage heading'
    label_main_page_warning: str = 'Home page warning text'
    label_main_page_warning_tip: str = 'Home page red text,\ndisplayed under black text'
    label_number_of_news: str = 'Show news'
    label_menu_name: str = 'Menu name'
    label_file_name: str = 'File name'
    label_menu_file_name: str = 'Menu file name'
    label_export_all: str = 'Export all documents to html'
    label_use_image: str = 'Use newly added image?'
    label_website_url: str = 'Url'
    label_website_url_tip: str = 'Website url e.g.\nhttp://www.white-bear.cz\nUsed for sitemap generation'
    label_saving: str = 'Saved'
    label_upload: str = 'Upload changes'
    label_files_to_upload: str = 'Files to upload'
    label_invalid_files: str = 'Invalid files'
    label_ip_port: str = 'IP:port'
    label_ip_port_tip: str = 'SFTP server IPv4:Port'
    label_sftp: str = 'SFTP - SSH file transfer protocol IPv4 configuration'
    label_user: str = 'User'
    label_user_tip: str = 'SFTP user name'
    label_key_file: str = 'Key file'
    label_key_file_tip: str = 'SFTP RSA public key'
    label_upload_information: str = 'Upload'
    label_successful_uploads: str = 'Successful transfers'
    label_failed_uploads: str = 'Failed transfers'
    label_uploading_file: str = 'Uploading'
    label_rsa_passphrase: str = 'RSA private key passphrase'
    label_connection: str = 'Connection'
    label_server_structure: str = 'The editor expects the same folder structure on the server as is in the working ' \
                                  'directory.\nExisting files on server are overwritten.'
    label_server_overwrite: str = 'Existing files on server are overwritten.'
    label_article_public: str = 'Enable article'
    label_replace_with: str = 'Replace with:'
    label_unrecognized_word: str = 'Unrecognized word:'
    label_dictionary_provider: str = 'Dictionary provider'
    label_dictionary_location: str = 'Personal dictionary'
    label_ignored_location: str = 'Ignored words'
    label_spelling_language: str = 'Spelling language'
    label_restart_required: str = 'Restart editor to apply changes'
    label_delete_images: str = 'Delete images:'

    status_loading: str = 'Loading and testing...'
    status_ready: str = 'Ready'
    status_error: str = 'Error'
    status_warning: str = 'Warning'
    status_valid: str = 'Self test OK:'
    status_articles: str = 'Articles:'
    status_ok: str = 'Ok'
    status_found: str = 'Found'
    status_saved: str = 'Saved'
    status_delete: str = 'Delete'
    status_established: str = 'Established'
    status_failed: str = 'Failed'
    status_connecting: str = 'Connecting...'
    status_closed: str = 'Closed'
    status_finished: str = 'Finished'
    status_testing_link: str = 'Testing url'
    status_seo: str = 'SEO'
    status_file: str = 'File'
    status_modified: str = 'Modified'
    status_uploaded: str = 'Uploaded'
    status_unuploaded: str = 'Unuploaded'
    status_state: str = 'State'
    status_self_test: str = 'Self test'

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
    toolbar_color: str = 'Change color'
    toolbar_browser: str = 'Open in browser'
    toolbar_self_test: str = 'Self test'

    button_close: str = 'Close'
    button_cancel: str = 'Cancel'
    button_ok: str = 'Ok'
    button_remove_link: str = 'Remove link'
    button_browse: str = 'Browse'
    button_save: str = 'Save'
    button_add: str = 'Add'
    button_upload: str = 'Upload'
    button_ignore: str = 'Ignore'
    button_ignore_all: str = 'Ignore always'
    button_replace: str = 'Replace'
    button_add_to_dict: str = 'Add to dictionary'
    button_settings: str = 'Settings'
    button_spellcheck: str = 'Spellcheck'
    button_edit_dictionary: str = 'Edit dictionary'
    button_edit_ignored_list: str = 'Edit ignored words'
    button_delete_images: str = 'Delete images'

    undo_last_action: str = 'Last action'
    undo_bold: str = 'Undo bold text'

    field_type: str = 'type'
    field_video: str = 'video'
    field_image: str = 'image'
