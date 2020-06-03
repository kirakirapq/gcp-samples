# coding: utf-8

class Profile(object):
    def __init__(
            self: str,
            first_name: str,
            last_name: str,
            age: str,
            favorite: str):
        """[summary]

        Arguments:
            self {str} -- [description]
            first_name {str} -- [description]
            last_name {str} -- [description]
            age {str} -- [description]
            favorite {str} -- [description]
        """
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.favorite = favorite

    @staticmethod
    def from_dict(source):
        """[summary]

        Arguments:
            source {[dict]} -- [description]

        Returns:
            [Peofile] -- [description]
        """
        # [START_EXCLUDE]
        profile = Peofile(
            source['first_name'],
            source['last_name'],
            source['age'],
            source['favorite'])

        return profile

    def to_dict(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        dest = {
            'name': {
                'first_name': self.first_name,
                'last_name': self.last_name
            },
            'age': self.age,
            'favorite': self.favorite
        }

        return dest
