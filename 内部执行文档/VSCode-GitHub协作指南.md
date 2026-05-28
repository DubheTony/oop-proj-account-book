# VSCode GitHub 协作指南 — 个人财务管理系统

> 本文档指导五名组员使用 VSCode 的 GitHub 扩展完成代码协作，避免手动传文件。

---

## 一、前置准备（每人必做）

### 1.1 安装 Git

1. 下载：https://git-scm.com/download/win
2. 安装时一路默认即可（关键选项：选择 "Git from the command line and also from 3rd-party software"）
3. 安装完成后打开 VSCode 终端（Ctrl+`），验证：
   ```
   git --version
   ```
   应输出 `git version 2.xx.x`

### 1.2 配置 Git 用户信息

在 VSCode 终端中执行（替换为自己的信息）：
```
git config --global user.name "你的姓名"
git config --global user.email "你的GitHub注册邮箱"
```

### 1.3 安装 GitHub Pull Requests 扩展

1. VSCode 左侧点击扩展图标（Ctrl+Shift+X）
2. 搜索 `GitHub Pull Requests`
3. 安装由 **GitHub** 官方发布的那个（图标是 GitHub 猫头）
4. 安装后左侧会出现 GitHub 图标

### 1.4 登录 GitHub

1. 点击左侧 GitHub 图标
2. 点击 "Sign in to GitHub"
3. 浏览器会自动打开，授权 VSCode 访问你的 GitHub 账户
4. 授权完成后 VSCode 左侧会显示你的 GitHub 用户名

---

## 二、克隆仓库到本地（每人第一次做）

1. 打开 VSCode，按 `Ctrl+Shift+P`，输入 `Git: Clone`
2. 输入仓库地址（组长提供）：`https://github.com/xxx/oop2-finance-tracker.git`
3. 选择本地存放目录
4. 克隆完成后 VSCode 提示 "Would you like to open the cloned repository?" → 点 **Open**
5. 现在你本地就有了完整的项目文件

---

## 三、日常工作流程（每次写代码前必看）

### 核心理念：**一人一分支，完成合并**

```
main 分支 ← （只放稳定通过的代码）
  ├── feat/gui/A-realname       ← A 的分支
  ├── feat/integration/B-realname ← B 的分支
  ├── feat/models/C-realname    ← C 的分支
  ├── feat/diagnosis/D-realname ← D 的分支
  └── feat/budget/E-realname    ← E 的分支
```

### 3.1 每次开始工作前（拉取最新代码）

1. VSCode 左下角点击当前分支名（如 `feat/models/C-realname`）
2. 在弹出的菜单中选择 `main`
3. 再次点击左下角分支名 → 选择 `Pull`（或点击顶部菜单 ... → Pull）
4. 切回自己的分支：左下角点击分支名 → 选择自己的分支
5. 在自己的分支上，按 `Ctrl+Shift+P` → `Git: Merge Branch` → 选择 `origin/main`
   - 目的：把自己分支更新到 main 的最新状态
   - 如果有冲突（Conflict），VSCode 会标红冲突文件 → 见第五节

### 3.2 写代码 + 提交

写完一部分代码，确认没有语法错误后：

1. 左侧点击**源代码管理图标**（Ctrl+Shift+G，第三个图标，像一个分叉）
2. 你会看到 "Changes" 列表 —— 所有修改过的文件
3. **只暂存自己负责的文件**：鼠标悬停在文件上，点击 `+` 号（Stage Changes）
4. 在顶部的 Message 输入框中写提交信息，格式：
   ```
   feat: 完成Transaction和AccountType类
   ```
   或
   ```
   fix: 修复预警重复触发的问题
   ```
5. 点击 `✓ Commit` 按钮
6. 点击左下角 **同步更改** 按钮（或 `...` → `Push`），推送到 GitHub

### 3.3 发起 Pull Request（合并到 main）

当你完成一个功能模块，需要合并到 main 让其他人能用时：

1. 左侧点击 **GitHub 图标**
2. 在 "Pull Requests" 区域，鼠标悬停 → 点击 `+` 号（Create Pull Request）
3. 设置：
   - **Base**: `main`（合并到哪个分支）
   - **Compare**: 你的分支（从哪个分支合并）
   - **Title**: 简短描述（如 "C: 完成核心实体类和FinanceController骨架"）
   - **Description**: 列出改了什么文件、做了什么
