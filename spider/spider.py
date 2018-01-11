import requests
from scrapy import Selector


# 进行数据抓取
class MySpider():
	def __init__(self, user=None, pwd=None):
		self.user = '18829890053'
		self.pwd = 'baixing0053'
		self.session = requests.session()
		self.headers = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Host': 'www.baixing.com',
			'Upgrade-Insecure-Requests': '1',
			'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
			                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}
		self.file = open('id.txt', 'w', encoding='utf-8')   # url 不多 所以放入txt文件中
	
	def get_post_params(self):
		# 获取post参数
		login_url = 'http://www.baixing.com/oz/login?'
		response_ = self.session.get(login_url, headers=self.headers)
		token_1 = Selector(response_).xpath('//*[@id="authform"]/input[1]/@value').extract_first()
		toekn_2_key = Selector(response_).xpath('//*[@id="authform"]/input[2]/@name').extract_first()
		token_2_value = Selector(response_).xpath('//*[@id="authform"]/input[2]/@value').extract_first()
		post_data = {
			"token" : token_1,
			toekn_2_key: token_2_value
		}
		cookies = response_.cookies.get_dict()
		return cookies, post_data
	
	def login(self):
		# 模拟登陆
		cookies, post_data = self.get_post_params()
		post_url = 'http://www.baixing.com/oz/login?'
		headers = self.headers
		headers['Origin'] = 'http://www.baixing.com'
		headers['Referer'] = 'http://www.baixing.com/oz/login?'
		post_data['identity'] = self.user
		post_data['password'] = self.pwd
		response_ = self.session.post(post_url, headers=headers, cookies=cookies, data=post_data)
		if response_.status_code == 200:
			print('登陆成功')
			return True
		else:
			return False
		
	def get_all_url(self):
		# 获取列表页所有的url
		zero_page_url = 'http://www.baixing.com/w/posts/myPosts/all?page=0'
		self.login()
		zero_page_response = self.session.get(zero_page_url, headers=self.headers)
		# 获取页码数
		page_num = Selector(zero_page_response).xpath('//ol[@class="page-nav"]/li[last()-1]/a/text()')
		if page_num:
			page_num = int(page_num.extract_first())
			print('请求第 -0- 页成功')
			self.file.write('请求 -0- 页成功\n')
		# 获取当前页面所有的url
		zero_id_list = Selector(zero_page_response).xpath('//*[@id="posts-ad-items"]/li/a/@href').extract()
		for id_ in zero_id_list:
			self.file.write(id_)
			self.file.write('\n')
		
		url_format = slice(0, -1)
		init_url = zero_page_url[url_format]
		for index in range(1, page_num):
			url_ = init_url + str(index)
			# 进行请求
			res = self.session.get(url_, headers=self.headers)
			# 解析url
			if res.status_code == 200:
				print('请求 -{}- 页成功'.format(index))
				id_list = Selector(res).xpath('//*[@id="posts-ad-items"]/li/a/@href').extract()
				# 写入文件
				self.file.write('请求 -{}- 页成功'.format(index))
				self.file.write('\n')
				for id_ in id_list:
					self.file.write(id_)
					self.file.write('\n')
			else:
				print('请求 -{}- 页失败'.format(index))
				self.file.write('请求 -{}- 页失败'.format(index))
				self.file.write('\n')
	
	


if __name__ == '__main__':
	spider = MySpider()
	spider.get_all_url()
