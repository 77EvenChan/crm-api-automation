import pytest
from typing import Generator

from src.crm_api.core.logger import log
from src.crm_api.core.http_client import HTTPClient, http_client
from src.crm_api.config.settings import settings
from src.crm_api.api.auth_api import AuthAPI

@pytest.fixture(scope="session", autouse=True)
def auto_auth_session() -> Generator[HTTPClient, None, None]:
	"""
	全局会话级前置夹具
	（1）整个测试会话启动前：自动登录并提取token，并瓜子啊到全局HTTP引擎
	（2）整个测试会话结束后自动清理Header
	"""
	log.info(f"【fixture启动】开始执行全局初始化")
	auth_api = AuthAPI(http_client)
	
	try:
		# 本地运行，因为Mock服务器还没设计，底层引擎会抛出异常，我们应始终遵循并行开发原则
		token = auth_api.login(settings.admin_username, settings.admin_password)
		
		# 将Token注入单例Session
		http_client.session.headers.update({"Authorization": f"Bearer {token}"})
		log.info("【fixture成功】全局token提取并注入Session成功")
	
	except Exception as e:
		log.error(f"【fixture阻断】全局鉴权失败，自动化测试终止：{e}")
		# 不中断，让yield传递，以便在没网时也能验证生命周期
	
	yield http_client
	
	log.info("【fixture销毁】测试会话结束，清理全局环境")
	http_client.session.headers.pop("Authorization", None)