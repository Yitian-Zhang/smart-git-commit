# 项目 上下文

## 目的
Smart Git Commit 是一个 CLI 工具：读取当前 Git 仓库的变更上下文（如 staged diff、分支信息等），调用 LLM 自动生成高质量的 git commit message，并与现有 git 工作流无缝集成。默认遵循 Semantic / Conventional Commit 风格的提交信息格式（如 `type(scope): subject`）。

## 技术栈
- Python 3.12+
- uv 作为包管理与运行工具链
- 仅需支持 OpenAI 兼容的 Chat Completions API

## 项目约定

### 代码风格
- 必须使用类型标注（Type Hint），并通过静态检查
- Public API 必须使用 Google 风格 docstring
- 代码注释使用英文
- CLI 交互界面全英文

### 架构模式
- 代码放在 `src/` 目录下
- 以清晰的子模块划分职责：CLI/交互、LLM 调用、Git 信息获取必须相互隔离
- 模块单一职责，高内聚低耦合，目录结构严谨可扩展

### 测试策略
- 自动化测试覆盖率目标：> 70%
- 优先为关键路径添加测试：Git 信息采集、Prompt 构造、模型输出解析与校验、CLI 行为

### Git工作流
- 不替代 git，只在现有工作流中增量增强提交信息生成
- 提交信息目标格式：Semantic / Conventional Commit（例如 `feat: ...`，`fix(scope): ...`）

## 领域上下文
- 输入：Git 变更上下文（如 `git diff --staged`），以及可选的仓库元信息
- 输出：单行或多行 commit message（subject/body），要求可直接用于 `git commit -m` 或编辑器填充
- 关注点：减少无效等待、减少不必要的模型思考（Reasoning Effort），在保证质量的前提下优先性能
- 用户体验：清晰的 loading 状态、可操作的错误提示与改进建议

## 重要约束
- 开箱即用，最小化配置；默认行为应对大多数仓库有效
- 性能优先：避免长时间等待，必要时提供降级策略（如更短上下文、较小模型）
- 不做 GUI，不替代 git

## 外部依赖
- OpenAI 兼容的 Chat Completions 服务端点（具体提供方可由用户配置）
