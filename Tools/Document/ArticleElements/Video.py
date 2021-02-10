import httplib2
import wx

from Constants.Constants import Numbers, Strings
from Resources.Fetch import Fetch


class Video:
    """
    Represents a placeholder for a youtube video in the text of the page.
    """

    def __init__(self, title: str, width: int, height: int, url: str):
        """
        Constructor for a video placeholder.
        :param title: The title of the video.
        :param width: The width of the element.
        :param height: The height of the element.
        :param url: The url of the video
        """
        self._link_title = title
        self._link_title_error_message: str = ''
        self._width = width
        self._height = height
        self._size_error_message: str = ''
        self._url = url
        self._url_error_message: str = ''
        self._status_color = None
        self._image = None
        self._modified = False

    def seo_test_self(self) -> bool:
        """
        SEO check self for correct title, url and dimensions.
        :return: True if no error is found.
        """
        # Disk paths have to be checked by the sub classes.
        # Clear all error before each retest
        self._link_title_error_message = ''
        self._url_error_message = ''
        self._size_error_message = ''
        self._status_color = wx.NullColour

        result = True
        self._image = wx.Image(Fetch.get_resource_path('video_placeholder.png'), wx.BITMAP_TYPE_PNG)
        # Check video link title
        if len(self._link_title) < Numbers.article_image_title_min or len(
                self._link_title) > Numbers.article_image_title_max:
            self._link_title_error_message = Strings.seo_error_link_title_length
            self._image = wx.Image(Fetch.get_resource_path('video_seo_error.png'), wx.BITMAP_TYPE_PNG)
            result = False

        # Check dimensions
        if self._width != Numbers.video_width or self._height != Numbers.video_height:
            self._size_error_message = Strings.seo_error_video_size_wrong
            self._image = wx.Image(Fetch.get_resource_path('video_size_incorrect.png'), wx.BITMAP_TYPE_PNG)
            result = False

        # Check url
        try:
            h = httplib2.Http()
            resp = h.request(self._url, 'HEAD')
            if int(resp[0]['status']) >= 400:
                self._url_error_message = Strings.seo_error_url_nonexistent
                self._image = wx.Image(Fetch.get_resource_path('video_seo_error.png'), wx.BITMAP_TYPE_PNG)
                result = False
        except KeyError as _:
            self._url_error_message = Strings.seo_error_url_malformed
            result = False
        except httplib2.ServerNotFoundError as _:
            self._url_error_message = Strings.seo_error_url_nonexistent
            result = False
        except ConnectionResetError as _:
            pass

        if not result:
            self._status_color = wx.RED
        return result

    # Getters ----------------------------------------------------------------------------------------------------------
    def get_image(self) -> wx.Image:
        """
        Return the placeholder image. Either correct video placeholder or error image.
        :return: Return the placeholder image. Either correct video placeholder or error image.
        """
        return self._image

    def get_title(self) -> (str, str):
        """
        Return the title of this video and any error string.
        :return: The title of this video and any error string.
        """
        return self._link_title, self._link_title_error_message

    def get_url(self) -> (str, str):
        """
        Return the url of this video and any error string.
        :return: The url of this video and any error string.
        """
        return self._url, self._url_error_message

    def get_size_error(self):
        """
        Return the element size error if there is any, empty string otherwise.
        :return: Return the element size error if there is any, empty string otherwise.
        """
        return self._size_error_message

    def get_size(self) -> (int, int):
        """
        Return the video size (width, height).
        :return: Return the video size (width, height).
        """
        return self._width, self._height

    def get_status_color(self) -> wx.Colour:
        """
        Return the status color of this video. White if ok, Red if SEO check failed.
        :return: Return the status color of this video. White if ok, Red if SEO check failed.
        """
        return self._status_color

    def is_modified(self) -> bool:
        """
        Return true if this instance was modified.
        :return: Return true if this instance was modified.
        """
        return self._modified

    # Setters ----------------------------------------------------------------------------------------------------------
    def set_title(self, title) -> None:
        """
        Set a new title for this video.
        :param title: The new title.
        :return: None
        """
        if self._link_title != title:
            self._link_title = title
            self._modified = True

    def set_url(self, url) -> None:
        """
        Set a new url for this video.
        :param url: The new url.
        :return: None
        """
        if self._url != url:
            self._url = url
            self._modified = True

    def set_modified(self, modified: bool) -> None:
        """
        Set new modified state.
        :param modified: True or False
        :return: None
        """
        self._modified = modified

    def __str__(self) -> str:
        return "Video: url: {}, title: {}, size: {} x {} px".format(self._url, self._link_title, self._width,
                                                                    self._height)
