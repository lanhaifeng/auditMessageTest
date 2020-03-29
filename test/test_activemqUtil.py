from unittest import TestCase
from message.activemqUtil import ActivemqUtil, ActivemqConfig
import time


class Test(TestCase):
	"""
	测试ActivemqUtil
	"""
	def test_activemq_util(self):
		ActivemqUtil.send_to_queue(ActivemqConfig.access_queue_name, "test")
		ActivemqUtil.receive_from_queue(ActivemqConfig.access_queue_name)

		ActivemqUtil.receive_from_topic(ActivemqConfig.access_queue_name)
		ActivemqUtil.send_to_topic(ActivemqConfig.access_queue_name, "test2")

		time.sleep(5)


if __name__ == '__main__':
	test = Test()
	test.test_activemq_util()