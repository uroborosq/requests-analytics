from datetime import datetime


class Request(object):

    def __init__(self, begin_, begin_working_, end_, id_, status_, manager_, engineer_, warranty_, request_state_,
                 client_, address_, model_, priority_):
        self.date_begin = datetime.strptime(begin_, '%d.%m.%Y %H:%M:%S')
        if end_ is not None:
            self.date_end = datetime.strptime(end_, '%d.%m.%Y %H:%M:%S')
        else:
            self.date_end = ''
        self.id = id_
        self.phase = request_state_
        self.manager = manager_
        self.engineer = [engineer_]
        self.warranty = warranty_
        self.status = status_
        self.client = client_
        self.address = address_
        self.model = model_
        self.priority = priority_
        if begin_working_ is not None:
            self.begin_working = datetime.strptime(begin_working_, '%d.%m.%Y %H:%M:%S')
        else:
            self.begin_working = ''

    def add_engineer(self, engineer_):
        self.engineer.append(engineer_)
