# -*- coding:UTF-8 -*-
import getopt
import os
import subprocess
import sys
import threading
import time
from enum import Enum, unique

import xlrd

from common.commonUtil import MessageConfig, FileUtil, AuditType, SystemUtil
from common.statisticAnalysis import StrategyDelegate, SingleExpectResultParse, GroupExpectResultParse
from common.dataProcessor import PostDataExcelReaderDelegate


def __start_receive(need_clean: bool = False, filter_content: str = ''):
    """
    启动接收消息方法
    :return:
    """
    __shutdown()
    if need_clean:
        __files = []
        __files += FileUtil.get_files_prefix(MessageConfig.output_dir, AuditType.ACCESS.analysis_pre_file_name)
        __files += FileUtil.get_files_prefix(MessageConfig.output_dir, AuditType.LOGON.analysis_pre_file_name)
        for __file in __files:
            os.remove(__file)
    file_path = FileUtil.get_project_path() + "\\config\\receive-0.0.1-SNAPSHOT.jar"
    operating_system = SystemUtil.get_operating_system()
    if operating_system == 'Windows':
        command = "start javaw -jar " + file_path
    else:
        command = "nohup java -jar " + file_path
    arg0 = "--spring.activemq.broker-url=tcp://" + MessageConfig.host + ":" + str(MessageConfig.port)
    arg1 = "--spring.activemq.user=" + MessageConfig.user
    arg2 = "--spring.activemq.password=" + MessageConfig.password
    arg3 = "--message.output.path=" + MessageConfig.output_dir
    arg4 = "--message.filters=" + filter_content
    cmd = [command, arg0, arg1, arg2, arg3, arg4]
    command = " ".join(cmd)
    p = subprocess.Popen(command, shell=True, stdout=open(MessageConfig.log_dir + "receive.log", "w"),
                         stderr=subprocess.STDOUT)
    p.communicate()
    p.wait()

    time.sleep(MessageConfig.analysis_wait_time)
    __shutdown()


def __shutdown():
    """
    退出程序
    :return:
    """
    time.sleep(MessageConfig.shutdown_wait_time)
    operating_system = SystemUtil.get_operating_system()
    if operating_system == 'Windows':
        command = FileUtil.get_project_path() + "\\bin\\shutdownJar.bat"
    else:
        command = FileUtil.get_project_path() + "\\bin\\shutdownJar.sh"
    p = subprocess.Popen(command, stdout=open(MessageConfig.log_dir + "shutdown.log", "w"), stderr=subprocess.STDOUT)
    p.communicate()
    p.wait()


def __statistic_analysis_data(filter_content: str):
    """
    统计分析数据
    :return:
    """
    __output_dir = MessageConfig.output_dir
    if os.path.exists(__output_dir):
        post_data_excel_reader_delegate = PostDataExcelReaderDelegate()
        reader = SingleExpectResultParse()
        access_properties = reader.access_properties()
        logon_properties = reader.logon_properties()

        reader = GroupExpectResultParse()
        access_properties.extend(reader.access_properties())
        logon_properties.extend(reader.logon_properties())

        __access_files = FileUtil.get_files_prefix(__output_dir, AuditType.ACCESS.analysis_pre_file_name)
        access_strategy = StrategyDelegate(access_properties, AuditType.ACCESS, filter_content)
        for access_file in __access_files:
            book = xlrd.open_workbook(access_file, 'r+b')
            sheets = book.sheets()
            for sheet in sheets:
                header = sheet.row_values(0)
                for index in range(1, sheet.nrows):
                    data = dict(zip(header, sheet.row_values(index)))
                    post_data_excel_reader_delegate.merge_data(data, AuditType.ACCESS)
                    access_strategy.statistic_data(data)

        __logon_files = FileUtil.get_files_prefix(__output_dir, AuditType.LOGON.analysis_pre_file_name)
        logon_strategy = StrategyDelegate(logon_properties, AuditType.LOGON, filter_content)
        for logon_file in __logon_files:
            book = xlrd.open_workbook(logon_file, 'r+b')
            sheets = book.sheets()
            for sheet in sheets:
                header = sheet.row_values(0)
                for index in range(1, sheet.nrows):
                    data = dict(zip(header, sheet.row_values(index)))
                    post_data_excel_reader_delegate.merge_data(data, AuditType.LOGON)
                    logon_strategy.statistic_data(data)

        access_strategy.analysis_data()
        logon_strategy.analysis_data()
    pass


@unique
class OperationMode(Enum):
    RECEIVE = "receive"
    DRECEIVE = "dreceive"
    ANALYSIS = "analysis"
    SANALYSIS = "sanalysis"
    ALL = "all"


