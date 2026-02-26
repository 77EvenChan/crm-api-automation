import json
from typing import Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from crm_api.config.settings import settings
from crm_api.core.logger import log
from crm_api.core.exceptions import APIRequestError

class HTTPClient:
	"""
	HTTP 客户端封装
	- Session 连接池复用
	- 失败自动重试机制
	- 统一请求/响应日志拦截
	"""
	
	def __init__(self) -> None:
		self.session = requests.Session()
		
		# 挂载重试策略（解决测试环境网络抖动造成的偶发性失败）
		retry_strategy = Retry(
			total=3,    # 最大重试次数
			backoff_factor=1,   # 重试间隔时间
			status_forcelist=[429,500,502,503,504],     # 遇到这些状态码自动重试
			allowed_methods=["HEAD","GET","OPTIONS","POST","PUT","DELETE"]
		)
		
		# 配置连接池大小
		adapter = HTTPAdapter(
			max_retries=retry_strategy,
			pool_connections=20,
			pool_maxsize=20
		)
		
		self.session.mount("http://", adapter)
		self.session.mount("https://", adapter)
	
	def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
		"""
		🙆‍统一请求入口
		:param method :     请求方法
		:param path:    接口路径
		:param kwargs:      其他参数
		:return:  requests.Response对象
		"""
		
		url = f"{settings.base_url}{path}"
		kwargs.setdefault("timeout", settings.timeout)
		
		# 拦截并格式化请求日志
		log.info(f"请求发起：{method.upper()} {path}")
		log.info(f"请求地址：{url}")
		if "params" in kwargs:
			log.info(f"请求参数：{kwargs['params']}")
		if "json" in kwargs:
			log.info(f"请求数据（JSON）：{kwargs['json']}")
		if "data" in kwargs:
			log.info(f"请求数据（Form）：{kwargs['data']}")
		
		# 发起请求并捕获异常
		try:
			resp = self.session.request(method, url, **kwargs)
		except requests.RequestException as e:
			error_msg = f"接口请求失败：{method.upper()}{url} ->{str(e)}"
			log.error(error_msg)
			# 抛出框架自定义异常
			raise APIRequestError(error_msg) from e
		
		# 拦截并格式化响应日志
		log.info(f"响应状态码：{resp.status_code} | 耗时：{resp.elapsed.total_seconds():.3f}s")
		try:
			# 尝试以JSON输出
			resp_data = resp.json()
			log.info(f"响应数据：{json.dumps(resp_data, ensure_ascii=False)}")
		except ValueError:
			# 如果不是Json 直接输出文本
			log.info(f"响应数据：{resp.text[::50]}")
		
		log.info("请求结束！")
		
		return resp
	
# 全局单例实例化
http_client = HTTPClient()