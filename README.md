# auditMessageTest

### docker搭建activemq环境
```xml
docker run -p 61616:61616 -p 61613:61613 -p 8161:8161  -d rmohr/activemq
```

### 需要的python模块
  + stomp.py
  + configparser
  + protobuf
  
### 根据proto生成py文件
将protoActiveMq.proto拷贝到exe下执行
```xml
protoc --python_out=. ./protoActiveMq.proto
```

### 有缺省参数并指明类型
```python
def show(name: str = "python"):
    pass
```

### expectResult.json
|  字段名    |    类型  |   描述   |
| ---- | ---- | ---- |
|   logonProperties  |   json对象         |  登录属性字段集合，与accessProperties至少配置一个    |
|   accessProperties |   json对象         |  访问属性字段集合，与logonProperties至少配置一个    |
|   propertyName     |   字符串            |   属性名，必填            |
|   configType       |   字符串            |   期待结果配置类型，支持str、file、dir，必填            |
|   expectResult     |   json对象          |   期待结果，必填            |

####expectResult
|  字段名    |    类型  |   描述   |
| ---- | ---- | ---- |
|   values           |   json数组         |  期待值数组，configType为str，*表示任意匹配，必填                              |
|   expectNums       |   json数组         |  期待值次数数组，configType为str，需要与上边数组一一对应，为空表示默认匹配1次     |
|   valueFiles       |   json数组         |  期待值文件路径，configType为file，必填                                       |
|   expectNumFiles   |   json数组         |  期待值次数文件路径，configType为file，与上边文件一一对应，必填                  |
|   dir              |   字符串           |  期待结果目录，不支持嵌套目录，必填                                             |
|   valueSuffix      |   字符串           |  期待值文件后缀，必填                                                         |
|   expectNumSuffix  |   字符串           |  期待值次数文件后缀，必填                                                     |

#### 二期修改
```text
过滤器处理
总数统计分类
分组主字段匹配
配置的约定
配置文件excel
stop+分析
时间格式化
匹配字段记录主键，关联后期字段
sql语句比较特殊化处理(原始SQL简单分词比较，标准化SQL)
```

####命令解析

过滤配置
例子：
```text
-f "access 规则名称 eq NETWORK,logon 客户端ip ne 127.0.0.1" 
```

|  参数名    |    可选值  |   描述   |
| ---- | ---- | ---- |
|   参数1，数据来源          |      access,logon      | access访问审计，logon登录审计 |
|   参数2，字段名       |   规则名称，见下表可选字段名         |  excel头字段名     |
|   参数3，操作符       |   eq,ne         |eq等于，ne不等于  |
|   参数4，具体值   |   填写期望过滤对应的值    |  |

访问可选字段名
```text
规则名称
操作类型
资产名
执行结果
审计级别
客户端IP
客户端端口
服务端IP
服务端端口
数据库用户
保护对象名
终端应用
终端IP
终端用户
```
登录可选字段名
```text
规则名称
数据库用户
应用程序
客户端IP
客户端端口
服务端IP
服务端端口
保护对象名
数据库实例
数据库主机名
操作系统用户
执行结果
审计级别
```

####约定规则
expectResult中
1.  当配置类型=str时，期待数量不配置，约定期待数量为1，例如：  
期待值列表=["test1", "test2"]  
默认期待数量列表=[1, 1]  
2.  当配置类型=file时，期待数量文件名与期待值文件名和路径一样，约定后缀使用.num，例如：  
期待值文件名=classpath:/test/sql/test1.sql  
默认期待数量文件名=classpath:/test/sql/test1.num  
3.  当配置类型=dir时，期待数量文件使用和期待值文件相同的文件名和路径，例如：  
期待值后缀=.sql，存在文件/test/sql/test1.sql  
期待值后缀=.num，使用文件/test/sql/test1.num  

