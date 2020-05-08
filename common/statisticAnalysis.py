# -*- coding:UTF-8 -*-
import datetime
import json
import os
import time
from enum import unique, Enum

import xlrd
import xlwt
from xlrd import sheet

from common.commonUtil import FileUtil, AuditType, HeadersConfig, MessageConfig
from common.dataProcessor import DataFilterDelegate, CompareHandlerDelegate


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

    def __init__(self, config_type: str, property_name: str, expect_result: dict,
                 strategy_type: StrategyType = StrategyType.SINGLE_FIELD_COUNT):
        assert config_type is not None, "'config_type' is required"
        assert property_name is not None, "'property_name' is required"
        assert strategy_type is not None, "'strategy_type' is required"
        self.configType = config_type.lower()
        self.propertyName = property_name
        self.strategyType = strategy_type

        if strategy_type == StrategyType.SINGLE_FIELD_COUNT:
            self.__single_field_count_init_(config_type, expect_result)
        if strategy_type == StrategyType.MULTIPLE_FIELDS_MATCH:
            self.__multiple_fields_match_init__(config_type, expect_result)

    def __single_field_count_init_(self, config_type: str, expect_result: dict):
        """
        策略类型为StrategyType.SINGLE_FIELD_COUNT的构造处理
        :return:
        """
        self.actualNums = []
        self.notMatchValues = []
        self.notMatchDataKeys = []

        if config_type.lower() == ConfigType.STR.value.lower():
            self.expectValues = expect_result['expectValues']
            self.expectNums = expect_result['expectNums']
            if len(self.expectNums) == 0:
                self.expectNums = [1] * len(self.expectValues)

            assert self.expectValues is not None, "'expectValues' is required"
            assert self.expectNums is not None, "'expectNums' is required"
            assert len(self.expectNums) != 0 and len(self.expectValues) == len(
                self.expectNums), "'values' length need equal 'expectNums' length"
        if config_type.lower() == ConfigType.FILE.value.lower():
            self.expectValueFiles = expect_result['expectValueFiles']
            self.expectNumFiles = expect_result['expectNumFiles']
            if not self.expectNumFiles or len(self.expectNumFiles) == 0:
                for file_name in self.expectValueFiles:
                    self.expectNumFiles.append(file_name[:file_name.rindex(".")] + ".num")

            assert self.expectValueFiles is not None, "'expectValueFiles' is required"
            assert self.expectNumFiles is not None, "'expectNumFiles' is required"
            assert len(self.expectNumFiles) != 0 and len(self.expectValueFiles) == len(
                self.expectNumFiles), "'valueFiles' length need equal 'expectNumFiles' length"
        if config_type.lower() == ConfigType.DIR.value.lower():
            self.dataDir = expect_result['dataDir']
            self.expectValueSuffix = expect_result['expectValueSuffix']
            self.expectNumSuffix = expect_result['expectNumSuffix']
            if not self.expectNumSuffix or not self.expectNumSuffix.strip:
                self.expectNumSuffix = ".num"

            assert self.dataDir is not None and self.dataDir.strip() != '', "'dataDir' is required"
            assert self.expectValueSuffix is not None and self.expectValueSuffix.strip() != '', \
                "'valueSuffix' is required"
            assert self.expectNumSuffix is not None and self.expectNumSuffix.strip() != '', \
                "'expectNumSuffix' is required"

    def __multiple_fields_match_init__(self, config_type: str, expect_result: dict):
        """
        策略类型为StrategyType.MULTIPLE_FIELDS_MATCH的构造处理
        :return:
        """
        self.groupExpectValues = []
        self.notMatchGroupValues = []
        self.notMatchGroupIds = []

        self.groupInvariantExpectValues = []
        self.notMatchGroupInvariantValues = []
        self.notMatchGroupInvariantIds = []

        self.matchGroupMainColumnNum = []
        self.groupColumns = expect_result['groupColumns']
        self.mainPropertyIndex = expect_result['groupColumns'].index(self.propertyName)
        self.groupInvariantColumns = expect_result['groupInvariantColumns']
        self.groupInvariantValues = expect_result['groupInvariantValues']
        assert self.groupColumns is not None and len(self.groupColumns) != 0, "'groupColumns' is required"
        assert self.mainPropertyIndex is not None and self.mainPropertyIndex >= 0, "'mainPropertyIndex' is required"
        if self.groupInvariantColumns and len(self.groupInvariantColumns) != 0:
            assert len(self.groupInvariantColumns) == len(self.groupInvariantValues), \
                "'groupInvariantColumns' length need equal 'groupInvariantValues' element length"

        if config_type.lower() == ConfigType.STR.value.lower():
            self.groupValues = expect_result['groupValues']

            assert self.groupValues is not None, "'groupValues' is required"
            for groupValue in self.groupValues:
                assert len(self.groupColumns) == len(
                    groupValue), "'groupColumns' length need equal 'groupValues' element length"

        if config_type.lower() == ConfigType.FILE.value.lower():
            self.groupFileValues = expect_result['groupFileValues']

            assert self.groupFileValues is not None, "'groupFileValues' is required"
            assert len(self.groupColumns) == len(
                self.groupFileValues), "'groupColumns' length need equal 'groupFileValues' length"
            pass

        if config_type.lower() == ConfigType.DIR.value.lower():
            self.groupDataDir = expect_result['groupDataDir']
            self.groupSuffixValues = expect_result['groupSuffixValues']

            assert self.groupDataDir is not None, "'groupDataDir' is required"
            assert self.groupSuffixValues is not None, "'groupSuffixValues' is required"
            assert len(self.groupColumns) == len(
                self.groupSuffixValues), "'groupColumns' length need equal 'groupSuffixValues' length"
            pass

    def __str__(self):
        """
        重写方法便于输出
        :return:
        """
        result = {}
        if self.strategyType == StrategyType.SINGLE_FIELD_COUNT:
            result = {
                "字段名": self.propertyName,
                "期待值列表": self.expectValues,
                "不匹配值列表": self.notMatchValues,
                "不匹配数据id": self.notMatchDataKeys,
                "期待数量": self.expectNums,
                "实际数量": self.actualNums
            }
        if self.strategyType == StrategyType.MULTIPLE_FIELDS_MATCH:
            result = {
                "主字段名": self.propertyName,
                "分组字段列表": self.groupColumns,
                "分组期待值列表": self.groupExpectValues,
                "不匹配实际值列表": self.notMatchGroupValues,
                "不匹配数据id": self.notMatchGroupIds,
                "固定值字段列表": self.groupInvariantColumns,
                "固定期待值列表": self.groupInvariantValues,
                "不匹配固定值列表": self.notMatchGroupInvariantValues,
                "不匹配固定值数据id": self.notMatchGroupInvariantIds
            }
            pass

        return json.dumps(result, ensure_ascii=False)

    def to_list_for_out(self, audit_type: AuditType):
        """
        转为输出列表
        ["审计类型", "字段名", "期待数量", "实际数量", "期待值列表", "不匹配值列表", "不匹配数据id"]
        ["审计类型", "主字段名", "分组字段列表", "分组期待值列表", "不匹配实际值列表", "不匹配数据id",
         "固定值字段列表", "固定期待值列表", "不匹配固定值列表", "不匹配固定值数据id"]
        :param audit_type: 审计类型
        :return:
        """
        if self.strategyType == StrategyType.SINGLE_FIELD_COUNT:
            return [audit_type.desc, self.propertyName, self.expectNums, self.actualNums, self.expectValues,
                    self.notMatchValues, self.notMatchDataKeys]
        if self.strategyType == StrategyType.MULTIPLE_FIELDS_MATCH:
            for index, num in enumerate(self.matchGroupMainColumnNum):
                if num == 0:
                    self.groupExpectValues.append(self.groupValues[index])
                    self.notMatchGroupValues.append(["all datas not match"])
                    self.notMatchGroupInvariantValues.append(["all datas not match"])
            return [audit_type.desc, self.propertyName, self.groupColumns, self.groupExpectValues,
                    self.notMatchGroupValues, self.notMatchGroupIds, self.groupInvariantColumns,
                    self.groupInvariantValues, self.notMatchGroupInvariantValues, self.notMatchGroupInvariantIds]
            pass


