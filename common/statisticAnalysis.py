import json
import os
import time
from enum import unique, Enum

import xlwt
from xlrd import sheet

from common.commonUtil import FileUtil, AuditType, HeadersConfig, MessageConfig


@unique
class ConfigType(Enum):
    """
    配置文件类型
    """
    STR = "str"
    FILE = "file"
    DIR = "dir"


@unique
class StrategyType(Enum):
    """
    策略类型
    """
    SINGLE_FIELD_COUNT = "SingleFieldCount"
    TOTAL_COUNT = "TotalCount"
    MULTIPLE_FIELDS_MATCH = "MultipleFieldsMatch"


class ExpectResult(object):
    """
    期待结果实体类
    """

    def __init__(self, config_type: str, property_name: str, expect_result: dict):
        assert config_type is not None, "'config_type' is required"
        assert property_name is not None, "'property_name' is required"
        self.configType = config_type.lower()
        self.propertyName = property_name
        self.actualNums = []
        self.notMatchValues = []
        self.notMatchDataKeys = []

        if config_type.lower() == ConfigType.STR.value.lower():
            self.expectValues = expect_result['expectValues']
            self.expectNums = expect_result['expectNums']

            assert self.expectValues is not None, "'expectValues' is required"
            assert self.expectNums is not None, "'expectNums' is required"
            assert len(self.expectNums) == 0 or len(self.expectValues) == len(
                self.expectNums), "'values' length need equal 'expectNums' length"
        if config_type.lower() == ConfigType.FILE.value.lower():
            self.expectValueFiles = expect_result['expectValueFiles']
            self.expectNumFiles = expect_result['expectNumFiles']

            assert self.expectValueFiles is not None, "'expectValueFiles' is required"
            assert self.expectNumFiles is not None, "'expectNumFiles' is required"
            assert len(self.expectNumFiles) == 0 or len(self.expectValueFiles) == len(
                self.expectNumFiles), "'valueFiles' length need equal 'expectNumFiles' length"
        if config_type.lower() == ConfigType.DIR.value.lower():
            self.dataDir = expect_result['dataDir']
            self.expectValueSuffix = expect_result['expectValueSuffix']
            self.expectNumSuffix = expect_result['expectNumSuffix']

            assert self.dataDir is not None and self.dataDir.strip() != '', "'dataDir' is required"
            assert self.expectValueSuffix is not None and self.expectValueSuffix.strip() != '', \
                "'valueSuffix' is required"
            assert self.expectNumSuffix is not None and self.expectNumSuffix.strip() != '', \
                "'expectNumSuffix' is required"

    def __str__(self):
        """
        重写方法便于输出
        :return:
        """
        result = {
            "字段名": self.propertyName,
            "期待值": self.expectValues,
            "不匹配值": self.notMatchValues,
            "不匹配数据id": self.notMatchDataKeys,
            "期待数量": self.expectNums,
            "实际数量": self.actualNums
        }

        return json.dumps(result, ensure_ascii=False)

    def to_list_for_out(self, audit_type : AuditType):
        """
        转为输出列表
        ["审计类型", "字段名", "期待数量", "实际数量", "期待值列表", "不匹配值列表", "不匹配数据id"]
        :param audit_type: 审计类型
        :return:
        """
        return [audit_type.desc, self.propertyName, self.expectNums, self.actualNums, self.expectValues,
                self.notMatchValues, self.notMatchDataKeys]


