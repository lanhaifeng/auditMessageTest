import configparser
from enum import Enum, unique

import stomp

from common.fileUtil import FileUtil


@unique
class MessageType(Enum):
	"""
	activemq消息类型
	"""
	QUEUE = "queue"
	TOPIC = "topic"


class ActivemqConfig(object):
	"""
	activemq属性配置类
	"""
	cp = configparser.ConfigParser()
	file = FileUtil.get_project_path() + "config/message.conf"
	cp.read(file, encoding="utf-8")
	host = cp.get("activemq", "ip")
	port = cp.getint("activemq", "port")
	user = cp.get("activemq", "user")
	password = cp.get("activemq", "password")
	logon_validate = cp.getboolean("activemq", "logon_validate")
	access_queue_name = cp.get("activemq", "access_queue_name")
	access_queue_num = cp.getint("activemq", "access_queue_num")


class MessageListener(stomp.ConnectionListener):
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
		self.conn = stomp.Connection10([(ActivemqConfig.host, ActivemqConfig.port)])
		if ActivemqConfig.logon_validate:
			assert ActivemqConfig.user is not None, "activemq 'user' is required"
			assert ActivemqConfig.password is not None, "activemq 'password' is required"
			self.conn.connect(ActivemqConfig.user, ActivemqConfig.password)
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

