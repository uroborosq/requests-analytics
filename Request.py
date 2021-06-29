from datetime import datetime


class Request(object):

    def __init__(self, begin_, end_, id_, status_, type_, manager_, engineer_):
        self.data_begin = begin_
        self.data_end = end_
        self.request_id = id_
        self.status = status_
        self.type = type_
        self.manager = manager_
        self.engineer = engineer_
