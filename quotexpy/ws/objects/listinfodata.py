"""Module for Quotex Candles websocket object."""

from quotexpy.ws.objects.base import Base


class ListInfoData(Base):
    """Class for Quotex Candles websocket object."""

    def __init__(self):
        super(ListInfoData, self).__init__()
        self.__name = "listInfoData"
        self.list_info_data_dict = {}

    def set(self, win, profit, game_state, id_number, asset, openTimestamp, closeTimestamp):
        #self.list_info_data_dict[id_number] = {
        #    "win": win,
        #    "profit": profit,
        #    "game_state": game_state,
        #    "asset":asset,
        #    "openTimestamp": openTimestamp,
        #    "closeTimestamp": closeTimestamp,
        #}
        self.list_info_data_dict[asset] = {
            "win": win,
            "profit": profit,
            "game_state": game_state,
            "asset":asset,
            "openTimestamp": openTimestamp,
            "closeTimestamp": closeTimestamp,
        }

    def delete(self, id_number):
        try:
            del self.list_info_data_dict[id_number]
        except:
            pass
    def get(self, id_number):
        return self.list_info_data_dict[id_number]
