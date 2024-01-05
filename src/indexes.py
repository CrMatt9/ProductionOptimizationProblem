class Index(tuple):
    def __new__(cls, seq, **kwargs):
        return super(Index, cls).__new__(cls, tuple(seq))

    def __init__(self, seq, **kwargs):
        self.__dict__.update(kwargs)
