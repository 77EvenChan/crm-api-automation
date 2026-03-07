import pytest
from typing import Generator
import requests_mock

from src.crm_api.core.logger import log
from src.crm_api.core.http_client import HTTPClient, http_client
from src.crm_api.config.settings import settings
from src.crm_api.api.auth_api import AuthAPI


@pytest.fixture(scope="session", autouse=True)
def global_mock_server() -> Generator[None, None, None]:
	# 【开关】：如果配置里关闭了Mock，直接放行将真是请求转成公网
	if not settings.enable_mock:
		log.info("【环境切换】Mock拦截器已关闭，当前为真实后端模式！")
		yield
		return # 直接退出
	log.info("【Mock 启动】拦截器已挂载，开启无后端测试模式")
	
	with requests_mock.Mocker() as m:
		# Mock 1: 登录鉴权
		m.post(
			f"{settings.base_url}/auth/login",
			json={"code": 0, "msg": "成功", "data": {"token": "ey_mock_token_8899"}}
		)
		
		# 【工业级最高防御版】Mock 2: 创建成功
		def match_success(request):
			try:
				body = request.json() or {}
				# 强转为字符串！哪怕取到了 None 也会变成 "None"，绝对不会触发 not iterable 报错！
				name = str(body.get("customer_name", ""))
				return "字节跳动" in name or "生命周期" in name
			except Exception:
				return False
		
		m.post(
			f"{settings.base_url}/customers",
			json={"code": 0, "msg": "创建成功", "data": {"customer_id": "CUST_8839201", "status": "INIT"}},
			additional_matcher=match_success
		)
		
		# 【工业级最高防御版】Mock 3: 创建失败
		def match_duplicate(request):
			try:
				body = request.json() or {}
				# 同理，强转为字符串，消灭一切隐患
				name = str(body.get("customer_name", ""))
				return "重复企业" in name
			except Exception:
				return False
		
		m.post(
			f"{settings.base_url}/customers",
			json={"code": 40900, "msg": "企业已存在", "data": None},
			additional_matcher=match_duplicate
		)
		
		# Mock 4: 查询客户详情 GET
		m.get(
			f"{settings.base_url}/customers/CUST_8839201",
			json={"code": 0, "msg": "成功",
			      "data": {"customer_id": "CUST_8839201", "customer_name": "生命周期测试企业"}}
		)
		
		# Mock 5: 删除客户 DELETE
		m.delete(
			f"{settings.base_url}/customers/CUST_8839201",
			json={"code": 0, "msg": "删除成功"}
		)
		
		yield


@pytest.fixture(scope="session", autouse=True)
def auto_auth_session(global_mock_server) -> Generator[HTTPClient, None, None]:
	log.info("【Fixture 启动】开始提取全局 Token")
	auth_api = AuthAPI(http_client)
	try:
		token = auth_api.login(settings.admin_username, settings.admin_password)
		http_client.session.headers.update({"Authorization": f"Bearer {token}"})
		log.info("【Fixture 成功】全局 Token 注入 Session 成功")
	except Exception as e:
		log.error(f"【Fixture 阻断】鉴权失败: {e}")
	
	yield http_client
	http_client.session.headers.pop("Authorization", None)