4. 点击 **Create**
5. 告诉至少一个组员来 **Review**（审阅）
6. Review 通过后，点击 **Merge Pull Request** 合并
7. 合并后，**通知全组拉取最新 main**（见 3.1）

---

## 四、分工分支与文件责任表

| 组员 | 分支名（建议） | 负责目录 | 不可修改的目录 |
|---|---|---|---|
| **A** | `feat/gui/A-xxx` | `gui/` | `models/`, `strategies/`, `rules/`, `methods/`, `services/` |
| **B** | `feat/integration/B-xxx` | `services/csv_importer.py`, `services/category_normalizer.py`, `main_cli.py` | `strategies/`, `rules/`, `methods/`, `gui/` |
| **C** | `feat/models/C-xxx` | `models/transaction.py`, `models/budget.py`, `models/suggestion.py`, `services/finance_controller.py` | `strategies/`, `rules/`, `methods/`, `gui/` |
| **D** | `feat/diagnosis/D-xxx` | `models/diagnosis_report.py`, `strategies/` | `rules/`, `methods/`, `gui/` |
| **E** | `feat/budget/E-xxx` | `models/monthly_plan.py`, `models/savings_plan.py`, `services/saving_calculator.py`, `rules/`, `methods/` | `strategies/`, `gui/` |

> **红线规则**：不要修改不是你负责的目录下的文件。如果确实需要修改他人的文件（如接口签名调整），在 PR 描述中 @对方 来 Review。

---

## 五、处理冲突（Merge Conflict）

当你合并 main 到自己分支时，如果和你自己的修改冲突了：

### VSCode 冲突解决界面

1. 冲突文件会标记为 `!` 并显示在源代码管理面板
2. 打开冲突文件，VSCode 会用颜色标记冲突区域：
   ```
   <<<<<<< HEAD (你的修改)
   你的代码
   =======
   main 分支的代码
   >>>>>>> origin/main
   ```
3. 在每个冲突区域上方，会出现三个按钮：
   - **Accept Current Change**：保留你的修改
   - **Accept Incoming Change**：使用 main 的版本
   - **Accept Both Changes**：两个都保留
   - **Compare Changes**：左右对比查看
4. 逐一处理完所有冲突后，保存文件
5. 在源代码管理面板，点击 `+` 暂存该文件
6. Commit → Push

> **建议**：每天开始工作前先 Merge main，减少冲突积累。

---

## 六、常见问题

### Q1: "我没有权限推送"
**原因**：你是私有仓库，组长需要在 GitHub 上把你加为 Collaborator。
**解决**：组长去 `https://github.com/xxx/oop2-finance-tracker/settings/access` → Add people → 输入你的 GitHub 用户名 → 权限选 Write。

### Q2: 推送时显示 "rejected"
**原因**：你的分支落后于远程分支。
**解决**：先 Pull 再 Push。左下角点 `Pull`，然后再 `Push`。

### Q3: 不小心改了他人的文件
**解决**：在源代码管理面板，右键该文件 → Discard Changes。这会恢复为原来版本。

### Q4: 不知道自己的分支名
**查看**：VSCode 左下角显示的就是当前分支名。也可以在终端输入 `git branch`。

### Q5: Push 后 GitHub 上看不到变化
**原因**：可能只 Commit 了但没有 Push。
**解决**：检查左下角是否有 "Synchronize Changes" 按钮。点击它。

---

## 七、终端速查（可选，GUI 够用的话不需要）

| 操作 | 终端命令 |
|---|---|
| 克隆仓库 | `git clone https://github.com/xxx/oop2-finance-tracker.git` |
| 查看分支 | `git branch -a` |
| 切换分支 | `git checkout 分支名` |
| 拉取最新 | `git pull origin main` |
| 暂存所有修改 | `git add .` |
| 提交 | `git commit -m "feat: 描述"` |
| 推送 | `git push` |
| 合并 main 到当前分支 | `git merge origin/main` |
| 放弃本地修改 | `git checkout -- 文件名` |

---

## 八、每日检查清单

每个组员每天结束时：

- [ ] 今天的代码已经 Commit + Push 到自己的分支了吗？
- [ ] 有没有不小心提交了 `__pycache__/` 或 `.vscode/`？（.gitignore 已配置，一般不会）
- [ ] 有没有修改了不属于自己负责的目录下的文件？（检查 Changes 列表）
- [ ] 如果有完成的模块，发起 PR 了吗？通知 Review 了吗？
