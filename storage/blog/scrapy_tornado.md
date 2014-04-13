![image](http://www.tornadoweb.org/en/stable/_images/tornado.png)

###如何安装
	pip install tornado

###Hello, world

	import tornado.ioloop
	import tornado.web

	class MainHandler(tornado.web.RequestHandler):
		def get(self):
			self.write("Hello, world")

	application = tornado.web.Application([
	    (r"/", MainHandler),
	])
	
	if __name__ == "__main__":
	    application.listen(8888)
	    tornado.ioloop.IOLoop.instance().start()
	    
### 更复杂的例子
#### url router

	class MainHandler(tornado.web.RequestHandler):
    	def get(self):
        	self.write("You requested the main page")

	class StoryHandler(tornado.web.RequestHandler):
    	def get(self, story_id):
        	self.write("You requested the story " + story_id)

	application = tornado.web.Application([
    	(r"/", MainHandler),
    	(r"/story/([0-9]+)", StoryHandler),
	])
通过正则来匹配请求url，映射到Handler类，来处理请求


#### Templates
temp.html:

	<html>
	<head>
      <title>{{ title }}</title>
     </head>
     <body>
     <ul>
       {% for item in items %}
         <li>{{ escape(item) }}</li>
       {% end %}
     </ul>
     </body>
     </html>
     
handler.py

	class MainHandler(tornado.web.RequestHandler):
    	def get(self):
        	items = ["Item 1", "Item 2", "Item 3"]
        	self.render("template.html", title="My title", items=items)


#### 配置

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/a/message/new", MessageNewHandler),
            (r"/a/message/updates", MessageUpdatesHandler),
            ],
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url="/auth/login",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        )
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()


[更多参考实例：https://github.com/facebook/tornado/demo](https://github.com/facebook/tornado/demo)


[参考文档1：http://www.tornadoweb.org/en/stable/overview.html](http://www.tornadoweb.org/en/stable/overview.html)




![image](http://scrapy.org/site-media/images/logo.png)

###如何安装
	apt-get install scrapy
	yum install scrapy
	pip install scrapy ##升级到最新版本
	
###如何使用
####第一步
安装完scrapy之后，可以使用`scrapy`命令
执行命令：

	scrapy startproject <project-name>
scrapy会自动帮忙建立一个scrapy项目目录，包括一些基本必须的文件。

结构如下：

	<project-name>/  #项目名称
    	scrapy.cfg
    	<project-name>/ #项目名称
        	__init__.py
        	items.py    #用来定义Items的模块
        	pipelines.py #用来定义piplines class实现的模块
        	settings.py  #用来设置配置的文件
        	spiders/    #存放各个Spider实现的目录
            	__init__.py
            	...
当在spider目录下，按正确方式实现了一个自己的spider模块之后，
可以进入最上层的<project-name>目录，
执行:

	scrapy crawl <spider-name>
就可以运行实现的Spiler。注：`spider-name`为Splider模块中设置。
具体如下：

####Spider
说明：
Spiler作用：根据给定的url作为入口，
请求页面，然后处理页面内容。


处理方式：Selector


	from scrapy.selector import Selector
	from scrapy.spider import Spider
	from scrapy.http import Request
	from myproject.items import MyItem

	class MySpider(Spider):
		name = 'example.com'
    	allowed_domains = ['example.com']
    	start_urls = [
        	'http://www.example.com/1.html',
        	'http://www.example.com/2.html',
        	'http://www.example.com/3.html',
    	]

    	def parse(self, response):
        	sel = Selector(response)
        	for h3 in sel.xpath('//h3').extract():
            	yield MyItem(title=h3)

        	for url in sel.xpath('//a/@href').extract():
            	yield Request(url, callback=self.parse)


####Selector
说明：`sel.css`作为css样式的选择器使用。

可以使用命里`scrapy shell <url>`, 进入console模式，进行网页元素选择测试

	    def parse(self, response):

        	sel = Selector(response)
        	url = response.url
        	if url.endswith("/"):
             	url = url[:-1]
        	if url not in self.title:
            	self.title[url] = sel.css("#maininfo #info h1::text").extract()[0]
            	
        	chapters = sel.css(".box_con dd a::attr(href)").extract()
        	for chapter in chapters:
            	chapter = self.base_url + chapter
            	print chapter
            	yield Request(chapter, callback=self.chap_callback)
            	

####Item
说明：用来存储数据的实体对象类：

	from scrapy.item import Item, Field

	class Product(Item):
    	name = Field()
    	price = Field()
    	stock = Field()
    	last_updated = Field(serializer=str)
GET字段：

	>>> product['name']
	Desktop PC
	>>> product.get('name')
	Desktop PC
	>>> product.get('last_updated', 'not set')
	not set
	>>> 'last_updated' in product.fields  # is last_updated a declared field?
	True
	>>> 'lala' in product.fields  # is lala a declared field?
	False
	
SET字段：

	>>> product['last_updated'] = 'today'
	>>> product['last_updated']
	today

	>>> product['lala'] = 'test' # setting unknown field
	Traceback (most recent call last):
    	...
	KeyError: 'Product does not support field: lala'

####pipeline
说明：用来处理Spidler返回的Item。

	import json

	class JsonWriterPipeline(object):

    	def __init__(self):
        	self.file = open('items.jl', 'wb')

    	def process_item(self, item, spider):
        	line = json.dumps(dict(item)) + "\n"
        	self.file.write(line)
        	return item

设置PIPline：
说明：在settings.py中设置使用哪些Pipline class来处理Item，后面的数字表示
优先级，The lower the better

	ITEM_PIPELINES = {
    'myproject.pipeline.PricePipeline': 300,
    'myproject.pipeline.JsonWriterPipeline': 800,
	}
	
[参考2：http://doc.scrapy.org/en/latest/intro/tutorial.html](http://doc.scrapy.org/en/latest/intro/tutorial.html)