class ExpectResultConfig(object):
    __single_expect_result_headers = ["审计类型", "字段名", "配置类型", "期待值配置", "期待数量配置", "期待数据目录"]
    __single_expect_result_sheet = "singleExpectResult"
    __single_expect_result_start_row = 1

    __group_expect_result_headers = ["审计类型", "主字段名", "配置类型", "常量字段名列表", "常量值列表", "分组字段名列表",
                                     "分组字段值配置", "分组字段数据目录"]
    __group_expect_result_sheet = "groupExpectResult"
    __group_expect_result_start_row = 1

    __single_expect_result_file = MessageConfig.single_expect_result_file
    __group_expect_result_file = MessageConfig.group_expect_result_file
    assert __single_expect_result_file is not None, "'single_expect_result_file' is required"
    assert __group_expect_result_file is not None, "'group_expect_result_file' is required"

    single_expect_json = None
    group_expect_json = None
    if __single_expect_result_file.endswith(".json"):
        __file = open(__single_expect_result_file, "rb")
        single_expect_json = json.load(__file)
        __file.close()
    elif __single_expect_result_file.endswith(".xls"):
        single_expect_json = {
            "logonProperties": [],
            "accessProperties": []
        }
        book = xlrd.open_workbook(__single_expect_result_file, 'r+b')
        sheet = book.sheet_by_name(__single_expect_result_sheet)
        for index in range(__single_expect_result_start_row, sheet.nrows):
            __data = dict(zip(__single_expect_result_headers, sheet.row_values(index)))
            __auditType = __data[__single_expect_result_headers[0]]
            __configType = __data[__single_expect_result_headers[2]]
            __json_row = {
                "propertyName": __data[__single_expect_result_headers[1]],
                "configType": __configType
            }
            if __configType == "str":
                __json_row['expectResult'] = {
                    "expectValues": json.loads(__data[__single_expect_result_headers[3]]),
                    "expectNums": json.loads(__data[__single_expect_result_headers[4]])
                }
            if __configType == "file":
                __json_row['expectResult'] = {
                    "expectValueFiles": json.loads(__data[__single_expect_result_headers[3]]),
                    "expectNumFiles": json.loads(__data[__single_expect_result_headers[4]])
                }
            if __configType == "dir":
                __json_row['expectResult'] = {
                    "dataDir": __data[__single_expect_result_headers[5]],
                    "expectValueSuffix": __data[__single_expect_result_headers[3]],
                    "expectNumSuffix": __data[__single_expect_result_headers[4]]
                }
            if __auditType == AuditType.LOGON.value:
                single_expect_json['logonProperties'].append(__json_row)
            if __auditType == AuditType.ACCESS.value:
                single_expect_json['accessProperties'].append(__json_row)
        pass

    if __group_expect_result_file.endswith(".json"):
        __file = open(__group_expect_result_file, "rb")
        group_expect_json = json.load(__file)
        __file.close()
    elif __group_expect_result_file.endswith(".xls"):
        group_expect_json = {
            "logonProperties": [],
            "accessProperties": []
        }
        book = xlrd.open_workbook(__group_expect_result_file, 'r+b')
        sheet = book.sheet_by_name(__group_expect_result_sheet)
        for index in range(__group_expect_result_start_row, sheet.nrows):
            __data = dict(zip(__group_expect_result_headers, sheet.row_values(index)))
            __auditType = __data[__group_expect_result_headers[0]]
            __configType = __data[__group_expect_result_headers[2]]
            __json_row = {
                "propertyName": __data[__group_expect_result_headers[1]],
                "configType": __configType,
                "expectResult": {
                    "groupColumns": json.loads(__data[__group_expect_result_headers[5]]),
                    "groupInvariantColumns": json.loads(__data[__group_expect_result_headers[3]]),
                    "groupInvariantValues": json.loads(__data[__group_expect_result_headers[4]])
                }
            }
            if __configType == "str":
                __json_row['expectResult']["groupValues"] = json.loads(__data[__group_expect_result_headers[6]])
            if __configType == "file":
                __json_row['expectResult']["groupFileValues"] = json.loads(__data[__group_expect_result_headers[6]])
            if __configType == "dir":
                __json_row['expectResult']["groupSuffixValues"] = json.loads(__data[__group_expect_result_headers[6]])
                __json_row['expectResult']["groupDataDir"] = __data[__group_expect_result_headers[7]]
            if __auditType == AuditType.LOGON.value:
                group_expect_json['logonProperties'].append(__json_row)
            if __auditType == AuditType.ACCESS.value:
                group_expect_json['accessProperties'].append(__json_row)
        pass

    assert single_expect_json, "'single_expect_json' is required"
    assert group_expect_json, "'group_expect_json' is required"


