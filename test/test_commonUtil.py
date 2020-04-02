import unittest
from unittest import TestCase

from common import protoActiveMq_pb2
from common.commonUtil import FileUtil, StringUtil
from common.protoActiveMq_pb2 import MsgCmdType


class TestFileUtil(TestCase):
	"""
	FileUtil测试
	"""
	def test_get_project_path(self):
		"""
		测试获取项目根目录方法
		:return:
		"""
		self.assertTrue(FileUtil.get_project_path().endswith("auditMessageTest\\"))


class TestStringUtil(TestCase):
	"""
	StringUtil测试
	"""
	def test_python_byte_to_java_byte(self):
		"""
		测试python字节元组转java字节数组
		:return:
		"""
		byte_array = b'\r{\x00\x00\x00\x10\x03'
		self.assertEqual(len(byte_array), 7)
		self.assertEqual(len(StringUtil.python_byte_to_java_byte(byte_array)), 7)
		self.assertEqual(StringUtil.python_byte_to_java_byte(byte_array), [13, 123, 0, 0, 0, 16, 3])

	def test_java_byte_to_python_byte(self):
		"""
		测试java字节数组转java字节元组
		:return:
		"""
		java_byte_array = (13, -31, 0, 0, 0, 16, 3)
		python_byte_array = StringUtil.java_byte_to_python_byte(java_byte_array)

		self.assertEqual(7, len(java_byte_array))
		self.assertEqual(bytearray(b'\r\xe1\x00\x00\x00\x10\x03'), bytearray(StringUtil.int_to_bin_16_binary_bytes(python_byte_array)))
		self.assertEqual(b'\r\xe1\x00\x00\x00\x10\x03', StringUtil.int_to_bin_16_binary_bytes(python_byte_array))


class ProtoActiveMq(TestCase):
	"""
	测试protoActiveMq_pb2.py
	"""
	def test_MSGCMDTYPE(self):
		"""
		测试protoActiveMq_pb2中BaseMessage的protobuf序列化和反序列化
		:return:
		"""
		cmd_len = 225
		cmd_type = MsgCmdType.CAPAAAccess
		base_message_serialize = protoActiveMq_pb2.BaseMessage()
		base_message_serialize.cmdLen = cmd_len
		base_message_serialize.cmdType = cmd_type
		base_message_bytes = base_message_serialize.SerializeToString()

		base_message = protoActiveMq_pb2.BaseMessage()
		base_message.ParseFromString(base_message_bytes)

		self.assertEqual(cmd_len, base_message.cmdLen)
		self.assertEqual(cmd_type, base_message.cmdType)


if __name__ == '__main__':
	unittest.main()

