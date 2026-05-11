# 测试数据说明

## 文件列表

| 文件 | 样本量 | 用途 |
|------|--------|------|
| test_set_100.csv | 100条 | 主测试集，覆盖17个品类，用于有效分类率和铁律拦截率测试 |
| test_set_200.csv | 200条 | 扩展测试集，用于规则引擎准确率验证 |
| test_set_300.csv | 300条 | 完整测试集，用于规则引擎优先级准确率（75.1%）测试 |

## CSV格式

所有文件使用逗号分隔、UTF-8编码，首行为列名：

| 列名 | 说明 | 示例 |
|------|------|------|
| feedback | 用户反馈原文 | "APP打开白屏等了30秒才出来" |
| category | 品类 | 外卖、电商、出行... |
| expected_sentiment | 期望情绪 | 负向/中性/正向 |
| expected_type | 期望问题类型 | 功能/性能/体验/内容 |
| expected_priority | 期望优先级 | 高/中/低 |

## 样本分布

100条主测试集覆盖17个品类，以外卖、电商、出行、社交、游戏、金融为主。部分品类样本偏少（如医疗仅2条），后续版本需补充。

## 测试脚本

```bash
cd scripts
pip install -r requirements.txt
set DIFY_API_KEY=app-xxxx
python batch_test.py
```