class SingleExpectResultParse(object):
    """
    期待结果读取
    """

    def __init__(self, strategy_type: StrategyType = StrategyType.SINGLE_FIELD_COUNT):
        """
        初始化方法，读取json文件
        """
        if strategy_type == StrategyType.SINGLE_FIELD_COUNT:
            self.__file_json = ExpectResultConfig.single_expect_json
        if strategy_type == StrategyType.MULTIPLE_FIELDS_MATCH:
            self.__file_json = ExpectResultConfig.group_expect_json

        assert 'logonProperties' in self.__file_json or 'accessProperties' in self.__file_json, \
            "'logonProperties' or 'accessProperties' is required"

        self.__logonProperties = []
        self.__accessProperties = []
        if 'logonProperties' in self.__file_json:
            for expect_result in self.__file_json['logonProperties']:
                self.__logonProperties.append(ExpectResult(expect_result['configType'], expect_result['propertyName'],
                                                           expect_result['expectResult'], strategy_type))

        if 'accessProperties' in self.__file_json:
            for expect_result in self.__file_json['accessProperties']:
                self.__accessProperties.append(ExpectResult(expect_result['configType'], expect_result['propertyName'],
                                                            expect_result['expectResult'], strategy_type))

        for expect_result in self.__logonProperties:
            self._parse_expect_result(expect_result)

        for expect_result in self.__accessProperties:
            self._parse_expect_result(expect_result)

    def _parse_expect_result(self, expect_result: ExpectResult):
        config_type = expect_result.configType
        if config_type.lower() == ConfigType.STR.value.lower():
            self._parse_str_expect_result(expect_result)
        if config_type.lower() == ConfigType.FILE.value.lower():
            self._parse_file_expect_result(expect_result)
        if config_type.lower() == ConfigType.DIR.value.lower():
            self._parse_dir_expect_result(expect_result)

        if expect_result.strategyType == StrategyType.SINGLE_FIELD_COUNT:
            if len(expect_result.actualNums) == 0:
                expect_result.actualNums = [0] * len(expect_result.expectValues)

    @staticmethod
    def _parse_str_expect_result(expect_result: ExpectResult):
        assert expect_result.expectValues is not None, "'expectValues' is required"
        assert expect_result.expectNums is not None, "'expectNums' is required"
        assert len(expect_result.expectNums) != 0 and len(expect_result.expectValues) == len(
            expect_result.expectNums), "'values' length need equal 'expectNums' length"
        pass

    @staticmethod
    def _parse_file_expect_result(expect_result: ExpectResult):
        expect_value_files = expect_result.expectValueFiles
        expect_num_files = expect_result.expectNumFiles

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
        SingleExpectResultParse._parse_str_expect_result(expect_result)
        pass

    @staticmethod
    def _parse_dir_expect_result(expect_result: ExpectResult):
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

        SingleExpectResultParse._parse_file_expect_result(expect_result)
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


