import unittest
from unittest import TestCase

from common.fileUtil import FileUtil


class TestFileUtil(TestCase):
	"""
	FileUtil测试
	"""
	def test_get_project_path(self):
		self.assertTrue(FileUtil.get_project_path().endswith("auditMessageTest\\"))


if __name__ == '__main__':
	unittest.main()

