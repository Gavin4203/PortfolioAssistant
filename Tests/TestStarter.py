from dotenv import load_dotenv
load_dotenv()

import unittest

test_source = "CopyWithRandPointerTests.Test"
tests = unittest.TestLoader().loadTestsFromTestCase(test_source)

unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    unittest.main()