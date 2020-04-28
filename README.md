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

