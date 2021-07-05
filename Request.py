from datetime import datetime


class Request(object):

    def __init__(self, begin_, end_, id_, status_, type_, manager_, engineer_):
        print(begin_ + "|" + end_)
        self.data_begin = datetime.strptime(begin_, '%d.%m.%Y %H:%M:%S')
        self.data_end = datetime.strptime(end_, '%d.%m.%Y %H:%M:%S')
        self.request_id = id_
        self.status = status_
        self.type = type_
        self.manager = manager_
        self.engineer = engineer_

    # пока что без менеджеров и инженеров
    def get(self):
        return [self.data_begin, self.data_end, self.request_id, self.status]
