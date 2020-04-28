# -*- coding:UTF-8 -*-
import configparser
import os
import platform
from enum import unique, Enum


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
		execute_path = os.path.abspath(os.path.dirname(__file__))
		return execute_path[:execute_path.find("auditMessageTest") + len("auditMessageTest")]

	@staticmethod
	def get_files(path: str, file_suffix_name: str) -> []:
		"""
		根据文件目录获取指定后缀文件名列表
		:param path:目录
		:param file_suffix_name:文件后缀
		:return:
		"""
		assert path is not None and path.strip() != '', "'path' is required"
		assert file_suffix_name is not None and file_suffix_name.strip() != '', "'file_suffix_name' is required"
		path = FileUtil.get_file_path(path)
		all_files = []
		for root, dirs, files in os.walk(path):
			# root 表示当前正在访问的文件夹路径
			# dirs 表示该文件夹下的子目录名list
			# files 表示该文件夹下的文件list
			# 遍历文件
			for file in files:
				file_path = os.path.join(root, file)
				# splitext() 分离文件名与后缀
				suffix_name = os.path.splitext(file)[1]
				if suffix_name.endswith(file_suffix_name):
					all_files.append(file_path)
		return all_files

	@staticmethod
	def get_files_prefix(path: str, file_name_prefix: str) -> []:
		"""
		根据文件目录获取指定文件名前缀的文件
		:param path: 目录
		:param file_name_prefix: 文件名前缀
		:return:
		"""
		assert path is not None and path.strip() != '', "'path' is required"
		assert file_name_prefix is not None and file_name_prefix.strip() != '', "'file_suffix_name' is required"
		path = FileUtil.get_file_path(path)
		all_files = []
		for root, dirs, files in os.walk(path):
			for file in files:
				file_name = os.path.splitext(file)[0]
				if file_name.startswith(file_name_prefix):
					all_files.append(os.path.join(root, file))
		return all_files

	@staticmethod
	def get_file_lines(path: str, split_char: str = '\n', encoding: str = 'UTF-8'):
		"""
		按行读取文件
		:param path: 文件路径
		:param split_char: 分隔符
		:param encoding: 文件编码
		:return:
		"""
		path = FileUtil.get_file_path(path)
		file = open(path, 'r', encoding=encoding)
		lines = [str(line).strip(split_char) for line in file.readlines()]
		file.close()

		return lines

	@staticmethod
	def get_sql_file(path: str, encoding: str = 'UTF-8'):
		"""
		读取sql文件
		:param path: 文件路径
		:param encoding: 文件编码
		:return:
		"""
		path = FileUtil.get_file_path(path)
		file = open(path, 'r', encoding=encoding)
		sql_list = file.read()
		sql_item = ''
		for x in sql_list:
			sql_item = sql_item + x

		file.close()
		return [] if sql_item == '' else [sql.strip() for sql in sql_item[:len(sql_item) - 1].split(";")]

	@staticmethod
	def get_sql_file_format(path: str, encoding: str = 'UTF-8'):
		"""
		读取sql文件并格式化，去掉换行和多余空格
		:param path: 文件路径
		:param encoding: 文件编码
		:return:
		"""
		path = FileUtil.get_file_path(path)
		file = open(path, 'r', encoding=encoding)
		sql_list = file.read()
		sql_item = ''
		for x in sql_list:
			# 判断包含空行的
			if '\n' in x:
				# 替换空行为1个空格
				x = x.replace('\n', ' ')

			sql_item = sql_item + x

		file.close()
		sql_list = [] if sql_item == '' else [sql.strip() for sql in sql_item[:len(sql_item) - 1].split(";")]
		for index, sql in enumerate(sql_list):
			sql_value = ''
			for word in sql.split(" "):
				if word != '':
					sql_value += word + " "
			if len(sql_value) > 1:
				sql_value = sql_value[:len(sql_value) - 1]
			sql_list[index] = sql_value
		return sql_list

	@staticmethod
	def get_file_spilt_char(file_name: str) -> str:
		"""
		根据文件后缀获取分隔符
		:param file_name: 文件名
		:return:
		"""
		assert file_name is not None and file_name.strip() != '', "'file_name' is required"
		if file_name.endswith(".sql"):
			return ";"
		else:
			return "\n"

	@staticmethod
	def get_file_path(path: str) -> str:
		"""
		根据项目相对路径获取绝对路径
		:param path:
		:return:
		"""
		if path.startswith("classpath:"):
			path = path[path.index("classpath:") + 10:]
			path = FileUtil.get_project_path() + path

		return path


