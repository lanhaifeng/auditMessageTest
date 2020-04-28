# -*- coding:UTF-8 -*-
import os

import xlrd

from common.commonUtil import MessageConfig, AuditType, FileUtil


class DataFilterConfig:
    """
    数据过滤字段
    """
    access_columns = str(MessageConfig.access_filter_columns).strip().split(",")
    logon_columns = str(MessageConfig.logon_filter_columns).strip().split(",")
    operators = str(MessageConfig.operator_symbol).strip().split(",")


class DataFilter(object):
    """
    分析时数据过滤
    """

    @property
    def operator(self) -> str:
        """
        返回当前过滤器支持的操作符
        :return:
        """
        pass

    @classmethod
    def filter(cls, data: dict, filter_value: str, column_name: str) -> bool:
        """
        数据过滤
        :param data: 数据
        :param filter_value: 过滤器期待的值
        :param column_name: 字段名
        :return:
        """
        assert data, "'data' is required"
        assert filter_value and filter_value.strip(), "'filter_value' is required"
        assert column_name and column_name.strip(), "'column_name' is required"
        return False
        pass


class EqualDataFilter(DataFilter):
    """
    相等过滤器
    """

    @property
    def operator(self) -> str:
        return "eq"

    @classmethod
    def filter(cls, data: dict, filter_value: str, column_name: str) -> bool:
        return filter_value == data[column_name]


class NotEqualDataFilter(DataFilter):
    """
    不相等过滤器
    """

    @property
    def operator(self) -> str:
        return "ne"

    @classmethod
    def filter(cls, data: dict, filter_value: str, column_name: str) -> bool:
        return filter_value != data[column_name]


class DataFilterDelegate(object):
    PRIMARY_KEY = "id"
    """
    数据过滤委托类,格式："access 规则名称 eq NETWORK"，[类型 字段名 比较符 值]
    """
    def __init__(self, filter_content: str):
        assert filter_content and filter_content.strip(), "'filter_content' is required"
        __access_group_filters = []
        __logon_group_filters = []
        for filter_value in filter_content.split(","):
            __filter = []
            for filter_element in filter_value.strip().split(" "):
                if filter_element is not None and filter_element.strip() != '':
                    __filter.append(filter_element.strip())
            if __filter[0] == AuditType.ACCESS.value:
                __access_group_filters.append(__filter[1:])
            if __filter[0] == AuditType.LOGON.value:
                __logon_group_filters.append(__filter[1:])

        self.__group_filters = {
            AuditType.ACCESS: __access_group_filters,
            AuditType.LOGON: __logon_group_filters,
        }
        self.__filters = []
        self.__filters.append(EqualDataFilter())
        self.__filters.append(NotEqualDataFilter())
        for __filter in self.__filters:
            self.__group_filters[__filter.operator] = __filter

        self.__group_columns = {
            AuditType.ACCESS: DataFilterConfig.access_columns,
            AuditType.LOGON: DataFilterConfig.logon_columns,
        }
        __access_data_keys = []
        __logon_data_keys = []
        self.__data_keys = {
            AuditType.ACCESS: __access_data_keys,
            AuditType.ACCESS_RESULT: __access_data_keys,
            AuditType.SQL_RESULT: __access_data_keys,
            AuditType.LOGON: __logon_data_keys,
            AuditType.LOGOFF: __logon_data_keys,
        }

    def filter(self, data: dict, audit_type: AuditType) -> bool:
        result = False
        for __filter in self.__group_filters[audit_type]:
            result = not __filter[0] in self.__group_columns[audit_type] \
                     or not __filter[1] in DataFilterConfig.operators \
                     or self.__group_filters[__filter[1]].filter(data, __filter[2], __filter[0])
            if not result:
                break
        return result


class ReaderFileHandler(object):
    """
    读取文件处理器
    """
    __default_reader_handler = MessageConfig.get_reader_handler("DEFAULT")
    __default_reader_values = __default_reader_handler.strip().split("@")

    @classmethod
    def read_file(cls, property_name: str, file_path: str) -> list:
        assert property_name and property_name.strip(), "'property_name' is required"
        assert file_path and file_path.strip(), "'file_path' is required"
        assert os.path.exists(file_path), "file_path:%s, not exist" % file_path
        __reader_handler = MessageConfig.get_reader_handler(property_name)
        __reader_values = __reader_handler.strip().split("@")

        if not __reader_handler:
            __reader_values = cls.__default_reader_values
        #导入
        __module = __import__(__reader_values[0], fromlist=True)
        # 去模块中找类
        __class_name = getattr(__module, __reader_values[1])
        # 根据类创建对象
        __obj = __class_name()
        # 去对象中找name对应的值
        __fun = getattr(__obj, __reader_values[2])
        if str(type(__fun)) == "<class 'function'>" or str(type(__fun)) == "<class 'method'>":
            return __fun(file_path)
        else:
            return __fun