def main(argv):
    """
    主函数入口
    :return:
    """
    operation_mode = None
    receive_filters = ""
    analysis_filters = ""
    help_desc = 'usage: auditMessageTest'
    help_desc += '\n    -m,--mode <arg>            run mode'
    help_desc += '\n    -o,--output_dir <arg>      output file dir'
    help_desc += '\n    -s,--single_file <arg>     config file for single strategy analysis audit' \
                 '\n                                ,default config/expectResultConfig.xls'
    help_desc += '\n    -g,--group_file <arg>      config file for group strategy analysis audit' \
                 '\n                                ,default config/expectResultConfig.xls'
    help_desc += '\n    -l,--log_dir <arg>         log file dir'
    help_desc += '\n    -t,--time <arg>            receive audit time,union seconds'
    help_desc += '\n    -i,--ip <arg>              mq host'
    help_desc += '\n    -p,--port <arg>            mq port'
    help_desc += '\n    -u,--user <arg>            mq username'
    help_desc += '\n    -P,--password <arg>        mq password'
    help_desc += '\n    -f,--receiveFilter <arg>   data receive filter'
    help_desc += '\n    -F,--analysisFilter <arg>  data analysis filter'
    help_desc += "\n    -------------------------------------------------------------------------"

    mode_desc = '\n\n    mode：'
    mode_desc += '\n    value        desc'
    mode_desc += '\n    ------       -----------------------------'
    mode_desc += '\n    receive      receive audit records'
    mode_desc += '\n    dreceive     delete audit files and receive audit records'
    mode_desc += '\n    analysis     analysis audit records and output result'
    mode_desc += '\n    sanalysis    stop receive audit process, and analysis audit records,' \
                 '\n                 and output result'
    mode_desc += '\n    all          same effect of dreceive and analysis'
    mode_desc += "\n    --------------------------------------------------------------------------"

    filter_desc = "\n\n    filter："
    filter_desc += "\n    eg：access 规则名称 eq NETWORK,logon 客户端ip ne 127.0.0.1"
    filter_desc += "\n    access：访问记录过滤规则，logon访问记录过滤规则"
    filter_desc += "\n    规则名称：过滤字段名"
    filter_desc += "\n    eq：等于，ne：不等于"
    filter_desc += "\n    NETWORK：期待过滤的值"

    help_desc = help_desc + mode_desc + filter_desc
    try:
        opts, args = getopt.getopt(argv, "hm:o:s:g:l:t:i:p:u:P:f:F:",
                                   ["help", "mode=", "output_dir=", "single_file=", "group_file=", "log_dir=", "time=",
                                    "ip=", "port=", "user=", "password=", "receiveFilter=", "analysisFilter="])
    except getopt.GetoptError:
        print(help_desc)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_desc)
            sys.exit()
        elif opt in ("-m", "--mode"):
            operation_mode = arg
            assert operation_mode is not None and operation_mode in [mode.value for mode in
                                                                     OperationMode], \
                "'operation_mode' need in (all, receive, analysis)"

        elif opt in ("-o", "--output_dir"):
            assert arg and arg.strip(), "'output_dir' is illegal"
            MessageConfig.output_dir = arg
        elif opt in ("-s", "--single_file"):
            assert arg and arg.strip() and arg.endswith('.json'), "'single_expect_result_file' is illegal"
            MessageConfig.single_expect_result_file = arg
        elif opt in ("-g", "--group_file"):
            assert arg and arg.strip() and arg.endswith('.json'), "'group_expect_result_file' is illegal"
            MessageConfig.group_expect_result_file = arg
        elif opt in ("-l", "--log_dir"):
            assert arg and arg.strip(), "'log_dir' is illegal"
            MessageConfig.log_dir = arg
        elif opt in ("-t", "--time"):
            analysis_wait_time = int(arg)
            assert analysis_wait_time > 0, "'analysis_wait_time' must digit and greater than 0"
            MessageConfig.analysis_wait_time = analysis_wait_time
        elif opt in ("-i", "--ip"):
            assert arg and arg.strip(), "'activemq ip' is illegal"
            MessageConfig.host = arg
        elif opt in ("-p", "--port"):
            assert arg and arg.strip(), "'activemq port' is illegal"
            MessageConfig.port = int(arg)
        elif opt in ("-u", "--user"):
            assert arg and arg.strip(), "'activemq user' is illegal"
            MessageConfig.user = arg
        elif opt in ("-P", "--password"):
            assert arg and arg.strip(), "'activemq password' is illegal"
            MessageConfig.password = arg
        elif opt in ("-f", "--receiveFilter"):
            assert arg and arg.strip(), "'receiveFilter' is illegal"
            receive_filters = arg
        elif opt in ("-F", "--analysisFilter"):
            assert arg and arg.strip(), "'analysisFilter' is illegal"
            analysis_filters = arg

    __receive_thread = None
    __analysis_thread = None
    if not operation_mode or operation_mode == OperationMode.ALL.value:
        __receive_thread = threading.Thread(target=__start_receive, args=(True, receive_filters))
        __analysis_thread = threading.Thread(target=__statistic_analysis_data, args=(analysis_filters, ))
    if operation_mode == OperationMode.RECEIVE.value:
        __receive_thread = threading.Thread(target=__start_receive, args=(False, receive_filters))
    if operation_mode == OperationMode.DRECEIVE.value:
        __receive_thread = threading.Thread(target=__start_receive, args=(True, receive_filters))
    if operation_mode == OperationMode.ANALYSIS.value:
        __analysis_thread = threading.Thread(target=__statistic_analysis_data, args=(analysis_filters, ))
    if operation_mode == OperationMode.SANALYSIS.value:
        __shutdown()
        __analysis_thread = threading.Thread(target=__statistic_analysis_data, args=(analysis_filters, ))

    if __receive_thread:
        __receive_thread.start()
        pass
    if __analysis_thread:
        __analysis_thread.start()
        pass


if __name__ == '__main__':
    main(sys.argv[1:])