@unique
class ConfigFileEnum(Enum):
	"""
	配置文件枚举
	"""
	COLUMN_DESC_CONF = "columnDesc.conf"
	DATA_PROCESSOR_CONF = "dataProcessor.conf"
	MESSAGE_CONF = "message.conf"

	@property
	def path(self):
		return FileUtil.get_project_path() + "/config/" + self.value


class MessageConfig(object):
	"""
	activemq属性配置类
	"""
	__cp = configparser.ConfigParser()
	__file = FileUtil.get_project_path() + "/config/message.conf"
	__cp.read(__file, encoding="utf-8")
	host = __cp.get("activemq", "ip")
	port = __cp.getint("activemq", "port")
	user = __cp.get("activemq", "user")
	password = __cp.get("activemq", "password")
	logon_validate = __cp.getboolean("activemq", "logon_validate")
	access_queue_name = __cp.get("activemq", "access_queue_name")
	access_queue_num = __cp.getint("activemq", "access_queue_num")

	output_dir = __cp.get("output_config", "output_dir")
	single_expect_result_file = __cp.get("output_config", "single_expect_result_file")
	if single_expect_result_file.startswith("classpath:"):
		single_expect_result_file = single_expect_result_file[single_expect_result_file.index("classpath:") + 10:]
		single_expect_result_file = FileUtil.get_project_path() + single_expect_result_file

	group_expect_result_file = __cp.get("output_config", "group_expect_result_file")
	if group_expect_result_file.startswith("classpath:"):
		group_expect_result_file = group_expect_result_file[group_expect_result_file.index("classpath:") + 10:]
		group_expect_result_file = FileUtil.get_project_path() + group_expect_result_file

	log_dir = __cp.get("log_config", "log_dir")
	if not os.path.exists(log_dir):
		os.mkdir(log_dir)
	analysis_wait_time = __cp.getint("analysis_config", "analysis_wait_time")
	shutdown_wait_time = __cp.getint("analysis_config", "shutdown_wait_time")

	__data_processor = configparser.ConfigParser()
	__file = FileUtil.get_project_path() + "/config/dataProcessor.conf"
	__data_processor.read(__file, encoding="utf-8")
	logon_filter_columns = __data_processor.get("data_analysis_filter", "logon_filter_columns")
	access_filter_columns = __data_processor.get("data_analysis_filter", "access_filter_columns")
	operator_symbol = __data_processor.get("data_analysis_filter", "operator_symbol")

	__config_file_readers = {
		ConfigFileEnum.DATA_PROCESSOR_CONF: __data_processor,
		ConfigFileEnum.MESSAGE_CONF: __cp
	}

	@classmethod
	def get_config_file_reader(cls, config_file: ConfigFileEnum) -> configparser.ConfigParser:
		"""
		获取对应配置文件读取器
		:param config_file: 配置文件枚举
		:return:
		"""
		assert config_file and isinstance(config_file, ConfigFileEnum), \
			"'config_file' is required and type is ConfigFileEnum"
		__cp = ""
		if config_file in cls.__config_file_readers.keys():
			__cp = cls.__config_file_readers[config_file]
		if not __cp:
			__cp = configparser.ConfigParser()
			__cp.read(config_file.path, encoding="utf-8")
			cls.__config_file_readers[config_file] = __cp
		return __cp

	@classmethod
	def get_value_from_config(cls, config_file: ConfigFileEnum, section: str, column_name: str) -> str:
		"""
		获取对应文件解析器，某部分，对应键，所对应的值
		:param config_file:文件类型
		:param section:部分名
		:param column_name:键名
		:return:
		"""
		assert config_file and isinstance(config_file, ConfigFileEnum), \
			"'config_file' is required and type is ConfigFileEnum"
		assert section is not None and section.strip() != '', "'section' is required"
		assert column_name is not None and column_name.strip() != '', "'column_name' is required"
		assert cls.get_config_file_reader(config_file).has_section(section), "section:" + section + ",not exist"
		assert cls.get_config_file_reader(config_file).has_option(section, column_name), \
			"section:" + section + ",option:" + column_name + ",not exist"
		return cls.get_config_file_reader(config_file).get(section, column_name)

	@classmethod
	def get_section_values(cls, config_file: ConfigFileEnum, section: str) -> list:
		"""
		获取对应文件解析器，某部分，特定部分全部的值
		:param config_file:文件类型
		:param section:部分名
		:return:
		"""
		assert config_file and isinstance(config_file, ConfigFileEnum), \
			"'config_file' is required and type is ConfigFileEnum"
		assert cls.get_config_file_reader(config_file).has_section(section), "section:" + section + ",not exist"
		return [item[1] for item in cls.get_config_file_reader(config_file).items(section)]

	@classmethod
	def get_compare_handler(cls, column_name: str) -> str:
		"""
		获取比较处理器
		:param column_name:字段名
		:return:
		"""
		assert column_name and column_name.strip(), "'column_name' is required"
		__reader = cls.get_config_file_reader(ConfigFileEnum.DATA_PROCESSOR_CONF)
		if not __reader.has_option("compare_handler", column_name):
			return __reader.get("compare_handler", "DEFAULT")
		return __reader.get("compare_handler", column_name)

	@classmethod
	def get_reader_handler(cls, column_name: str) -> str:
		"""
		获取文件读取器
		:param column_name: 字段名
		:return:
		"""
		assert column_name and column_name.strip(), "'column_name' is required"
		__reader = cls.get_config_file_reader(ConfigFileEnum.DATA_PROCESSOR_CONF)
		if not __reader.has_option("reader_handler", column_name):
			return __reader.get("reader_handler", "DEFAULT")
		return __reader.get("reader_handler", column_name)


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


