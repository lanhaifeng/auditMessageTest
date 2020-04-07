import time
import unittest
from unittest import TestCase

from common import protoActiveMq_pb2
from common.commonUtil import StringUtil, MessageConfig
from message.activemqUtil import ActivemqUtil, MessageListener

java_protobuf_byte_array = (13, -31, 0, 0, 0, 16, 3, 26, 38, 57, 48, 48, 51, 49, 52, 48, 54, 55, 53, 50, 48, 50, 53, 57, 52, 53,
	54, 48, 95, 49, 53, 56, 53, 55, 50, 54, 53, 53, 57, 49, 48, 50, 52, 50, 49, 95, 54, 34, 36, 57, 48, 48, 51,
	49, 52, 48,
	54, 55, 53, 50, 48, 50, 53, 57, 52, 53, 54, 48, 95, 49, 53, 56, 53, 55, 50, 54, 53, 53, 57, 49, 48,
	50, 52, 50,
	49, 82, 7, 110, 101, 116, 119, 111, 114, 107, 88, -6, -44, -19, -25, -37, -58, -24, 2, 98, 3, 83, 69,
	84, -120,
	1, 1, -86, 1, 3, 10, 1, 49, -70, 1, 17, 83, 69, 84, 32, 80, 82, 79, 70, 73, 76, 73, 78, 71, 32, 61,
	32, 63,
	-54, 1, 13, 49, 57, 50, 46, 49, 54, 56, 46, 54, 49, 46, 52, 55, -48, 1, -68, -120, 3, -38, 1, 15, 49,
	57, 50,
	46, 49, 54, 56, 46, 50, 51, 56, 46, 49, 48, 52, -32, 1, -22, 25, -24, 1, 1, -14, 1, 17, 83, 69, 84,
	32, 80, 82,
	79, 70, 73, 76, 73, 78, 71, 32, 61, 32, 49, -6, 1, 4, 82, 79, 79, 84, -94, 2, 12, 50, 51, 56, 95, 49,
	48, 52,
	109, 121, 115, 113, 108, 13, -45, 0, 0, 0, 16, 3, 26, 38, 57, 48, 48, 51, 49, 52, 48, 54, 55, 53, 50,
	48, 50,
	53, 57, 52, 53, 54, 48, 95, 49, 53, 56, 53, 55, 50, 54, 53, 53, 57, 49, 48, 50, 52, 50, 49, 95, 55,
	34, 36, 57,
	48, 48, 51, 49, 52, 48, 54, 55, 53, 50, 48, 50, 53, 57, 52, 53, 54, 48, 95, 49, 53, 56, 53, 55, 50,
	54, 53, 53,
	57, 49, 48, 50, 52, 50, 49, 82, 7, 110, 101, 116, 119, 111, 114, 107, 88, -22, -43, -19, -25, -37,
	-58, -24, 2,
	98, 4, 83, 72, 79, 87, -120, 1, 1, -86, 1, 0, -70, 1, 11, 83, 72, 79, 87, 32, 83, 84, 65, 84, 85, 83,
	-54, 1,
	13, 49, 57, 50, 46, 49, 54, 56, 46, 54, 49, 46, 52, 55, -48, 1, -68, -120, 3, -38, 1, 15, 49, 57, 50,
	46, 49,
	54, 56, 46, 50, 51, 56, 46, 49, 48, 52, -32, 1, -22, 25, -24, 1, 1, -14, 1, 11, 83, 72, 79, 87, 32,
	83, 84, 65,
	84, 85, 83, -6, 1, 4, 82, 79, 79, 84, -94, 2, 12, 50, 51, 56, 95, 49, 48, 52, 109, 121, 115, 113, 108,
	13, -45,
	0, 0, 0, 16, 3, 26, 38, 57, 48, 48, 51, 49, 52, 48, 54, 55, 53, 50, 48, 50, 53, 57, 52, 53, 54, 48,
	95, 49, 53,
	56, 53, 55, 50, 54, 53, 53, 57, 49, 48, 50, 52, 50, 49, 95, 56, 34, 36, 57, 48, 48, 51, 49, 52, 48,
	54, 55, 53,
	50, 48, 50, 53, 57, 52, 53, 54, 48, 95, 49, 53, 56, 53, 55, 50, 54, 53, 53, 57, 49, 48, 50, 52, 50,
	49, 82, 7,
	110, 101, 116, 119, 111, 114, 107, 88, -17, -34, -19, -25, -37, -58, -24, 2, 98, 4, 83, 72, 79, 87,
	-120, 1, 1,
	-86, 1, 0, -70, 1, 11, 83, 72, 79, 87, 32, 83, 84, 65, 84, 85, 83, -54, 1, 13, 49, 57, 50, 46, 49, 54,
	56, 46,
	54, 49, 46, 52, 55, -48, 1, -68, -120, 3, -38, 1, 15, 49, 57, 50, 46, 49, 54, 56, 46, 50, 51, 56, 46,
	49, 48,
	52, -32, 1, -22, 25, -24, 1, 1, -14, 1, 11, 83, 72, 79, 87, 32, 83, 84, 65, 84, 85, 83, -6, 1, 4, 82,
	79, 79,
	84, -94, 2, 12, 50, 51, 56, 95, 49, 48, 52, 109, 121, 115, 113, 108, 13, -23, 0, 0, 0, 16, 3, 26, 38,
	57, 48,
	48, 51, 49, 52, 48, 54, 55, 53, 50, 48, 50, 53, 57, 52, 53, 54, 48, 95, 49, 53, 56, 53, 55, 50, 54,
	53, 53, 57,
	49, 48, 50, 52, 50, 49, 95, 57, 34, 36, 57, 48, 48, 51, 49, 52, 48, 54, 55, 53, 50, 48, 50, 53, 57,
	52, 53, 54,
	48, 95, 49, 53, 56, 53, 55, 50, 54, 53, 53, 57, 49, 48, 50, 52, 50, 49, 82, 7, 110, 101, 116, 119,
	111, 114,
	107, 88, -68, -27, -19, -25, -37, -58, -24, 2, 98, 6, 83, 69, 76, 69, 67, 84, 114, 4, 84, 69, 83, 84,
	-120, 1,
	1, -86, 1, 0, -70, 1, 18, 115, 101, 108, 101, 99, 116, 32, 42, 32, 102, 114, 111, 109, 32, 116, 101,
	115, 116,
	-54, 1, 13, 49, 57, 50, 46, 49, 54, 56, 46, 54, 49, 46, 52, 55, -48, 1, -68, -120, 3, -38, 1, 15, 49,
	57, 50,
	46, 49, 54, 56, 46, 50, 51, 56, 46, 49, 48, 52, -32, 1, -22, 25, -24, 1, 1, -14, 1, 18, 115, 101, 108,
	101, 99,
	116, 32, 42, 32, 102, 114, 111, 109, 32, 116, 101, 115, 116, -6, 1, 4, 82, 79, 79, 84, -94, 2, 12, 50,
	51, 56,
	95, 49, 48, 52, 109, 121, 115, 113, 108)