class CompareHandler(object):
    """
    比较处理器
    """
    ALL_EQUAL = "*"

    @staticmethod
    def equals(actual_val: str, expect_val: str) -> bool:
        """
        全等比较
        :param actual_val:实际值
        :param expect_val:期待值
        :return:
        """
        if expect_val == CompareHandler.ALL_EQUAL:
            return True
        assert expect_val and expect_val.strip(), "'expect_val' is required"
        if actual_val and actual_val.strip():
            return actual_val == expect_val
        else:
            return False
        pass

    @staticmethod
    def equals_ignore_case(actual_val: str, expect_val: str) -> bool:
        """
        忽略大小写全等比较
        :param actual_val: 实际值
        :param expect_val: 期待值
        :return:
        """
        if expect_val == CompareHandler.ALL_EQUAL:
            return True
        assert expect_val and expect_val.strip(), "'expect_val' is required"
        if actual_val and actual_val.strip():
            return CompareHandler.equals(actual_val.upper(), expect_val.upper())
        else:
            return False
        pass

    @staticmethod
    def equals_space_tokenizer(actual_val: str, expect_val: str) -> bool:
        """
        以空格作为分隔，进行分词比较
        :param actual_val:实际值
        :param expect_val:期待值
        :return:
        """
        if expect_val == CompareHandler.ALL_EQUAL:
            return True
        assert expect_val and expect_val.strip(), "'expect_val' is required"
        if actual_val and actual_val.strip():
            param1_values = CompareHandler.space_tokenizer(actual_val)
            param2_values = CompareHandler.space_tokenizer(expect_val)
            result = True
            for index, val in enumerate(param1_values):
                if not CompareHandler.equals(val, param2_values[index]):
                    result = False
                    break
            return result
        else:
            return False
        pass

    @staticmethod
    def equals_space_tokenizer_ignore_case(actual_val: str, expect_val: str) -> bool:
        """
        以空格作为分隔，忽略大小写进行分词比较
        :param actual_val:实际值
        :param expect_val:期待值
        :return:
        """
        if expect_val == CompareHandler.ALL_EQUAL:
            return True
        assert expect_val and expect_val.strip(), "'expect_val' is required"
        if actual_val and actual_val.strip():
            param1_values = CompareHandler.space_tokenizer(actual_val)
            param2_values = CompareHandler.space_tokenizer(expect_val)
            result = True
            for index, val in enumerate(param1_values):
                if not CompareHandler.equals_ignore_case(val, param2_values[index]):
                    result = False
                    break
            return result
        else:
            return False
        pass

    @staticmethod
    def space_tokenizer(param: str):
        """
        根据空格分词
        :param param: 参数
        :return:
        """
        param_values = []
        if param and param.strip():
            for value in param.strip().split(" "):
                if value.strip() != '':
                    param_values.append(value)
        return param_values


class CompareHandlerDelegate(object):
    """
    比较处理委托类
    """

    @staticmethod
    def equals(column_name: str, actual_val: str, expect_val: str) -> bool:
        """
        比较两个值是否相等
        :param column_name: 字段名，用户获取比较器
        :param actual_val: 实际值
        :param expect_val: 期待值
        :return:
        """
        assert column_name and column_name.strip(), "'column_name' is required"
        __compare_handler = MessageConfig.get_compare_handler(column_name)
        __compare_values = __compare_handler.strip().split("@")
        # 导入
        __module = __import__(__compare_values[0], fromlist=True)
        # 去模块中找类
        __class_name = getattr(__module, __compare_values[1])
        # 去对象中找name对应的值
        __fun = getattr(__class_name, __compare_values[2])
        if str(type(__fun)) == "<class 'function'>" or str(type(__fun)) == "<class 'method'>":
            return __fun(actual_val, expect_val)
        else:
            return False


class PostDataExcelReader(object):
    """
    excel后置数据读取器
    """
    def __init__(self, file_pre: str, merge_columns: list):
        assert file_pre and file_pre.strip(), "'file_pre' is required"
        assert merge_columns and len(merge_columns), "'merge_columns' is required"

        self.__merge_columns = merge_columns
        __files = FileUtil.get_files_prefix(MessageConfig.output_dir, file_pre)
        self.__datas = {}
        for __file in __files:
            book = xlrd.open_workbook(__file, 'r+b')
            sheets = book.sheets()
            for sheet in sheets:
                header = sheet.row_values(0)
                for index in range(1, sheet.nrows):
                    data = dict(zip(header, sheet.row_values(index)))
                    self.__datas[data[self.primary_key_name]] = data

    @property
    def primary_key_name(self) -> str:
        """
        返回主键名
        :return:
        """
        return 'id'

    def get_append_data(self, primary_key_value: str) -> dict:
        """
        根据主键获取扩展数据
        :param primary_key_value: 关联主键
        :return:
        """
        __data = self.__datas[primary_key_value] if primary_key_value in self.__datas.keys() else {}
        __merge_data = {}
        if __data:
            for key in self.__merge_columns:
                __merge_data[key] = __data[key]
        return __merge_data


class AccessResultExcelReader(PostDataExcelReader):
    """
    访问审计执行结果读取器
    """

    def __init__(self, file_pre: str):
        __merge_columns = ["id", "返回行数", "错误码", "执行时长", "是否访问审计执行结果"]
        super().__init__(file_pre, __merge_columns)


class SqlResultExcelReader(PostDataExcelReader):
    """
    SQL返回内容excel读取器
    """

    def __init__(self, file_pre: str):
        __merge_columns = ["访问id", "字段描述", "行数据"]
        super().__init__(file_pre, __merge_columns)

    @property
    def primary_key_name(self) -> str:
        return "访问id"


class LogoffExcelReader(PostDataExcelReader):
    """
    登出excel读取器
    """

    def __init__(self, file_pre: str):
        __merge_columns = ["id", "退出时间", "是否登出审计"]
        super().__init__(file_pre, __merge_columns)


class PostDataExcelReaderDelegate(object):
    """
    数据后置处理委托类
    """
    def __init__(self):
        self.__readers = {
            AuditType.ACCESS: [AccessResultExcelReader(AuditType.ACCESS_RESULT.analysis_pre_file_name),
                               SqlResultExcelReader(AuditType.SQL_RESULT.analysis_pre_file_name)],
            AuditType.LOGON: [LogoffExcelReader(AuditType.LOGOFF.analysis_pre_file_name)]
        }
        pass

    def merge_data(self, data: dict, audit_type: AuditType):
        for reader in self.__readers[audit_type]:
            __append_data = reader.get_append_data(data["id"])
            if __append_data:
                data.update(__append_data)