class GroupExpectResultParse(SingleExpectResultParse):

    def __init__(self, strategy_type: StrategyType = StrategyType.MULTIPLE_FIELDS_MATCH):
        super().__init__(strategy_type)

    @staticmethod
    def _parse_str_expect_result(expect_result: ExpectResult):
        assert expect_result.groupValues is not None, "'groupValues' is required"
        for groupValue in expect_result.groupValues:
            assert len(expect_result.groupColumns) == len(
                groupValue), "'groupColumns' length need equal 'groupValues' element length"
        expect_result.matchGroupMainColumnNum = [0] * len(expect_result.groupValues)

    @staticmethod
    def _parse_file_expect_result(expect_result: ExpectResult):
        group_file_values = expect_result.groupFileValues
        main_property_index = expect_result.mainPropertyIndex

        group_values = [[]] * len(expect_result.groupColumns)
        for columnIndex in range(len(expect_result.groupColumns)):
            for file_index in range(len(group_file_values[columnIndex])):
                group_value_file = FileUtil.get_file_path(group_file_values[columnIndex][file_index])
                assert os.path.exists(group_value_file), "'groupFileValue' is not exist, group_value_file:" + str(
                    group_value_file)
                if group_value_file.endswith(".sql"):
                    __group_value = FileUtil.get_sql_file(group_value_file)
                    if __group_value is not None and len(__group_value) != 0:
                        group_values[columnIndex] = group_values[columnIndex] + __group_value
                else:
                    __group_value = FileUtil.get_file_lines(group_value_file)
                    if __group_value is not None and len(__group_value) != 0:
                        group_values[columnIndex] = group_values[columnIndex] + __group_value

        expect_group_values = [[''] * len(expect_result.groupColumns)] * len(group_values[main_property_index])
        for row_index in range(len(group_values[main_property_index])):
            for cell_index in range(len(expect_result.groupColumns)):
                expect_group_values[row_index][cell_index] = group_values[cell_index][row_index]
        expect_result.groupValues = expect_group_values
        expect_result.matchGroupMainColumnNum = [0] * len(expect_result.groupValues)
        delattr(expect_result, "groupFileValues")

    @staticmethod
    def _parse_dir_expect_result(expect_result: ExpectResult):
        group_data_dir = expect_result.groupDataDir
        group_suffix_values = expect_result.groupSuffixValues
        assert group_data_dir is not None and group_data_dir.strip() != '', "'groupDataDir' is required"
        assert group_suffix_values is not None and len(group_suffix_values) != 0, \
            "'groupSuffixValues' is required"
        _group_value_files = [[]] * len(expect_result.groupColumns)
        for index in range(len(expect_result.groupColumns)):
            _group_value_files[index] = FileUtil.get_files(group_data_dir, group_suffix_values[index])

        expect_result.groupFileValues = _group_value_files
        delattr(expect_result, "groupDataDir")
        delattr(expect_result, "groupSuffixValues")

        GroupExpectResultParse._parse_file_expect_result(expect_result)


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
                if CompareHandlerDelegate.equals(property_name, actual_value, expect_value):
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
            if expect_results[row_index].strategyType == StrategyType.SINGLE_FIELD_COUNT:
                row = expect_results[row_index].to_list_for_out(audit_type)
                for cell_index in range(len(row)):
                    work_sheet.write(row_index + 1, cell_index, str(row[cell_index]))


