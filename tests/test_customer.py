import pytest
from src.crm_api.core.http_client import http_client
from src.crm_api.api.customer_api import CustomerAPI
from src.crm_api.core.logger import log

class TestCustomerManagement:
	"""业务测试类：CRM - 客户管理模块核心流程验证"""
	def setup_method(self) -> None:
		"""每个测试方法前初始化API对象"""
		self.customer_api = CustomerAPI(http_client)
		log.info("开始执行客户管理业务用例")
		
	@pytest.mark.parametrize(
		"customer_name, contact_phone, industry, expect_code, expect_msg, is_success",[
			# 用例1：正向路径 - 正常创建企业客户
			("北京字节跳动科技有限公司", "13800138000", "IT", 0, "创建成功", True),
			# 用例2：逆向路径 -客户名称重复冲突验证
			("重复企业有限公司","13900139000", "金融", 40900, "企业已存在", False),
		],
		ids=["创建成功","创建失败"]
	)
	def test_create_customer_data_driver(self, customer_name: str, contact_phone: str, industry: str, expect_code: int, expect_msg: str, is_success: bool) -> None:
		"""数据驱动测试：验证创建客户接口的正向与逆向业务逻辑"""
		log.info(f"用例参数注入 -> 企业名称：{customer_name}, 行业：{industry}")
		
		# 发起业务调用
		resp = self.customer_api.create_customer(
			customer_name=customer_name,
			contact_phone=contact_phone,
			industry=industry
		)
		
		# 多重业务断言
		assert resp['code'] == expect_code, f"业务响应码错误：期望{expect_code}，实际{resp['code']}"
		assert resp['msg'] == expect_msg, f"业务提示信息不匹配：实际为{resp['msg']}"
		
		# 核心流转字段断言
		if is_success:
			assert resp['data']['customer_id'].startswith("CUST_"), "客户ID生成规则校验失败"
			assert resp['data']['status'] == "INIT", "新创建的客户状态必须为INIT"
			log.info(f"断言通过：成功创建客户，ID为{resp['data']['customer_id']}")
		
		else:
			assert resp['data'] is None, "异常流转时，data字段必须为空以防数据泄露"
			log.info("断言通过：系统正确拦截了重复创建请求")