import unittest
import database_manager as dm

## retrieve_or_create_user, create a new user
##
class DatabaseTestCase(unittest.TestCase):
    def __init__(self):
        dm.init_db_connection('localhost:27017/kevin-test', 'redis://localhost')

    def test_(self):

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
