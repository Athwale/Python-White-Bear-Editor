import wx


class CarrierEvent(wx.PyCommandEvent):
    """
    This event can carry any kind of payload between the other parts of the program in other threads
    and the main gui thread.
    """

    def __init__(self, event_type, event_id, payload_type, payload=None):
        """
        Construct the event and store the passed values.
        :param event_type: Event type.
        :param event_id: Event ID.
        :param payload: Any kind of value to carry.
        :param payload_type: Identifies what is this event carrying
        """
        wx.PyCommandEvent.__init__(self, event_type, event_id)
        self._type = event_type
        self._id = event_id
        self._payload = payload
        self._payload_type = payload_type

    def get_value(self):
        """
        Returns the value from the event.
        @return: the value of this event
        """
        return self._payload

    def get_payload_type(self) -> int:
        """
        Get this payload type
        :return: int Payload identifier
        """
        return self._payload_type

    def __str__(self) -> str:
        return "Carrier event id: {}, type: {}, value: {}, payload_type: {}".format(str(self._id), str(self._type),
                                                                                    str(self._payload),
                                                                                    str(self._payload_type))
