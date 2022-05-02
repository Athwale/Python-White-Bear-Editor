import threading
from typing import List

import wx
from Tools.Tools import Tools


class OptimizerThread(threading.Thread):
    """
    Optimizes jpg and png image files and overwrites them on disk.
    """

    def __init__(self, parent, files: List[str]):
        """
        Image optimizer thread constructor.
        :param files: List of file paths to upload
        """
        threading.Thread.__init__(self)
        self._parent = parent
        self._stop_event = threading.Event()
        self._files_to_optimize = files
        self._files_done: int = 0

    def run(self) -> None:
        """
        Overrides Thread.run. Don't call this directly its called internally when you call Thread.start().
        :return: None, this method calls the wx.CallAfter to pass results back into GUI.
        """
        error = False
        for file in self._files_to_optimize:
            # Show which file is being uploaded.
            wx.CallAfter(self._parent.on_file_optimization, file)
            if self._stop_event.is_set():
                break
            try:
                Tools.optimize_image(file)
                self._files_done += 1
                wx.CallAfter(self._parent.on_optimization_done, self._files_done)
            except OSError as e:
                # OSError is raised when the file could not be completely written.
                wx.CallAfter(self._parent.on_optimization_fail, f'{file} {e}')
                error = True
        wx.CallAfter(self._parent.on_optimization_finished, error)

    def stop(self) -> None:
        """
        Stop the execution of this thread at the end of the previous upload operation.
        :return: None
        """
        self._stop_event.set()
