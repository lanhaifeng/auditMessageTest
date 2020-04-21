import getopt
import os
import subprocess
import sys
import threading
import time
from enum import Enum, unique

import xlrd

from common.commonUtil import MessageConfig, FileUtil, AuditType, SystemUtil
from common.statisticAnalysis import SingleFieldStrategyDelegate, SingleExpectResultReader, GroupExpectResultReader


def __start_receive():
    """
    启动接收消息方法
    :return:
    """
    file_path = FileUtil.get_project_path() + "\\config\\receive-0.0.1-SNAPSHOT.jar"
    operating_system = SystemUtil.get_operating_system()
    if operating_system == 'Windows':
        command = "start javaw -jar " + file_path
    else:
        command = "nohup java -jar " + file_path
    arg0 = "--spring.activemq.broker-url=tcp://" + MessageConfig.host + str(MessageConfig.port)
    arg1 = "--spring.activemq.user=" + MessageConfig.user
    arg2 = "--spring.activemq.password=" + MessageConfig.password
    arg3 = "--message.output.path=" + MessageConfig.output_dir
    cmd = [command, arg0, arg1, arg2, arg3]
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


def __statistic_analysis_data():
    """
    统计分析数据
    :return:
    """
    __output_dir = MessageConfig.output_dir
    if os.path.exists(__output_dir):
        reader = SingleExpectResultReader(MessageConfig.single_expect_result_file)
        access_properties = reader.access_properties()
        logon_properties = reader.logon_properties()

        reader = GroupExpectResultReader(MessageConfig.group_expect_result_file)
        access_properties.extend(reader.access_properties())
        logon_properties.extend(reader.logon_properties())

        __access_files = FileUtil.get_files_prefix(__output_dir, AuditType.ACCESS.value.upper())
        access_strategy = SingleFieldStrategyDelegate(access_properties, AuditType.ACCESS)
        for access_file in __access_files:
            book = xlrd.open_workbook(access_file, 'w+b')
            sheets = book.sheets()
            for sheet in sheets:
                header = sheet.row_values(0)
                for index in range(1, sheet.nrows):
                    data = dict(zip(header, sheet.row_values(index)))
                    access_strategy.statistic_data(data)

        __logon_files = FileUtil.get_files_prefix(__output_dir, AuditType.ACCESS.value.upper())
        logon_strategy = SingleFieldStrategyDelegate(logon_properties, AuditType.LOGON)
        for logon_file in __logon_files:
            book = xlrd.open_workbook(logon_file, 'w+b')
            sheets = book.sheets()
            for sheet in sheets:
                header = sheet.row_values(0)
                for index in range(1, sheet.nrows):
                    data = dict(zip(header, sheet.row_values(index)))
                    logon_strategy.statistic_data(data)

        access_strategy.analysis_data()
        logon_strategy.analysis_data()
    sys.exit()
    pass


@unique
class OperationMode(Enum):
    RECEIVE = "receive"
    ANALYSIS = "analysis"
    ALL = "all"


def main(argv):
    """
    主函数入口
    :return:
    """
    operation_mode = None
    help_desc = 'python auditMessageTest -m <mode:receive,analysis,all> -o <output_dir> -s <single_file> ' \
                '-g <group_file> -l <log_dir> -t <time:receive and write data time> -i <ip:activemq ip>' \
                ' -p <port:activemq port> -u <user:activemq user> -w <password:activemq passwod>'
    try:
        opts, args = getopt.getopt(argv, "hm:o:s:g:l:t:i:p:u:w",
                                   ["help", "mode=", "output_dir=", "single_file=", "group_file=", "log_dir=", "time=",
                                    "ip=", "port=", "user=", "password="])
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
            assert arg is not None and arg != '', "'output_dir' is illegal"
            MessageConfig.output_dir = arg
        elif opt in ("-s", "--single_file"):
            assert arg is not None and arg != '' and arg.endswith('.json'), "'single_expect_result_file' is illegal"
            MessageConfig.single_expect_result_file = arg
        elif opt in ("-g", "--group_file"):
            assert arg is not None and arg != '' and arg.endswith('.json'), "'group_expect_result_file' is illegal"
            MessageConfig.group_expect_result_file = arg
        elif opt in ("-l", "--log_dir"):
            assert arg is not None and arg != '', "'log_dir' is illegal"
            MessageConfig.log_dir = arg
        elif opt in ("-t", "--time"):
            analysis_wait_time = int(arg)
            assert analysis_wait_time > 0, "'analysis_wait_time' must digit and greater than 0"
            MessageConfig.analysis_wait_time = analysis_wait_time
        elif opt in ("-i", "--ip"):
            assert arg is not None and arg != '', "'activemq ip' is illegal"
            MessageConfig.host = arg
        elif opt in ("-p", "--port"):
            assert arg is not None and arg != '', "'activemq port' is illegal"
            MessageConfig.port = int(arg)
        elif opt in ("-u", "--user"):
            assert arg is not None and arg != '', "'activemq user' is illegal"
            MessageConfig.user = arg
        elif opt in ("-w", "--password"):
            assert arg is not None and arg != '', "'activemq password' is illegal"
            MessageConfig.password = arg
    if operation_mode is None or operation_mode == OperationMode.ALL.value:
        __receive_thread = threading.Thread(target=__start_receive())
        __analysis_thread = threading.Thread(target=__statistic_analysis_data())
    if operation_mode == OperationMode.RECEIVE.value:
        __receive_thread = threading.Thread(target=__start_receive())
    if operation_mode == OperationMode.ANALYSIS.value:
        __analysis_thread = threading.Thread(target=__statistic_analysis_data())


if __name__ == '__main__':
    main(sys.argv[1:])
