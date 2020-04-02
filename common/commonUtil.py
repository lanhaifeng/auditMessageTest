import os


class FileUtil(object):
	"""
	文件工具类
	"""
	@staticmethod
	def get_project_path():
		"""
		获取当前项目路径
		:return:
		"""
		execute_path = os.getcwd()
		return execute_path[:execute_path.find("auditMessageTest\\") + len("auditMessageTest\\")]


class StringUtil(object):
	"""
	字符串工具类
	"""
	@staticmethod
	def python_byte_to_java_byte(byte_array):
		"""
		python字节元组转java字节数组
		:param byte_array:字节元组
		:return:
		"""
		return [int(i) - 256 if int(i) > 127 else int(i) for i in byte_array]

	@staticmethod
	def java_byte_to_python_byte(byte_array):
		"""
		java字节数组转python字节元组
		:param byte_array:字节元组
		:return:
		"""
		return [i + 256 if i < 0 else i for i in byte_array]

	@staticmethod
	def int_to_bin_16_binary_bytes(int_value):
		"""
		int转bin16进制，如：b'\x01',b'\r\xe1\x00\x00\x00\x10\x03'-
		:param int_value:数值
		:return:
		"""
		if type(int_value) is int:
			return int_value.to_bytes(1, 'big')

		if type(int_value) is tuple or type(int_value) is list:
			return bytes(int_value)
		return int_value

	@staticmethod
	def bin_16_binary_bytes_to_int(byte_value):
		"""
		bin16进制转int
		:param byte_value: b'\x01'
		:return:
		"""
		for i, num in enumerate(byte_value):
			byte_value[i] = int.from_bytes(num, byteorder='little', signed=True)
		return byte_value

