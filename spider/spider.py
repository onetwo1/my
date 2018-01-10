import requests
from scrapy import Selector


# 进行数据抓取
class MySpider:
	def __init__(self, user, pwd):
		self.user = '18829890053'
		self.pwd = 'baixing0053'
	
	def get_post_params(self):
		# 获取post参数
		login_url = 'http://www.baixing.com/oz/login?'
		response_ = requests.get(login_url, headers='')
		
	
	def login(self):
		# 模拟登陆
		pass
	
	def download(self):
		# 下载文件
		pass