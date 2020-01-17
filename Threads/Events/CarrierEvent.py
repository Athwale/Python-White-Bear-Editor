from wx import wx


class CarrierEvent(wx.PyCommandEvent):
    """

    """

    def __init__(self, event_type, event_id, payload=None):
        """

        :param event_type:
        :param event_id:
        :param payload:
        """
        wx.PyCommandEvent.__init__(self, event_type, event_id)
        self._payload = payload

    def get_value(self):
        """
        Returns the value from the event.
        @return: the value of this event
        """
        return self._payload
