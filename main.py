import os
import subprocess
import threading
import time

import xlrd

from common.commonUtil import MessageConfig, FileUtil, AuditType, SystemUtil
from common.statisticAnalysis import SingleFieldStrategyDelegate, ExpectResultReader, GroupExpectResultReader


def __start_receive():
    """
    启动接收消息方法
    :return:
    """
    file_path = FileUtil.get_project_path() + "\\config\\receive-0.0.1-SNAPSHOT.jar"
    operating_system = SystemUtil.get_operating_system()
    if operating_system == 'Windows':
        command = FileUtil.get_project_path() + "\\bin\\startJar.bat"
    else:
        command = "nohup java -jar " + file_path
        arg0 = "--spring.activemq.broker-url=tcp://192.168.230.24:61615"
        arg1 = "--message.output.path=" + MessageConfig.output_dir
        cmd = [command, arg0, arg1]
        command = " ".join(cmd)
    p = subprocess.Popen(command, shell=True, stdout=open(MessageConfig.log_dir + "receive.log", "w"),
                         stderr=subprocess.STDOUT)
    p.communicate()
    p.wait()


def __shutdown():
    """
    退出程序
    :return:
    """
    time.sleep(MessageConfig.shutdown_wait_time)
    operating_system = SystemUtil.get_operating_system()
    if operating_system == 'Windows':
        command = FileUtil.get_project_path() + "\\bin\\shutdown.bat"
    else:
        command = FileUtil.get_project_path() + "\\bin\\shutdown.sh"
    p = subprocess.Popen(command, stdout=open(MessageConfig.log_dir + "shutdown.log", "w"), stderr=subprocess.STDOUT)
    p.communicate()
    p.wait()


def __statistic_analysis_data():
    """
    统计分析数据
    :return:
    """
    time.sleep(MessageConfig.analysis_wait_time)
    __output_dir = MessageConfig.output_dir
    if os.path.exists(__output_dir):
        reader = ExpectResultReader(MessageConfig.expect_result_file)
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
    __shutdown()
    pass


def main():
    """
    主函数入口
    :return:
    """
    __receive_thread = threading.Thread(target=__start_receive())
    __analysis_thread = threading.Thread(target=__statistic_analysis_data())
    __receive_thread.start()
    __analysis_thread.start()


if __name__ == '__main__':
    main()
