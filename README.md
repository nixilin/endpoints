这是一些用Flask实现的URL，用于接收一些平台（如sonarqube，jfrog xray）分析完毕的webhook发送的json payload，并提取出部分需要的内容，写入到MySQL。

忽略hardcode数据库连接信息（如有）。


main.py会从环境变量读取SONAR_LOGIN作为与sonarqube交互的凭证。因此 `docker run` 的时候一定记得用 `-e SONAR_LOGIN` 指定token
