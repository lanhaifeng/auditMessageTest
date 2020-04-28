import unittest
from unittest import TestCase

from common.commonUtil import FileUtil
from common.dataProcessor import CompareHandlerDelegate, ReaderFileHandler


class TestCompareHandlerDelegate(TestCase):
    def test_equals(self):
        param1 = "SELECT   * from Test.TESTTABLE"
        param2 = "SELECT   *   from Test.TESTTABLE"
        assert not CompareHandlerDelegate.equals("test", param1, param2), "期待:%s == %s" % (param1, param2)
        assert CompareHandlerDelegate.equals("原始SQL", param1, param2), "期待:%s == %s" % (param1, param2)

        param2 = "select   *   from test.testtable"
        assert not CompareHandlerDelegate.equals("原始SQL", param1, param2), "期待:%s == %s" % (param1, param2)
        assert CompareHandlerDelegate.equals("标准化SQL", param1, param2), "期待:%s == %s" % (param1, param2)


class TestReaderFileHandler(TestCase):
    def test_read_file(self):
        assert ['select *\nfrom test1', 'SELECT   *   from\n\ntest.TESTTABLE'] == \
               ReaderFileHandler.read_file("原始SQL",
                                           FileUtil.get_file_path("classpath:/test/sql/sql/test2.sql"))
        assert "['select * from test1', 'SELECT * from test.TESTTABLE']" == \
               str(ReaderFileHandler.read_file("标准化SQL",
                                               FileUtil.get_file_path("classpath:/test/sql/sql/test2.sql")))


if __name__ == '__main__':
    unittest.main()



