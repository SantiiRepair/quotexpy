class CandlesPeriod:
    FIVE_SECONDS = 5
    TEN_SECONDS = 10
    FIFTEEN_SECONDS = 15
    THIRTY_SECONDS = 30
    ONE_MINUTE = 60
    TWO_MINUTES = 120
    THREE_MINUTES = 180
    FIVE_MINUTES = 300
    TEN_MINUTES = 600
    FIFTEEN_MINUTES = 900
    THIRTY_MINUTES = 1800
    ONE_HOUR = 3600
    FOUR_HOURS = 14400
    ONE_DAY = 86400

    @classmethod
    def get_allowed_periods(cls):
        return [
            cls.FIVE_SECONDS,
            cls.TEN_SECONDS,
            cls.FIFTEEN_SECONDS,
            cls.THIRTY_SECONDS,
            cls.ONE_MINUTE,
            cls.TWO_MINUTES,
            cls.THREE_MINUTES,
            cls.FIVE_MINUTES,
            cls.TEN_MINUTES,
            cls.FIFTEEN_MINUTES,
            cls.THIRTY_MINUTES,
            cls.ONE_HOUR,
            cls.FOUR_HOURS,
            cls.ONE_DAY,
        ]
