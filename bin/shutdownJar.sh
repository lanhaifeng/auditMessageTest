#!/bin/bash
kill -s 9 `ps -aux | grep receive-0.0.1-SNAPSHOT.jar | awk '{print $2}'`