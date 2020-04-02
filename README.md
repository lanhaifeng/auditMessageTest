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