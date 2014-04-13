saesimpleblog
=============
## Simple Blog On SAE

###1.说明
使用[bottle 0.9.6](http://https://pypi.python.org/pypi/bottle/0.9.6)搭建一个非常简单的blog。

解析 sae所提供的[storage](http://sae.sina.com.cn/doc/python/storage.html)中的md文件，生成html，并显示到页面上。

###2.如果你还不熟悉sae
[新手入门](http://sae.sina.com.cn/doc/tutorial/index.html)

[SAE python入门指南](http://sae.sina.com.cn/doc/python/tutorial.html)

###3. Main Code

index.wsgi


    import os

    from bottle import Bottle, run, static_file
    # sae no include python markdown library, we need
    # put the marddown in root dir
    import markdown

    import sae
    from sae.storage import Bucket

    app = Bottle()
    app_root = os.path.dirname(__file__)

    # the bottle on sae is 0.9.6
    # the style of route is :argvs, not <argvs>
    @app.route('/css/:filename')
    def server_static(filename):
        return static_file(filename,
                        root=os.path.join(app_root, "css"),
                        mimetype='text/css')

    @app.route('/')
    def hello():
        head_html = """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="utf-8">
            <link type="text/css"
            rel="stylesheet"
            href="/css/mdstyle.css" />
        </head>
        <body>
        """
        tail_html = """
        </body>
        </html>
        """
        bkt = Bucket("blog")
        articles = []
        ## list all article in blog buc        ## list all article in blog buc    
            if i.name.endswith(".md"):
                art                art          s(i.name)
                article = markdown.markdown(article.decode("UTF-8"))                 articles.append(article)
        if len(articles) == 0:
            articles = ["No Article"]
        body_html = "<hr/>".join(articles)
        html = head_html + body_html + tail_html
        return html

    application = sae.create_wsgi_app(app)
    
    
    
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