class ExpectResultReader(object):
    """
    期待结果读取
    """

    def __init__(self, expect_result_file: str):
        """
        初始化方法，读取json文件
        """
        assert expect_result_file is not None, "'expect_result_file' is required"
        __file = open(expect_result_file, "rb")
        self.__file_json = json.load(__file)
        __file.close()

        assert 'logonProperties' in self.__file_json or 'accessProperties' in self.__file_json, \
            "'logonProperties' or 'accessProperties' is required"

        self.__logonProperties = []
        self.__accessProperties = []
        if 'logonProperties' in self.__file_json:
            for expect_result in self.__file_json['logonProperties']:
                self.__logonProperties.append(ExpectResult(expect_result['configType'], expect_result['propertyName'],
                                                           expect_result['expectResult']))

        if 'accessProperties' in self.__file_json:
            for expect_result in self.__file_json['accessProperties']:
                self.__accessProperties.append(ExpectResult(expect_result['configType'], expect_result['propertyName'],
                                                            expect_result['expectResult']))

        for expect_result in self.__logonProperties:
            self.__parse_expect_result(expect_result)

        for expect_result in self.__accessProperties:
            self.__parse_expect_result(expect_result)

    def __parse_expect_result(self, expect_result: ExpectResult):
        config_type = expect_result.configType
        if config_type.lower() == ConfigType.STR.value.lower():
            self.__parse_str_expect_result(expect_result)
        if config_type.lower() == ConfigType.FILE.value.lower():
            self.__parse_file_expect_result(expect_result)
        if config_type.lower() == ConfigType.DIR.value.lower():
            self.__parse_dir_expect_result(expect_result)

        if len(expect_result.actualNums) == 0:
            expect_result.actualNums = [0] * len(expect_result.expectValues)
        if len(expect_result.expectNums) == 0:
            expect_result.expectNums = [1] * len(expect_result.expectValues)

    @staticmethod
    def __parse_str_expect_result(expect_result: ExpectResult):
        assert expect_result.expectValues is not None, "'expectValues' is required"
        assert expect_result.expectNums is not None, "'expectNums' is required"
        assert len(expect_result.expectNums) == 0 or len(expect_result.expectValues) == len(
            expect_result.expectNums), "'values' length need equal 'expectNums' length"
        pass

    @staticmethod
    def __parse_file_expect_result(expect_result: ExpectResult):
        expect_value_files = expect_result.expectValueFiles
        expect_num_files = expect_result.expectNumFiles

        assert expect_value_files is not None, "'expectValueFiles' is required"
        assert expect_num_files is not None, "'expectNumFiles' is required"
        assert len(expect_num_files) == 0 or len(expect_value_files) == len(
            expect_num_files), "'expectValueFiles' length need equal 'expectNumFiles' length"
        expect_values = []
        expect_nums = []
        for index in range(len(expect_value_files)):
            expect_value_file = FileUtil.get_file_path(expect_value_files[index])
            expect_num_file = FileUtil.get_file_path(expect_num_files[index])
            assert os.path.exists(expect_value_file) and os.path.exists(
                expect_num_file), "expect_value_files or expect_num_files" \
                                  "is not exist, expect_value_files:" + str(
                expect_value_files) + "expect_num_files:" + str(expect_num_files)
            if expect_value_file.endswith(".sql"):
                __sqls = FileUtil.get_sql_file(expect_value_file)
                if len(__sqls) != 0:
                    expect_values.extend(__sqls)
            else:
                __sqls = FileUtil.get_file_lines(expect_value_file)
                if len(__sqls) != 0:
                    expect_values.extend(__sqls)
            __nums = FileUtil.get_file_lines(expect_num_file)
            if len(__nums) != 0:
                expect_nums.extend(__nums)

        expect_result.expectValues = expect_values
        expect_result.expectNums = expect_nums
        delattr(expect_result, "expectValueFiles")
        delattr(expect_result, "expectNumFiles")
        ExpectResultReader.__parse_str_expect_result(expect_result)
        pass

    @staticmethod
    def __parse_dir_expect_result(expect_result: ExpectResult):
        data_dir = expect_result.dataDir
        value_suffix = expect_result.expectValueSuffix
        expect_num_suffix = expect_result.expectNumSuffix

        assert data_dir is not None and data_dir.strip() != '', "'dataDir' is required"
        assert value_suffix is not None and value_suffix.strip() != '', "'valueSuffix' is required"
        assert expect_num_suffix is not None and expect_num_suffix.strip() != '', "'expectNumSuffix' is required"
        expect_value_files = FileUtil.get_files(data_dir, value_suffix)
        expect_num_files = []
        for file in expect_value_files:
            file_path = file[:file.find(value_suffix)] + expect_num_suffix
            if os.path.exists(file_path):
                expect_num_files.append(file_path)
        expect_result.expectValueFiles = expect_value_files
        expect_result.expectNumFiles = expect_num_files

        delattr(expect_result, "dataDir")
        delattr(expect_result, "expectValueSuffix")
        delattr(expect_result, "expectNumSuffix")

        ExpectResultReader.__parse_file_expect_result(expect_result)
        pass

    def expect_result_str(self):
        """
        返回json字符串
        :return:
        """
        return str(self.__file_json)

    def expect_result_datas(self):
        """
        返回json文件读取结果
        :return:
        """
        return self.__file_json

    def logon_properties(self):
        """
        返回登录期待结果
        :return:
        """
        return self.__logonProperties

    def access_properties(self):
        """
        返回访问期待结果
        :return:
        """
        return self.__accessProperties


class Strategy(object):
    ANY_MATCH_WORDS = '*'
    PRIMARY_KEY = 'id'
    """
    策略基类
    """
    def statistic_data(self, data: dict, expect_result: ExpectResult):
        """
        统计数据
        :param data一条审计数据
        :param expect_result期待结果实体类
        :return:
        """
        pass

    def analysis_data(self, work_sheet: sheet, *args):
        """
        分析数据生成结果
        :param work_sheet: 表格页
        :return:
        """
        pass


class SingleFieldCountStrategy(Strategy):
    """
    单一字段数量统计策略
    """
    def __init__(self):
        self.__headers = ["审计类型", "字段名", "期待数量", "实际数量", "期待值列表", "不匹配值列表", "不匹配数据id"]

    def statistic_data(self, data: dict, expect_result: ExpectResult):
        property_name = expect_result.propertyName
        values = expect_result.expectValues
        actual_nums = expect_result.actualNums

        actual_value = data[property_name]
        key = data[self.PRIMARY_KEY]
        match_flag = False
        if property_name in data and actual_value != '':
            for index, expect_value in enumerate(values):
                if expect_value == self.ANY_MATCH_WORDS or actual_value == expect_value:
                    actual_nums[index] = actual_nums[index] + 1
                    match_flag = True

        if match_flag is False:
            expect_result.notMatchValues.append(actual_value)
            expect_result.notMatchDataKeys.append(key)

    def analysis_data(self, work_sheet: sheet, *args):
        expect_results = None
        audit_type = None
        for param in args:
            if isinstance(param, AuditType):
                audit_type = param

            if isinstance(param, list) and len(param) > 0 and isinstance(param[0], ExpectResult):
                expect_results = param

        nrows = len(work_sheet.rows)
        for index, header in enumerate(self.__headers):
            work_sheet.write(nrows, index, header)

        for row_index in range(len(expect_results)):
            row = expect_results[row_index].to_list_for_out(audit_type)
            for cell_index in range(len(row)):
                work_sheet.write(row_index + 1, cell_index, str(row[cell_index]))


