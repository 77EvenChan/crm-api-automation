from typing import Dict, Any
from crm_api.core.http_client import HTTPClient

class CustomerAPI:
	"""
	【Mock 接口文档契约 - 客户管理模块】
    ==================================================[接口1: 创建企业客户]
    1. 接口说明: 录入新的 B 端企业客户信息，进入公海池
    2. 请求方式: POST
    3. 请求路径: /customers
    4. 请求头: Authorization: Bearer <token>, Content-Type: application/json
    5. 请求参数:
       - customer_name (str): 企业名称, 必填 (例: "北京字节跳动科技有限公司")
       - contact_phone (str): 联系人电话, 必填
       - industry (str): 所属行业, 选填 (枚举: IT/金融/医疗/制造)
    6. 响应示例:
       {
           "code": 0,
           "msg": "created successfully",
           "data": {
               "customer_id": "CUST_8839201",
               "status": "INIT",
               "created_at": "2026-02-27T10:00:00Z"
           }
       }
    7. 错误码: 40001 (参数校验失败), 40900 (客户名称已存在)
    8. 业务说明: 创建成功后，状态默认为 INIT（初始态），必须要有合法的 Token 才能请求。
    ==================================================
    [接口2: 获取客户详情]
    1. 接口说明: 根据客户 ID 查询详细档案
    2. 请求方式: GET
    3. 请求路径: /customers/{customer_id}
    ...
	"""
	def __init__(self, client: HTTPClient) -> None:
		self.client = client
	
	def create_customer(self, customer_name: str, contact_phone: str, industry: str = "IT") -> Dict[str, Any]:
		"""
		业务动作：创建企业客户
		:return: 接口的完整反序列化字典，共测试层断言
		"""
		
		payload = {
			"customer_name": customer_name,
			"contact_phone": contact_phone,
			"industry": industry
		}
		
		# 将HTTP请求细节完全隐藏在这一层
		resp = self.client.request("POST", "/customers", json=payload)
		return resp.json()
	
	def get_customer(self, customer_id: str) -> Dict[str, Any]:
		"""业务动作：获取客户详情"""
		resp = self.client.request("GET", f"/customers/{customer_id}")
		return resp.json()
	
	def delete_customer(self, customer_id: str) -> Dict[str, Any]:
		"""业务动作：删除客户记录"""
		resp = self.client.request("DELETE", f"/customers/{customer_id}")
		return resp.json()
	