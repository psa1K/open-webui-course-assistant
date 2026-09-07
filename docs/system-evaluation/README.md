# Issue #25 系统测试归档

本目录只归档由 `scripts/verify_system_evaluation.py` 生成的脱敏测试结果与审批材料。

- `baseline-results.json`：第一轮固定用例的真实运行结果。
- `optimization-proposal.md`：从基线结果自动整理的候选优化项；均为“等待用户批准”。
- `approved-optimizations.md`：用户逐项批准后才创建并记录批准范围。
- `optimized-results.json`：仅在批准优化并完成第二轮运行后生成。
- `before-after-comparison.md`：基线与优化后使用同一组测试用例的对比。

不要在本目录写入管理员密码、Bearer Token、API Key、`.env` 内容或本地数据库。测试输入在 [test-cases.json](../../configs/system-evaluation/test-cases.json) 固定；基线完成后若需修改用例，必须单独说明原因，不能通过改题掩盖问题。