class TotalCountStrategy(object):
    """
    总数统计策略
    """
    def __init__(self):
        self.__accessCount = 0
        self.__accessResultCount = 0
        self.__logonCount = 0
        self.__logoffCount = 0
        self.__headers = ["访问审计数量", "访问审计结果数量", "登录数量", "登出数量"]

    def statistic_data(self, audit_type: AuditType, data: dict):
        """
        统计数据
        :param audit_type: 审计类别
        :param data: 一条数据
        :return:
        """
        assert audit_type is not None, "'audit_type' is required"
        if audit_type == AuditType.ACCESS:
            if data['是否访问结果'] == "true":
                self.__accessResultCount += 1
            else:
                self.__accessCount += 1

        if audit_type == AuditType.LOGON:
            if data['是否登录结果'] == "true":
                self.__logoffCount += 1
            else:
                self.__logonCount += 1

    def analysis_data(self, work_sheet: sheet):
        """
        分析数据
        :param work_sheet: excel完整路径
        :return:
        """
        __results = [self.__accessCount, self.__accessResultCount, self.__logonCount, self.__logoffCount]
        nrows = len(work_sheet.rows)
        for index, header in enumerate(self.__headers):
            work_sheet.write(nrows, index, header)

        nrows = len(work_sheet.rows)
        for index, result in enumerate(__results):
            work_sheet.write(nrows, index, result)
        pass


class MultipleFieldsMatchStrategy(Strategy):
    """
    多字段匹配策略
    """
    def statistic_data(self, data: dict, expect_result: ExpectResult):
        super().statistic_data(data, expect_result)

    def analysis_data(self, work_sheet: sheet, *args):
        super().analysis_data(work_sheet)


class SingleFieldStrategyDelegate(object):
    """
    策略组
    """
    def __init__(self, expect_results: list, audit_type: AuditType):
        """
        ExpectResult通过初始化策略组
        :param expect_results: 期待结果对象
        :param audit_type: 审计类型
        """
        assert audit_type is not None, "'audit_type' is required"
        self.__audit_type = audit_type
        self.__expectResults = expect_results

        self.__singleFieldCountStrategy = SingleFieldCountStrategy()
        self.__totalCountStrategy = TotalCountStrategy()
        self.__multipleFieldsMatchStrategy = MultipleFieldsMatchStrategy()

        self.__accessHeaders = HeadersConfig.get_section_columns("accessDesc")
        self.__accessResultHeaders = HeadersConfig.get_section_columns("accessResult")
        self.__logonHeaders = HeadersConfig.get_section_columns("logon")
        self.__logoffHeaders = HeadersConfig.get_section_columns("logOff")

        self.__workbook = xlwt.Workbook()

        for expectResult in expect_results:
            assert type(expectResult) is ExpectResult, "'expect_results' list element type required from " \
                                                       "common.commonUtil import ExpectResult "

    def __get_headers(self, data: dict):
        """
        获取头
        :param data: 一条记录
        :return:
        """
        if self.__audit_type == AuditType.ACCESS:
            if data['是否访问结果'] == "true":
                return self.__accessResultHeaders
            else:
                return self.__accessHeaders
        if self.__audit_type == AuditType.LOGON:
            if data['是否登录结果'] == "true":
                return self.__logoffHeaders
            else:
                return self.__logonHeaders

    def statistic_data(self, data: dict):
        """
        统计数据
        :param data: 一条row数据
        :return:
        """
        for expectResult in self.__expectResults:
            if expectResult.propertyName in self.__get_headers(data):
                self.__singleFieldCountStrategy.statistic_data(data, expectResult)
        self.__totalCountStrategy.statistic_data(self.__audit_type, data)

    def analysis_data(self):
        """
        输入分析结果
        :return:
        """
        single_field_count_sheet = self.__workbook.add_sheet("singleFieldCount")
        total_count_sheet = self.__workbook.add_sheet("totalCount")
        self.__singleFieldCountStrategy.analysis_data(single_field_count_sheet, self.__expectResults, self.__audit_type)
        self.__totalCountStrategy.analysis_data(total_count_sheet)

        if not os.path.exists(MessageConfig.output_dir):
            os.mkdir(MessageConfig.output_dir)
        self.__workbook.save(
            MessageConfig.output_dir + "/analysisResult_" + self.__audit_type.value + str(time.time()) + ".xls")
