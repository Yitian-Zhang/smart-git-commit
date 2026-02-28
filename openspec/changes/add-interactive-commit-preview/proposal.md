# 变更：commit-message 提案

## 变更内容
### 项目名
Smart Git Commit，CLI 工具，用 LLM 自动生成 git commit message，支持 Semantic Git Commit Message 标准。

### 技术栈和规范
- Python 3.12+，用 UV 管包
- 必须用 Type Hint
- Public API 用 Google style docstring，英文注释
- 只需要支持 OpenAI 兼容的 Chat Completion API
- 测试覆盖率 > 70%

### 我的原则
- 全英文界面
- 开箱即用，最小化配置
- 融入现有 git 工作流，不打断用户
- 性能优先，降低模型的思考时间（Reasoning Effort），避免长时间等待
- 良好的 CLI 用户体验（loading、富有建设性建议的错误提示）
- 良好的 Github 开源项目风格的英文 README.md
- 良好的命令行工具说明和帮助

### 项目结构要求
- 代码放在 src/ 目录下
- 清晰的模块划分，每个功能独立成子模块
- 界面逻辑、LLM 相关的逻辑以及 Git 获取信息的逻辑应该实现分离
- 严谨的文件夹目录结构
- 职责单一，模块高内聚低耦合

### 目标
做一个好用的 CLI 工具，不做 GUI，不替代 git。
