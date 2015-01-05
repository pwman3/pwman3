import unittest
from . import test_pwman


def suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTests(test_pwman.suite())
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
