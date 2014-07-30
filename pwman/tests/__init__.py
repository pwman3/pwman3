from . import test_pwman

def suite():
    import unittest
    #import doctest
    suite = unittest.TestSuite()
    #suite.addTests(doctest.DocTestSuite(helloworld))
    suite.addTests(test_pwman.suite())
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