class TotalCountStrategy(object):
    """
    总数统计策略
    """
    def __init__(self, audit_type: AuditType):
        assert audit_type is not None, "'audit_type' is required"

        self.__auditType = audit_type
        self.__accessCount = 0
        self.__accessResultCount = 0
        self.__logonCount = 0
        self.__logoffCount = 0
        self.__cmdTypeCount = {}
        if audit_type == AuditType.ACCESS:
            self.__headers = ["访问审计数量", "访问审计执行结果数量"]
        if audit_type == AuditType.LOGON:
            self.__headers = ["登录数量", "登出数量"]

    def statistic_data(self, data: dict):
        """
        统计数据
        :param data: 一条数据
        :return:
        """
        if self.__auditType == AuditType.ACCESS:
            if data['是否访问审计执行结果'] == "true":
                self.__accessResultCount += 1
            else:
                self.__accessCount += 1
            if "操作类型" in data.keys():
                __type = data["操作类型"]
                __count = 0
                if __type in self.__cmdTypeCount.keys():
                    __count = self.__cmdTypeCount[__type]
                __count += 1
                self.__cmdTypeCount[__type] = __count

        if self.__auditType == AuditType.LOGON:
            if data['是否登出审计'] == "true":
                self.__logoffCount += 1
            else:
                self.__logonCount += 1

    def analysis_data(self, work_sheet: sheet):
        """
        分析数据
        :param work_sheet: excel完整路径
        :return:
        """
        __results = []
        if self.__auditType == AuditType.ACCESS:
            __results = [self.__accessCount, self.__accessResultCount]
            self.__headers += self.__cmdTypeCount.keys()
            __results += self.__cmdTypeCount.values()
        if self.__auditType == AuditType.LOGON:
            __results = [self.__logonCount, self.__logoffCount]

        nrows = len(work_sheet.rows)
        for index, header in enumerate(self.__headers):
            work_sheet.write(nrows + index, 0, header)
            work_sheet.write(nrows + index, 1, __results[index])


