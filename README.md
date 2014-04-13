## Simple Blog On SAE

###1.说明
使用[bottle 0.9.6](http://https://pypi.python.org/pypi/bottle/0.9.6)搭建一个非常简单的blog。

解析 sae所提供的[storage](http://sae.sina.com.cn/doc/python/storage.html)中的md文件，生成html，并显示到页面上。

###2.如果你还不熟悉sae
[新手入门](http://sae.sina.com.cn/doc/tutorial/index.html)

[SAE python入门指南](http://sae.sina.com.cn/doc/python/tutorial.html)

###3. 代码结构
1/    #version 1. 主程序

storage/   #模拟sae storage, 本地测试使用


###4. 本地测试方法
dev_server.py --storage-path=../storage/

[sae本地开发环境](http://sae.sina.com.cn/doc/python/tools.html#id2)