groupExpectResult中
1.  当配置类型=dir时，分组字段文件名和路径与主字段相同，例如：  
分组字段后缀=[".sql", ".text1", ".text2"]，主字段后缀为.sql，存在文件/test/sql/test1.sql  
其他两个字段文件为/test/sql/test1.text1，/test/sql/test1.text2

#### 使用说明
auditMessageTest用于接收和统计分析消息中间件中的审计消息，目前只支持activemq消息中间件。  
*环境：*
1. 安装python3并配置环境变量
2. 安装jdk8并配置环境变量

*使用：*  
查看帮助信息  
python auditMessageTest -h  
```text
usage: auditMessageTest
    -m,--mode <arg>            run mode
    -o,--output_dir <arg>      output file dir
    -s,--single_file <arg>     config file for single strategy analysis audit
                                ,default config/expectResultConfig.xls
    -g,--group_file <arg>      config file for group strategy analysis audit
                                ,default config/expectResultConfig.xls
    -l,--log_dir <arg>         log file dir
    -t,--time <arg>            receive audit time,union seconds
    -i,--ip <arg>              mq host
    -p,--port <arg>            mq port
    -u,--user <arg>            mq username
    -P,--password <arg>        mq password
    -f,--filter <arg>          data analysis filter
    -------------------------------------------------------------------------

    mode：
    value        desc
    ------       -----------------------------
    receive      receive audit records
    dreceive     delete audit files and receive audit records
    analysis     analysis audit records and output result
    sanalysis    stop receive audit process, and analysis audit records,
                 and output result
    all          same effect of dreceive and analysis
    --------------------------------------------------------------------------

    filter：
    eg：access 规则名称 eq NETWORK,logon 客户端ip ne 127.0.0.1
    access：访问记录过滤规则，logon访问记录过滤规则
    规则名称：过滤字段名
    eq：等于，ne：不等于
    NETWORK：期待过滤的值
```
参数说明
+ -m,--mode [receive|dreceive|analysis|sanalysis|all]  
运行模式  
receive：接收消息  
dreceive：删除旧的数据文件，再receive  
analysis：分析数据
sanalysis：停止receive的java进程，再analysis
all： 停止receive的java进程，再dreceive，再analysis  

+ -o,--output_dir <arg>  
数据输出目录  

+ -s,--single_file <arg>   
单字段分析的配置文件路径，默认在项目为config/expectResultConfig.xls  

+ -g,--group_file <arg>  
分组字段分析的配置文件路径，默认在项目为config/expectResultConfig.xls  

+ -l,--log_dir <arg>  
日志目录，默认为/log/  

+ -t,--time <arg>  
接收审计的时间，单位秒

+ -i,--ip <arg>  
activemq的ip地址，默认127.0.0.1

+ -p,--port <arg>
activemq的端口，默认61615

+ -u,--user <arg>  
activemq的用户，默认hzmcmq

+ -P,--password <arg>  
activemq的密码，默认hzmcmq@2017

+ -f,--filter <arg>  
数据分析的过滤配置，格式"审计类型 字段名 操作符 值"，多个过滤用,分隔

例子：
1. 接收192.168.230.206上审计60s，数据保存到output
```text
python auditMessageTest -m receive -o /output/ -i 192.168.230.206  -t 60
```

2. 接收192.168.230.206上审计60s，数据保存到output并删除之前的审计
```text
python auditMessageTest -m dreceive -o /output/ -i 192.168.230.206  -t 60
```

4. 分析output下审计，指定单字段分析配置文件为/config/single.xls，分组字段
分析配置文件为/config/group.xls
```text
python auditMessageTest -m analysis -o /output/ -s /config/single.xls -g /config/group.xls
```

5. 分析output下审计，只分析访问审计保护对象名为ora_202_2_1521，登录审计规则名不为LOGON，
指定单字段分析配置文件为/config/single.xls，分组字段
分析配置文件为/config/group.xls
```text
python auditMessageTest -m analysis -o /output/ -s /config/single.xls -g /config/group.xls 
-f "access 保护对象名 eq ora_202_2_1521,logon 规则名称 ne LOGON"
```