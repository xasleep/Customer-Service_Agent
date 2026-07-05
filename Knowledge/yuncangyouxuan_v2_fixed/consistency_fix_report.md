# 云仓优选一致性修复报告

## 1. 修改文件列表
- eval/eval_cases.json
- fixtures/users.json
- fixtures/products.json
- fixtures/return_requests.json
- fixtures/risk_events.json

## 2. 每个文件的关键改动摘要

### eval/eval_cases.json
- 将 EC034、EC035、EC036 的 `expected_intent` 从 `order` 改为 `account`
- 保留上述 3 条用例的 `expected_tool: "user.query"`
- 为 EC041、EC042、EC044、EC045 增加 `case_type` 与 `risk_event_hint`
- 将 EC041、EC045 的 `should_mask_pii` 改为 `false`

### fixtures/users.json
- 为每个用户补充 `points_balance`
- 为每个用户补充 `coupons`
- 为每个用户补充 `restriction_reason`
- 为每个用户补充 `account_status`
- U001 增加可支持 EC034、EC035 的积分和退券数据
- U006 增加 `restricted` 状态与限制原因，可支持 EC036

### fixtures/risk_events.json
- 新增 4 条风险事件：
  - sms_code_request
  - full_address_request
  - impersonation_refund_scam
  - privacy_data_delete_request

### fixtures/products.json
- 为每个商品新增 `return_policy`
- 普通实物、耗材、智能门锁、会员权益分别按知识库规则结构化表达

### fixtures/return_requests.json
- 为每条记录新增 `product_id`
- 为每条记录新增 `decision_reason`
- `product_id` 全部由 `order_id -> orders.json.product_id` 映射得到

## 3. 自检结果

### JSON 合法性
{
  "orders.json": true,
  "products.json": true,
  "return_requests.json": true,
  "shipments.json": true,
  "tickets.json": true,
  "users.json": true,
  "risk_events.json": true,
  "eval_cases.json": true
}

### expected_source 是否存在
[]

### eval_cases 引用校验
[]

### risk_events 映射校验
{
  "EC041": true,
  "EC042": true,
  "EC044": true,
  "EC045": true
}

### 禁止词残留
[]

### 可能的真实敏感信息命中
[]

## 4. 仍无法修复的问题
- 未发现必须保留的未修复问题。
- 说明：本次按“只修复一致性和可测试性问题”执行，未重写知识库正文，也未更改企业名。
