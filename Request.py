from datetime import datetime


class Request(object):

    def __init__(self, begin_, end_, id_, status_, manager_, engineer_, warranty_, request_state_, client_):
        self.data_begin = datetime.strptime(begin_, '%d.%m.%Y %H:%M:%S')
        if end_ is not None:
            self.data_end = datetime.strptime(end_, '%d.%m.%Y %H:%M:%S')
        else:
            self.data_end = ''
        self.request_id = id_
        self.request_state = request_state_
        self.manager = manager_
        self.engineer = engineer_
        self.warranty = warranty_
        self.status = status_
        self.client = client_

    # пока что без менеджеров и инженеров
    def get(self):
        return [self.data_begin, self.data_end, self.request_id, self.request_state, self.warranty, self.status,
                self.manager, self.client]
