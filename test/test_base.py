import unittest
from unittest import TestCase


class TestBase(TestCase):
    """
    基础测试测试
    """
    def test_str_bytes(self):
        """
        测试字符串与字节元组
        :return:
        """
        __str = "Hello, world!"
        __byte = b"Hello, world!"
        __bytes = bytearray(__str, encoding="utf8")
        self.assertEqual(__byte, bytes(__str, encoding="utf8"), "字符串转字节元组")
        self.assertEqual(__byte, str.encode(__str, encoding="utf8"), "字符串转字节元组")
        self.assertEqual(__byte, __str.encode(encoding="utf8"), "字符串转字节元组")

        self.assertEqual(__str, bytes.decode(__byte, encoding="utf8"), "字节元组转字符串")
        self.assertEqual(__str, str(__byte, encoding="utf8"), "字节元组转字符串")
        self.assertEqual(__str, __byte.decode(encoding="utf8"), "字节元组转字符串")

    def test_bytes(self):
        """
        测试元祖截组
        :return:
        """
        arrarys = (3, 4, 2, 6, 8, 9, 5, 1, 7, 0)
        self.assertEqual((3, 4, 2, 6), arrarys[:4])
        self.assertEqual((8, 9, 5, 1, 7, 0), arrarys[4:])
        self.assertEqual((8, 9, 5), arrarys[4:7])

        arrarys = [[3, 4, 2, 6, 8, 9, 5, 1, 7, 0], [4, 2, 6, 8, 9, 5, 1, 7, 0, 3], [2, 6, 8, 9, 5, 1, 7, 0, 3, 4]]
        self.assertEqual([3, 4, 2, 6, 8, 9, 5, 1, 7, 0], arrarys[0])


if __name__ == '__main__':
    unittest.main()

