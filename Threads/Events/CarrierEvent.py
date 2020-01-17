import wx


class CarrierEvent(wx.PyCommandEvent):
    """
    This event can carry any kind of payload between the other parts of the program in other threads
    and the main gui thread.
    """

    def __init__(self, event_type, event_id, payload=None):
        """
        Construct the event and store the passed values.
        :param event_type: Event type.
        :param event_id: Event ID.
        :param payload: Any kind of value to carry.
        """
        wx.PyCommandEvent.__init__(self, event_type, event_id)
        self._type = event_type
        self._id = event_id
        self._payload = payload

    def get_value(self):
        """
        Returns the value from the event.
        @return: the value of this event
        """
        return self._payload

    def __str__(self) -> str:
        return "Carrier event id: {}, type: {}, value: {}".format(str(self._id), str(self._type), str(self._payload))
