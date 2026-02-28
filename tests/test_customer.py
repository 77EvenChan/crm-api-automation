import pytest
import allure
import json
from pathlib import Path
from src.crm_api.core.http_client import http_client
from src.crm_api.api.customer_api import CustomerAPI
from src.crm_api.core.logger import log

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "customer_data.json"


def load_test_data():
	with open(DATA_FILE, "r", encoding="utf-8") as f:
		data = json.load(f)
	return [
		(d.get("customer_name"), d.get("contact_phone"), d.get("industry"),
		 d.get("expect_code"), d.get("expect_msg"), d.get("is_success"))
		for d in data
	]


def load_case_ids():
	with open(DATA_FILE, "r", encoding="utf-8") as f:
		return [str(d.get("case_id", "Unknown")) for d in json.load(f)]


@allure.epic("CRM 系统自动化测试")
@allure.feature("客户管理模块")
class TestCustomerManagement:
	
	def setup_method(self) -> None:
		self.customer_api = CustomerAPI(http_client)
	
	@allure.story("创建企业客户")
	@allure.title("数据驱动验证: {expect_msg}")
	@pytest.mark.parametrize(
		"customer_name, contact_phone, industry, expect_code, expect_msg, is_success",
		load_test_data(),
		ids=load_case_ids()
	)
	def test_create_customer_data_driven(
			self, customer_name, contact_phone, industry, expect_code, expect_msg, is_success
	) -> None:
		with allure.step("1. 组装测试数据并发起请求"):
			log.info(f"用例参数注入 -> 企业名称: {customer_name}")
			res = self.customer_api.create_customer(customer_name, contact_phone, industry)
		
		with allure.step(f"2. 校验业务响应码应为 {expect_code}"):
			assert res.get("code") == expect_code
			assert res.get("msg") == expect_msg
		
		with allure.step("3. 校验状态流转与数据落盘"):
			data_body = res.get("data")
			if is_success:
				assert data_body is not None
				assert str(data_body.get("customer_id")).startswith("CUST_")
				assert data_body.get("status") == "INIT"
			else:
				assert data_body is None
	
	@allure.story("查询与作废客户闭环")
	@allure.title("生命周期测试: 创建 -> 查询 -> 删除")
	def test_customer_lifecycle(self) -> None:
		with allure.step("1. 前置动作: 创建临时测试客户"):
			res_create = self.customer_api.create_customer("生命周期测试企业", "111", "IT")
			assert res_create.get("code") == 0
			cust_id = res_create.get("data", {}).get("customer_id")
		
		with allure.step(f"2. 核心动作: 查询详情 ({cust_id})"):
			res_get = self.customer_api.get_customer(cust_id)
			assert res_get.get("code") == 0
		
		with allure.step(f"3. 清理动作: 作废客户 ({cust_id})"):
			res_delete = self.customer_api.delete_customer(cust_id)
			assert res_delete.get("code") == 0