@unique
class AuditType(Enum):
	"""
	统计策略类型
	"""
	ACCESS = "access"
	ACCESS_RESULT = "accessResult"
	LOGON = "logon"
	LOGOFF = "logoff"
	SQL_RESULT = "sqlResult"

	@property
	def desc(self):
		if self == AuditType.ACCESS:
			return "访问"
		if self == AuditType.LOGON:
			return "登录"

	@property
	def analysis_pre_file_name(self):
		if self == AuditType.ACCESS:
			return "AccessAudit"
		if self == AuditType.ACCESS_RESULT:
			return "AccessResult"
		if self == AuditType.SQL_RESULT:
			return "SqlResult"
		if self == AuditType.LOGON:
			return "LogonAudit"
		if self == AuditType.LOGOFF:
			return "Logoff"


class HeadersConfig(object):
	"""
	文件头配置
	"""
	@staticmethod
	def get_section_columns(section: str):
		"""
		获取配置文件columnDesc.conf中对应section
		:return:
		"""
		assert section and section.strip(), "'section' is required"
		return MessageConfig.get_section_values(ConfigFileEnum.COLUMN_DESC_CONF, section)


class SystemUtil(object):
	"""
	系统工具类
	"""
	@staticmethod
	def get_operating_system():
		"""
		获取操作系统
		:return:
		"""
		return platform.system()
