"""Module for Quotex Candles websocket object."""

from quotexpy.ws.objects.base import Base


class ListInfoData(Base):
    """Class for Quotex Candles websocket object."""

    def __init__(self):
        super(ListInfoData, self).__init__()
        self.__name = "listInfoData"
        self.list_info_data_dict = {}

    def set(self, win, game_state, profit, id_number):
        self.list_info_data_dict[id_number] = {
            "win": win,
            "profit": profit,
            "game_state": game_state,
        }

    def delete(self, id_number):
        del self.list_info_data_dict[id_number]

    def get(self, id_number):
        return self.list_info_data_dict[id_number]
