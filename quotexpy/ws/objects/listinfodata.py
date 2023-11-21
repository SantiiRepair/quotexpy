"""Module for Quotex Candles websocket object."""

from quotexpy.ws.objects.base import Base


class ListInfoData(Base):
    """Class for Quotex Candles websocket object."""

    def __init__(self):
        super(ListInfoData, self).__init__()
        self.__name = "listInfoData"
        self.list_info_data_dict = {}

    def set(self, win, profit, game_state, id_number, asset):
        self.list_info_data_dict[id_number] = {"win": win, "profit": profit, "game_state": game_state, "asset": asset}
        # workaround for listinfodata sometimes key valid is asset or id_number or both
        self.list_info_data_dict.update(
            {asset: {"win": win, "profit": profit, "game_state": game_state, "asset": asset}}
        )
        # TODO implementar keepalive ids dead by long time
        # print(self.list_info_data_dict)

    def delete(self, keyId):
        try:
            del self.list_info_data_dict[keyId]
        except:
            pass

    def get(self, keyId):
        return self.list_info_data_dict[keyId]
