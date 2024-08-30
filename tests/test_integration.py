import unittest

from .test_postgresql import TestPostGresql
from .test_mongodb import TestMongoDB
from .test_mysql import TestMySQLDatabase, TestMariaDBDatabase
from .test_pwman import suite


def complete_suite(suite):

    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestPostGresql))
    suite.addTest(loader.loadTestsFromTestCase(TestMySQLDatabase))
    suite.addTest(loader.loadTestsFromTestCase(TestMariaDBDatabase))
    suite.addTest(loader.loadTestsFromTestCase(TestMongoDB))

    return suite


if __name__ == '__main__':
    import os
    test_suite = complete_suite(suite())
    unittest.TextTestRunner(verbosity=2,
                            failfast=int(os.getenv("PWMAN_FAILFAST", "1"))).run(test_suite)