class MultipleFieldsMatchStrategy(Strategy):

    """
    多字段匹配策略
    """

    def __init__(self) -> None:
        self.__headers = ["审计类型", "主字段名", "分组字段列表", "分组期待值列表", "不匹配实际值列表", "不匹配数据id",
                          "固定值字段列表", "固定期待值列表", "不匹配固定值列表", "不匹配固定值数据id"]

    def statistic_data(self, data: dict, expect_result: ExpectResult):
        super().statistic_data(data, expect_result)
        main_property_name = expect_result.propertyName
        main_property_index = expect_result.mainPropertyIndex
        group_columns = expect_result.groupColumns
        group_values = expect_result.groupValues
        group_invariant_columns = expect_result.groupInvariantColumns
        group_invariant_values = expect_result.groupInvariantValues

        for row_index, row in enumerate(group_values):
            # 主字段值比较
            if CompareHandlerDelegate.equals(main_property_name, data[main_property_name], row[main_property_index]):
                match = True
                not_match_value = []
                expect_result.matchGroupMainColumnNum[row_index] = expect_result.matchGroupMainColumnNum[row_index] + 1

                # 固定字段值进行比较
                for index, column in enumerate(group_invariant_columns):
                    not_match_value.append(data[column])
                    if not CompareHandlerDelegate.equals(column, data[column], group_invariant_values[index]):
                        match = False
                if not match:
                    expect_result.groupInvariantExpectValues.append(row)
                    expect_result.notMatchGroupInvariantValues.append(not_match_value)
                    expect_result.notMatchGroupInvariantIds.append(data[self.PRIMARY_KEY])

                # 分组字段值进行比较
                for index, column in enumerate(group_columns):
                    not_match_value.append(data[column])
                    if not CompareHandlerDelegate.equals(column, data[column], row[index]):
                        match = False
                if not match:
                    expect_result.groupExpectValues.append(row)
                    expect_result.notMatchGroupValues.append(not_match_value)
                    expect_result.notMatchGroupIds.append(data[self.PRIMARY_KEY])
        pass

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
        if expect_results is not None:
            for row_index in range(len(expect_results)):
                if expect_results[row_index].strategyType == StrategyType.MULTIPLE_FIELDS_MATCH:
                    row = expect_results[row_index].to_list_for_out(audit_type)
                    for cell_index in range(len(row)):
                        work_sheet.write(row_index + 1, cell_index, str(row[cell_index]))


