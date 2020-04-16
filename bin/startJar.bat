@echo off
start javaw -jar D:\core\auditMessageTest\config\receive-0.0.1-SNAPSHOT.jar --spring.activemq.broker-url=tcp://192.168.230.206:61615 --message.output.path=/out/
echo ------------ start success --------------