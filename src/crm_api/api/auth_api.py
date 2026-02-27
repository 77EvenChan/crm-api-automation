from crm_api.core.http_client import HTTPClient

class AuthAPI:
	"""
	【Mock 接口文档契约 - 认证模块】
    1. 接口说明: 管理员登录并获取 JWT Token
    2. 请求方式: POST
    3. 请求路径: /auth/login
    4. 请求头: Content-Type: application/json
    5. 请求参数:
       - username (str): 用户名, 必填
       - password (str): 密码, 必填
    6. 响应示例: {"code": 0, "msg": "success", "data": {"token": "ey...xxx"}}
    7. 错误码: 40100 (密码错误), 40400 (用户不存在)
    8. 业务说明: Token 有效期 2 小时，请求业务接口必须挂载于 Header 的 Authorization 字段。
	"""
	def __init__(self, client: HTTPClient) -> None:
		self.client = client
	
	def login(self, username: str,password: str) -> str:
		"""执行业务登录动作，提取并返回token"""
		payload = {
			"username": username,
			"password": password
		}
		
		# 发起网络请求
		resp = self.client.request("POST", "/auth/login", json=payload)
		
		resp_data = resp.json()
		
		# 底层业务级阻断：如果鉴权失败则抛出异常，避免用例层断言时出现错误
		if resp_data.get("code") != 0:
			raise ValueError(f"系统级异常：管理员登录失败，响应数据是：{resp_data}")
		
		return resp_data['data']['token']