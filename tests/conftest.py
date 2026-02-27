import pytest
from typing import Generator
import requests_mock

from src.crm_api.core.logger import log
from src.crm_api.core.http_client import HTTPClient, http_client
from src.crm_api.config.settings import settings
from src.crm_api.api.auth_api import AuthAPI

@pytest.fixture(scope="session", autouse=True)
def global_mock_server() -> Generator[None, None, None]:
	"""【拦截器优先启动】确保在所有网络请求前就绪"""
	log.info("【Mock启动】拦截器已挂载，开启无后端测试模式")
	
	with requests_mock.Mocker() as m:
		# 登录接口
		m.post(f"{settings.base_url}/auth/login", json={"code": 0, "msg": "success", "data": {"token": "EvenChan_mock_token_77"}})
	
		# 客户管理 - 正向成功
		def match_success(request):
			try:
				# 将拦截到的底层报文还原成字典，精准读取字段
				return request.json().get("customer_name") == "北京字节跳动科技有限公司"
			except Exception:
				return False
		
		m.post(
			f"{settings.base_url}/customers",
			json={"code": 0, "msg": "创建成功", "data": {"customer_id": "CUST_8839201", "status": "INIT"}},
			additional_matcher=match_success
		)
		
		# 客户管理 - 逆向重复
		def match_duplicate(request):
			try:
				return request.json().get("customer_name") == "重复企业有限公司"
			except Exception:
				return False
		
		m.post(
			f"{settings.base_url}/customers",
			json={"code": 40900, "msg": "企业已存在", "data": None},
			additional_matcher=match_duplicate
		)
		
		yield

@pytest.fixture(scope="session", autouse=True)
def auto_auth_session(global_mock_server) -> Generator[HTTPClient, None, None]:
	"""全局鉴权：依赖Mock启动后再发请求"""
	log.info("【Fixture启动】开始提取全局Token")
	auth_api = AuthAPI(http_client)
	
	try:
		token = auth_api.login(settings.admin_username, settings.admin_password)
		http_client.session.headers.update({"Authorization": f"Bearer {token}"})
		log.info("【Fixture 成功】全局 Token 注入 Session 成功")
	except Exception as e:
		log.error(f"【Fixture 阻断】鉴权失败: {e}")
	
	yield http_client
	
	log.info("【Fixture销毁】测试会话结束")
	http_client.session.headers.pop("Authorization", None)