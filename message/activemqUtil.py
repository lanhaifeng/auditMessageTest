# -*- coding:UTF-8 -*-
from enum import Enum, unique

import stomp

from common import protoActiveMq_pb2
from common.commonUtil import MessageConfig
from common.protoActiveMq_pb2 import MsgCmdType
from stomp.utils import encode


@unique
class MessageType(Enum):
	"""
	activemq消息类型
	"""
	QUEUE = "queue"
	TOPIC = "topic"


class MessageListener(object):
	"""
	消息监听器
	"""
	def on_message(self, headers, message):
		"""
		消费消息处理
		:param headers:消息头
		:param message:消息
		:return:
		"""
		print('headers: %s' % headers)
		print('message: %s' % message)
		message_data = message
		if type(message) is str:
			message_data = encode(message, encoding="utf-8")
		head_length = 7
		index = 0

		while index < len(message_data):
			audit = None
			base_message = protoActiveMq_pb2.BaseMessage()
			base_message.ParseFromString(message_data[index:head_length+index])
			# print(base_message)

			if base_message.cmdType == MsgCmdType.CAPAALogOn:
				audit = protoActiveMq_pb2.CapaaLogOn()

			if base_message.cmdType == MsgCmdType.CAPAALogOff:
				audit = protoActiveMq_pb2.CapaaLogOff()

			if base_message.cmdType == MsgCmdType.CAPAAAccess:
				audit = protoActiveMq_pb2.CapaaAccess()

			if base_message.cmdType == MsgCmdType.CAPAAAccessResult:
				audit = protoActiveMq_pb2.CapaaAccessResult()

			if base_message.cmdType == MsgCmdType.CAPAAFlowInfo:
				audit = protoActiveMq_pb2.CapaaFlowInfo()

			if base_message.cmdType == MsgCmdType.CAPAADBStat:
				audit = protoActiveMq_pb2.DBStat()

			if base_message.cmdType == MsgCmdType.CAPAADBResultset:
				audit = protoActiveMq_pb2.DBResultset()

			if audit is not None:
				audit.ParseFromString(message_data[index:base_message.cmdLen+index])
				index += base_message.cmdLen
				# print("audit: %s" % audit)

	def on_error(self, headers, message):
		"""
		消费消息错误处理
		:param headers:消息头
		:param message:消息
		:return:
		"""
		print(f"headers:{headers['destination']}, message:{message}")


class ActivemqUtil(object):
	"""
	activemq工具类
	"""

	def __init__(self):
		"""
		初始化属性
		"""
		self.conn = stomp.Connection10([(MessageConfig.host, MessageConfig.port)], auto_decode=False)
		if MessageConfig.logon_validate:
			assert MessageConfig.user is not None, "activemq 'user' is required"
			assert MessageConfig.password is not None, "activemq 'password' is required"
			self.conn.connect(MessageConfig.user, MessageConfig.password)
		else:
			self.conn.connect()

	def close_conn(self):
		"""
		关闭连接
		:return:
		"""
		self.conn.disconnect()

	@staticmethod
	def format_destination(destination_name, message_type):
		"""
		格式化目的地
		:param destination_name: 目的名
		:param message_type: 消息类型
		:return:
		"""
		assert message_type is not None, "'message_type' is required"
		if type(message_type) == MessageType:
			destination_name = "/" + message_type.value + "/" + destination_name
			return destination_name

	def send_to_message(self, destination_name, msg, message_type=MessageType.QUEUE):
		"""
		发送消息到队列
		:param destination_name: 目的名，队列或者主题名
		:param msg: 消息
		:param message_type: 消息类型
		:return:
		"""
		assert message_type is not None, "'message_type' is required"
		if type(message_type) == MessageType:
			self.conn.send(destination=self.format_destination(destination_name, message_type), body=msg)

	def send_to_queue(self, queue_name, msg):
		"""
		发送消息到队列
		:param queue_name: 队列名
		:param msg: 消息
		:return:
		"""
		self.send_to_message(queue_name, msg, MessageType.QUEUE)

	def send_to_topic(self, topic_name, msg):
		"""
		发送消息到主题
		:param topic_name: 主题名
		:param msg: 消息
		:return:
		"""
		self.send_to_message(topic_name, msg, MessageType.TOPIC)

	def receive_message(self, destination_name, message_type=MessageType.QUEUE):
		"""
		接收消息
		:param destination_name: 目的名，队列或者主题名
		:param message_type: 消息类型
		:return:
		"""
		assert message_type is not None, "'message_type' is required"
		if type(message_type) == MessageType:
			self.conn.set_listener("MessageListener", MessageListener())
			self.conn.subscribe(ActivemqUtil.format_destination(destination_name, message_type))

	def receive_from_queue(self, queue_name):
		"""
		从队列接收消息
		:param queue_name: 队列名
		:return:
		"""
		self.receive_message(queue_name, MessageType.QUEUE)

	def receive_from_topic(self, topic_name):
		"""
		从主题接收消息
		:param topic_name: 主题名
		:return:
		"""
		self.receive_message(topic_name, MessageType.TOPIC)

