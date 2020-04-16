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
