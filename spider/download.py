import requests
import MySQLdb
from threading import Thread
from queue import Queue
from scrapy import Selector


# 生产者 and 消费者队列模式

# 存取产品的队列(缓冲区)
My_Queue = Queue()
# 存储url的集合
Url_Set = set()
# 存储res的队列
Res_Queue = Queue()
# 存储data的队列
Data_Queue = Queue()


# 放入url的类
class Producer(Thread):
	def __init__(self):
		super(Producer, self).__init__()
	
	def run(self):
		"""任务函数 -将url放入队列- """
		while True:
			# 如果队列没有满
			if My_Queue.not_full():
				# 从集合中取出一个url放入队列中
				My_Queue.put(Url_Set.pop())

# 消费url的类
class Consumer(Thread):
	def __init__(self):
		super(Consumer, self).__init__()
	
	# 下载数据 - 接收参数url
	def download_task(self, url):
		res = requests.get(url=url)
		return res
	
	def run(self):
		"""任务函数 -消耗url- """
		while True:
			# 如果队列不为空
			if My_Queue.not_empty():
				# 从队列中取出一个url执行下载任务
				url = My_Queue.get()
				res = self.download_task(url)
				# 返回的响应放入一个队列中
				Res_Queue.put(res)
				
# 解析res的类
class Parser(Thread):
	def __init__(self):
		super(Parser, self).__init__()
	
	# 解析数据 - 接受参数res
	def parse_task(self, res):
		selector_res = Selector(res)
		url = res.request.url
		title = selector_res.xpath('//div[@class="viewad-title"]/h1/text()').extract_first()
		price = selector_res.xpath('//div[@class="viewad-actions"]/span[@class="price"]/text()').extract_first().strip()
		publish_date = selector_res.xpath('//div[@class="viewad-actions"]/span[2]/text()').extract_first()
		h_publish_date = selector_res.xpath('//div[@class="viewad-actions"]/span[2]/@data-original-title').extract_first()
		varieties = selector_res.xpath('//div[@class="top-meta clearfix"]/li[1]/a/text()').extract_first()
		gender = selector_res.xpath('//div[@class="top-meta clearfix"]/li[2]/span[2]/text()').extract_first()
		age = selector_res.xpath('//div[@class="top-meta clearfix"]/li[3]/span[2]/text()').extract_first()
		publisher_id = selector_res.xpath('//span[@class="meta-posterType"]/text()').extract_first()
		supply_and_demand = selector_res.xpath('//span[@class="meta-供求"]/text()').extract_first()
		address = selector_res.xpath('//span[@class="meta-address"]/a/text()').extract_first()
		phone_1 = selector_res.xpath('//a[@class="contact-no"]/text()').extract_first()
		phone_2 = selector_res.xpath('//a[@class="show-contact"]/@data-contact').extract_first()
		phone = phone_1.replace('*', '') + phone_2
		weChat = ''
		ancestry = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[1]/label[2]/text()').extract_first()
		vaccine = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[3]/label[2]/text()').extract_first()
		insect = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[4]/label[2]/text()').extract_first()
		sale_number = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[5]/label[2]/text()').extract_first()
		trading_place = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[6]/label[2]/text()').extract_first()
		desc = selector_res.xpath('//div[@class="viewad-text-hide"]/text()').extract()
		picture_flag = selector_res.xpath('//div[@class="featured-height"]')
		if picture_flag:
			photo_item = picture_flag.xpath('div/a/@style').extract()
		else:
			picture_url = ''
		video_flag = selector_res.xpath('//source[@type="video/mp4"]')
		if video_flag:
			video_url = video_flag[0].xpath('@src').extract_first(default='')
		pass

	def run(self):
		"""任务函数 -消耗res- """
		while True:
			if Res_Queue.not_empty():
				# 从队列中取出一个res进行解析
				res = Res_Queue.get()
				data = self.parse_task(res)
				# 放入data队列
				Data_Queue.put(data)




if __name__ == '__main__':
	
	# 从文本中取出url - 放入set集合中
	with open('id.txt', 'r', encoding='utf-8') as f:
		for line in f.readlines():
			if '请求' in line:
				continue
			else:
				Url_Set.add(line)
	sc = Consumer()
	sp = Parser()
	res = sc.download_task('http://ezhou.baixing.com/chongwujiaoyi/a1253977347.html')
	sp.parse_task(res)


	