class StrategyDelegate(object):
    """
    策略组
    """
    def __init__(self, expect_results: list, audit_type: AuditType, filter_content: str):
        """
        ExpectResult通过初始化策略组
        :param expect_results: 期待结果对象
        :param audit_type: 审计类型
        """
        assert audit_type is not None, "'audit_type' is required"
        self.__audit_type = audit_type
        self.__expectResults = expect_results

        self.__singleFieldCountStrategy = SingleFieldCountStrategy()
        self.__totalCountStrategy = TotalCountStrategy(audit_type)
        self.__multipleFieldsMatchStrategy = MultipleFieldsMatchStrategy()

        self.__accessHeaders = HeadersConfig.get_section_columns("accessDesc")
        self.__accessResultHeaders = HeadersConfig.get_section_columns("accessResult")
        self.__logonHeaders = HeadersConfig.get_section_columns("logon")
        self.__logoffHeaders = HeadersConfig.get_section_columns("logOff")

        self.__workbook = xlwt.Workbook()

        if filter_content and filter_content.strip():
            self.__dataFilterDelegate = DataFilterDelegate(filter_content)
        else:
            self.__dataFilterDelegate = None

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
            if data['是否访问审计执行结果'] == "true":
                return self.__accessResultHeaders
            else:
                return self.__accessHeaders
        if self.__audit_type == AuditType.LOGON:
            if data['是否登出审计'] == "true":
                return self.__logoffHeaders
            else:
                return self.__logonHeaders

    def statistic_data(self, data: dict):
        """
        统计数据
        :param data: 一条row数据
        :return:
        """
        if self.__dataFilterDelegate is None or self.__dataFilterDelegate.filter(data, self.__audit_type):
            for expectResult in self.__expectResults:
                if expectResult.propertyName in self.__get_headers(data):
                    if expectResult.strategyType == StrategyType.SINGLE_FIELD_COUNT:
                        self.__singleFieldCountStrategy.statistic_data(data, expectResult)
                    if expectResult.strategyType == StrategyType.MULTIPLE_FIELDS_MATCH:
                        self.__multipleFieldsMatchStrategy.statistic_data(data, expectResult)
            self.__totalCountStrategy.statistic_data(data)

    def analysis_data(self):
        """
        输入分析结果
        :return:
        """
        single_field_count_sheet = self.__workbook.add_sheet("singleFieldCount")
        multiple_field_match_sheet = self.__workbook.add_sheet("multipleFieldMatch")
        total_count_sheet = self.__workbook.add_sheet("totalCount")
        __single_expectResults = []
        __multiple_expectResults = []
        for expectResult in self.__expectResults:
            if expectResult.strategyType == StrategyType.SINGLE_FIELD_COUNT:
                __single_expectResults.append(expectResult)
            if expectResult.strategyType == StrategyType.MULTIPLE_FIELDS_MATCH:
                __multiple_expectResults.append(expectResult)

        self.__singleFieldCountStrategy.analysis_data(single_field_count_sheet, __single_expectResults,
                                                      self.__audit_type)
        self.__multipleFieldsMatchStrategy.analysis_data(multiple_field_match_sheet, __multiple_expectResults,
                                                         self.__audit_type)
        self.__totalCountStrategy.analysis_data(total_count_sheet)

        if not os.path.exists(MessageConfig.output_dir):
            os.mkdir(MessageConfig.output_dir)
        self.__workbook.save(
            MessageConfig.output_dir + "/analysisResult_" + self.__audit_type.value + "_"
            + datetime.datetime.now().strftime(
                "%Y_%m_%d_%H%M%S.%f")[:-3] + ".xls")