class TestActiveMqUtil(TestCase):
	"""
	测试ActivemqUtil中activemq queue发送接收信息
	"""
	@unittest.skipIf(0, "skip test_activemq_util_parse")
	def test_activemq_util_parse(self):
		"""
		测试protobuf字节码转对象
		"""
		python_protobuf_byte_array = StringUtil.java_byte_to_python_byte(java_protobuf_byte_array)
		protobuf_16_binary_bytes = StringUtil.int_to_bin_16_binary_bytes(python_protobuf_byte_array)

		base_message = protoActiveMq_pb2.BaseMessage()
		base_message.ParseFromString(protobuf_16_binary_bytes[:7])
		capaa_access = protoActiveMq_pb2.CapaaAccess()
		capaa_access.ParseFromString(protobuf_16_binary_bytes[:base_message.cmdLen])
		lisener = MessageListener()
		lisener.on_message([], protobuf_16_binary_bytes)

	@unittest.skipIf(1, "skip test_activemq_util_queue")
	def test_activemq_util_queue(self):
		__java_protobuf_byte_array = (13, -31, 0, 0, 0, 16, 3)
		python_protobuf_byte_array = StringUtil.java_byte_to_python_byte(__java_protobuf_byte_array)
		protobuf_16_binary_bytes = StringUtil.int_to_bin_16_binary_bytes(python_protobuf_byte_array)

		activemq_util = ActivemqUtil()
		activemq_util.send_to_queue(MessageConfig.access_queue_name, protobuf_16_binary_bytes)
		activemq_util.receive_from_queue(MessageConfig.access_queue_name)

		time.sleep(10)

	@unittest.skip("skip test_activemq_util_queue_topic")
	def test_activemq_util_queue_topic(self):
		"""
		测试ActivemqUtil中activemq topic发送接收信息
		:return:
		"""
		__java_protobuf_byte_array = (13, -2, 0, 0, 0, 16, 3)
		python_protobuf_byte_array = StringUtil.java_byte_to_python_byte(__java_protobuf_byte_array)
		protobuf_16_binary_bytes = StringUtil.int_to_bin_16_binary_bytes(python_protobuf_byte_array)
		activemq_util = ActivemqUtil()
		activemq_util.receive_from_topic(MessageConfig.access_queue_name)
		activemq_util.send_to_topic(MessageConfig.access_queue_name, protobuf_16_binary_bytes)
		time.sleep(10)


if __name__ == '__main__':
	unittest.main()

