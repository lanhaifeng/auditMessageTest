import configparser
import unittest
from unittest import TestCase

import xlrd
import xlwt
from xlutils.copy import copy

from common import protoActiveMq_pb2
from common.commonUtil import FileUtil, StringUtil, MessageConfig, AuditType, HeadersConfig
from common.protoActiveMq_pb2 import MsgCmdType
from common.statisticAnalysis import SingleFieldStrategyDelegate, ExpectResultReader, GroupExpectResultReader, \
	StrategyType


class TestFileUtil(TestCase):
	"""
	FileUtil测试
	"""
	def test_get_project_path(self):
		"""
		测试获取项目根目录方法
		:return:
		"""
		self.assertTrue(FileUtil.get_project_path().endswith("auditMessageTest"))

	def test_get_files(self):
		"""
		测试根据目录和后缀获取指定文件
		:return:
		"""
		sql_dir = FileUtil.get_project_path() + "test"
		files = FileUtil.get_files(sql_dir, ".sql")
		for file in files:
			print(file)


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


class TestProtoActiveMq(TestCase):
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


class TestExcel(TestCase):
	"""
	测试excel工具类
	"""
	excel_url = '\\test\\LogonAudit_1586413078263.xls'
	def test_read_excel(self):
		"""
		测试读写excel
		:return:
		"""
		excel_path = FileUtil.get_project_path() + self.excel_url
		book = xlrd.open_workbook(excel_path, 'w+b')
		sheets = book.sheets()
		sheet1 = sheets[0]
		print('表格总页数', len(sheets))

		nrows = sheet1.nrows
		print('表格总行数', nrows)

		ncols = sheet1.ncols
		print('表格总列数', ncols)

		row3_values = sheet1.row_values(2)
		print('第3行值', row3_values)

		row0_values = sheet1.row_values(0)
		row1_values = sheet1.row_values(1)
		data = dict(zip(row0_values, row1_values))
		print(data)

		col3_values = sheet1.col_values(2)
		print('第3列值', col3_values)

		cell_3_3 = sheet1.cell(2, 2).value
		print('第3行第3列的单元格的值：', cell_3_3)

	@unittest.skipIf(1, "skip test_create_write_excel")
	def test_create_write_excel(self):
		"""
		写excel
		:return:
		"""
		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('test')
		worksheet.write(0, 0, 'A1data')
		workbook.save('excelwrite.xls')

	@unittest.skipIf(0, "skip test_append_write_excel")
	def test_append_write_excel(self):
		"""
		测试excel追加写
		:return:
		"""
		excel_url = '\\test\\LogonAudit_1586092319878.xls'
		excel_path = FileUtil.get_project_path() + self.excel_url
		book = xlrd.open_workbook(excel_path, 'w+b')
		# sheets = book.sheet_names()
		# worksheet = book.sheet_by_name(sheets[0])
		# nrows = worksheet.nrows

		nrows = book.sheets()[0].nrows

		new_workbook = copy(book)
		new_worksheet = new_workbook.get_sheet(0)
		for i in range(0, 10):
			new_worksheet.write(nrows, i, i)
		new_workbook.save(excel_path)


class TestExpectResult(TestCase):
	"""
	测试ExpectResult
	"""
	def test_read_json(self):
		reader = ExpectResultReader(MessageConfig.expect_result_file)
		logon_strategy = SingleFieldStrategyDelegate(reader.logon_properties(), AuditType.LOGON)
		access_strategy = SingleFieldStrategyDelegate(reader.access_properties(), AuditType.ACCESS)

		logon_excel_path = FileUtil.get_project_path() + '\\test\\LogonAudit_1586413078263.xls'
		book = xlrd.open_workbook(logon_excel_path, 'w+b')
		sheets = book.sheets()
		for sheet in sheets:
			header = sheet.row_values(0)
			for index in range(1, sheet.nrows):
				data = dict(zip(header, sheet.row_values(index)))
				logon_strategy.statistic_data(data)

		logon_strategy.analysis_data()
		for expectResult in reader.logon_properties():
			# print(expectResult)
			pass

		access_excel_path = FileUtil.get_project_path() + '\\test\\AccessAudit_1586413078448.xls'
		book = xlrd.open_workbook(access_excel_path, 'w+b')
		sheets = book.sheets()
		for sheet in sheets:
			header = sheet.row_values(0)
			for index in range(1, sheet.nrows):
				data = dict(zip(header, sheet.row_values(index)))
				access_strategy.statistic_data(data)

		access_strategy.analysis_data()
		for expectResult in reader.access_properties():
			# print(expectResult)
			pass

		file = FileUtil.get_project_path() + "/config/columnDesc.conf"

		cp = configparser.ConfigParser()
		cp.read(file, encoding="utf-8")
		print([item[1] for item in cp.items("logOff")])
		print(HeadersConfig.get_section_columns("logOff"))
		print('消息类型' in HeadersConfig.get_section_columns("logOff"))
		print('消息类型1' in HeadersConfig.get_section_columns("logOff"))

		print(FileUtil.get_file_lines(file))

		sql_file = FileUtil.get_project_path() + "\\test\\sql\\sql\\test2.sql"
		print(FileUtil.get_sql_file(sql_file))

		reader = GroupExpectResultReader(MessageConfig.group_expect_result_file, StrategyType.MULTIPLE_FIELDS_MATCH)
		for expectResult in reader.access_properties():
			print(expectResult)
			pass
		access_strategy = SingleFieldStrategyDelegate(reader.access_properties(), AuditType.ACCESS)
		for sheet in sheets:
			header = sheet.row_values(0)
			for index in range(1, sheet.nrows):
				data = dict(zip(header, sheet.row_values(index)))
				access_strategy.statistic_data(data)

		access_strategy.analysis_data()


if __name__ == '__main__':
	unittest.main()

