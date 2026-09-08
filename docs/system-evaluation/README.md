# Issue #25 系统测试归档

本目录只归档由 `scripts/verify_system_evaluation.py` 生成的脱敏测试结果与审批材料。

- `baseline-results.json`：第一轮固定用例的真实运行结果。
- `optimization-proposal.md`：从基线结果自动整理的候选优化项；均为“等待用户批准”。
- `approved-optimizations.md`：用户逐项批准后创建，记录每项批准范围、实施文件、风险、回滚方法与真实验收。
- `optimized-results.json`：批准优化后的第二轮真实运行结果。
- `before-after-comparison.md`：基线与优化后使用同一组测试用例的对比。

不要在本目录写入管理员密码、Bearer Token、API Key、`.env` 内容或本地数据库。测试输入在 [test-cases.json](../../configs/system-evaluation/test-cases.json) 固定；基线完成后若需修改用例，必须单独说明原因，不能通过改题掩盖问题。

当前进度（2026-09-08）：第一轮真实基线结果、OPT-A～OPT-E 的用户批准和实施记录、第二轮真实结果以及前后对比均已归档。两轮固定 15 项用例的通过数由 0 项提升至 10 项；5 个未通过用例及其后续建议在 `before-after-comparison.md` 中如实保留。
