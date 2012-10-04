import unittest
import bms
import sys
from StringIO import StringIO

class Test1(unittest.TestCase):
  def setUp(self):
    self.testclass = bms.BMSEvaluator()
    sys.stdout = StringIO()

  def test_func_for(self):
    result = bms.parser.parse('for i = 1 to 5   print "%i%"  next i', lexer=bms.lexer)
    self.testclass.evaluate(result)
    self.assertEqual(sys.stdout.getvalue(), "1234")

if __name__ == "__main__":
  unittest.main()

