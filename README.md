# yqg-git-ai

## 项目简介

yqg-git-ai 是一个开箱即用、支持 AI 智能交互的 Git 命令行助手，帮助团队自动化日常分支管理、cherry-pick、发布、代码审查等繁琐操作。你只需用自然语言输入需求，AI 会引导你一步步完成所有操作，大幅提升效率，支持 DeepSeek、OpenAI 等主流大模型。

---

## 功能特性
- 支持自然语言指令（如"我今天要发布代码"、"帮我review9d6f998f这个diff"）
- 自动检测最新 daily 分支，交互式创建新分支
- 智能 cherry-pick（pick-diff）：自动查找并选择性 cherry-pick 你在 master 上的提交
- 一键 arc diff 并自动 AI 代码审查
- review 任意 commit，结合 summary 和 diff 给出 AI 审查建议
- 分支变更摘要（pick-diff 后自动输出）
- 支持 Y/N 交互和分支命名
- AI/非AI双模式，命令参数与自然语言均可用
- 全局配置，无需每个项目单独配置

---

## 环境依赖
- Python 3.7+
- OpenAI 或 DeepSeek API Key
- 推荐使用 [pipx](https://github.com/pypa/pipx) 全局安装
- [uv](https://github.com/astral-sh/uv) 可用于开发/调试虚拟环境

---

## 🚀 Quick Start

### 1. 克隆项目
```bash
git clone https://github.com/yourname/yqg-git-ai.git
cd yqg-git-ai
```

### 2. 修改 config.json 里的 username
- 打开项目根目录下的 `config.json`，将 `"username"` 字段改为你自己的 GitLab 用户名（**必填**）。
  例如：
  ```json
  {
    "api_key": "sk-xxxxxx",
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-ai/DeepSeek-R1",
    "use_ai": false,
    "username": "cuichenglong"
  }
  ```

### 3. （可选）配置 AI Key 等参数
- 如果你暂时不需要 AI 相关功能，可以跳过此步，后续随时补充 config.json 即可。
- 只有在使用 AI 智能分流、代码审查等功能时才需要配置 API Key。
- 即使不配置 AI，依然可以使用所有快捷的命令行操作。
- 如需使用 AI 相关功能，请修改项目根目录下的 `config.json`，内容示例：
  ```json
  {
    "api_key": "sk-xxxxxx",
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-ai/DeepSeek-R1",
    "use_ai": true,
    "username": "你的 Git 用户名"
  }
  ```

### 4. 全局安装 CLI 工具
```bash
pipx install .
```

### 5. 验证安装成功
```bash
yqg-git
# 或
yqg-git --help
```
如果能看到详细的命令帮助和安全提示，说明安装成功！

---

## 🛠️ 常用命令与用法

| 命令                                 | 说明                                 | 支持自然语言/AI语义 |
|--------------------------------------|--------------------------------------|---------------------|
| `yqg-git daily-flow`                 | 自动拉取最新 daily 分支并创建新分支   | 是                  |
| `yqg-git pick-diff`                  | 智能 cherry-pick 你在 master 上的提交，支持 AI 语义 | 是                  |
| `yqg-git arc-diff`                   | 一键 arc diff 并自动 AI 代码审查      | 是                  |
| `yqg-git review-<hashid>`            | review 某个 commit diff，AI 审查建议  | 是                  |
| `yqg-git daily-msg`                  | （已集成到 pick-diff）输出分支变更摘要| 否                  |
| `yqg-git 我要发布代码`                | 支持自然语言，自动识别并执行 daily-flow | 是                  |
| `yqg-git 帮我review9d6f998f这个代码`  | 支持自然语言，自动识别并 review commit | 是                  |
| `yqg-git 我要pick diff`                | 支持自然语言，自动识别并执行 cherry-pick | 是                  |

---

## 🧠 AI 智能能力

- 支持 DeepSeek、OpenAI 等主流大模型
- AI 能力包括：自然语言理解、代码 diff 审查、commit 审查、自动分流命令
- 可在 config.json 里通过 `use_ai` 开关控制

---

## 卸载/删除全局命令

- **pipx 安装的卸载（推荐）**
  ```bash
  pipx uninstall yqg-git-ai
  ```
- **uv/pip 虚拟环境卸载**
  ```bash
  deactivate  # 退出虚拟环境
  rm -rf venv
  ```

---

## 常见问题

- **ModuleNotFoundError: No module named 'xxx'**
  > 说明依赖未安装，建议用 pipx 重新全局安装。
- **API Key 未设置**
  > 请参考上面"安装步骤"配置 config.json 或环境变量。
- **zsh: command not found: yqg-git**
  > 请确认已用 `pipx install .` 安装，或虚拟环境已激活。
  > pipx 会自动处理 PATH，无需手动配置。

---

## 贡献与扩展

欢迎 PR 和 issue，后续可扩展更多 AI 智能交互、自动化脚本、团队协作等功能。

---

如需更详细的使用说明、二次开发文档等，也可以联系作者或提 issue。

## 代码隐私注意事项

使用 AI 功能时，为保护代码隐私和安全，请避免发送以下内容：

- 密钥、证书等凭证信息
- 内部 API 接口细节和调用方式
- 数据库连接信息和配置
- 用户隐私数据
- 核心商业逻辑代码
- 内部系统架构细节
- 未公开的业务规则

建议：
- 仅发送必要的代码片段
- 使用示例数据替代真实数据
- 去除敏感的注释信息
- 定期检查和更新安全设置
- 关注 AI 服务商的隐私政策更新

## TODO

- [ ] 支持 周master 分支代码检测  
  - 提醒需要pick、revert的diff
- [ ] 支持更多自然语言指令
- [ ] 增强 AI 代码审查能力，支持多模型切换
- [ ] 提供更丰富的命令行交互体验
- [ ] 文档国际化（中英文）
- [ ] arc diff 后续支持 commit 内容和 summary 关联 review

> 说明：本工具不会自动强制 push，遇到冲突建议手动处理，确保代码安全和团队协作规范。