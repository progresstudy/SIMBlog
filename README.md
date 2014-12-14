SIMBlog
=======

部署在SAE上的blog系统

部署方法

  1. 到SAE上创建应用，选择python环境，创建 私有storage，名称 articles
  2. 从github上clone simblog代码到本地
  3. 更改simblog/1/config.yaml 文件， name设置成SAE上申请的应用名
  4. 更改simblog/1/setting.py文件, 根据情况，设置SITENAME，AUTHOR，TAGLINE，ABOUT_ME，EMAIL等信息
  5. 把更改后的所有文件上传到 SAE提供的svn地址
  6. 打开浏览器，访问对应子域名，是否成功部署
  
使用方法

  1. simblog上传文章通过两种方法：

  1.1 通过使用Cyberduck来上传文章到SAE的storage中，Cyberduck使用方法，见：http://sae.sina.com.cn/doc/python/storage.html
  
  1.2 通过设置github的webhook，监听pushevent，
  更新、添加文章到bolg系统，github的webhook介绍：https://developer.github.com/webhooks/
  
  webhook使用方法：http://jingyan.baidu.com/article/5d6edee228c88899ebdeec47.html
  注：webhook中添加的url 为 <子域名>.sinaapp.com/article/<PULL_SECRET> 
  其中 PULL_SECRET 定义在 setting.py文件中，建议进行更改
