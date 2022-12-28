from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, u_id, name, surname, address, pic_URL):
        self.u_id = u_id
        self.name = name
        self.surname = surname
        self.address = address
        self.pic_URL = pic_URL

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    @staticmethod
    def is_authenticated():
        return True

    def get_id(self):
        return self.u_id
