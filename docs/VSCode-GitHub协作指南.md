# VSCode GitHub 协作指南 — 个人财务管理系统

---

## 一、前置准备

见最后的deepseek对话

## 二、克隆仓库到本地（不确定这一段是否正确，没有检验过）

1. 打开 VSCode，按 `Ctrl+Shift+P`，输入 `Git: Clone`
2. 输入仓库地址（组长提供）：`https://github.com/xxx/oop2-finance-tracker.git`
3. 选择本地存放目录
4. 克隆完成后 VSCode 提示 "Would you like to open the cloned repository?" → 点 **Open**
5. 现在你本地就有了完整的项目文件

---

## 三、日常工作流程（每次写代码前必看）

### 核心理念：**一人一分支，完成合并**

```
master 分支 ← （只放稳定通过的代码）
  ├── feat/gui/A-realname       ← A 的分支
  ├── feat/integration/B-realname ← B 的分支
  ├── feat/models/C-realname    ← C 的分支
  ├── feat/diagnosis/D-realname ← D 的分支
  └── feat/budget/E-realname    ← E 的分支
```

### 3.1 每次开始工作前（拉取最新代码）

1. VSCode 左下角点击当前分支名（如 `feat/models/C-realname`）
2. 在弹出的菜单中选择 `master`
3. 点击**源代码管理图标**（Ctrl+Shift+G，第三个图标，像一个分叉）→ 选择 存储库 - 三个点 - 拉取
4. 切回自己的分支：左下角点击分支名 → 选择自己的分支
5. 点击**源代码管理图标**（Ctrl+Shift+G，第三个图标，像一个分叉）→ 选择 存储库 - 三个点 - 分支 - 合并 → 选择 `origin/master`
   - 目的：把自己分支更新到 master 的最新状态
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
5. 点击 `✓ 提交` 按钮

在源代码管理面板（Ctrl+Shift+G）中：

1. 点击面板右上角的“...”图标（更多操作）
2. 从弹出的菜单中选择“推送” 
   (有时显示为“Push”)
3. 等待右下角提示“推送完成”

### 3.3 发起 Pull Request（合并到 master 分支）

当你完成一个功能模块，需要合并到 master 让其他人能用时：

1. 左侧点击 **GitHub 图标**
2. 在 "Pull Requests" 区域，鼠标悬停 → 点击一个 带`+` 号的符号
3. 设置：
   - **Base**: `master`（合并到哪个分支）
   - **Compare**: 你的分支（从哪个分支合并）
   - **Title**: 简短描述（如 "C: 完成核心实体类和FinanceController骨架"）
   - **Description**: 列出改了什么文件、做了什么
4. 点击 **Create**
5. 告诉至少一个组员来 **Review**（审阅）
6. Review 通过后，点击 **Merge Pull Request** 合并
7. 合并后，**通知全组拉取最新 master**（见 3.1）

---


> 不要修改不是你负责的目录下的文件。
---

## 五、处理冲突（后面都没有看过）

当你合并 master 到自己分支时，如果和你自己的修改冲突了：

### VSCode 冲突解决界面

1. 冲突文件会标记为 `!` 并显示在源代码管理面板
2. 打开冲突文件，VSCode 会用颜色标记冲突区域：
   ```
   <<<<<<< HEAD (你的修改)
   你的代码
   =======
   master 分支的代码
   >>>>>>> origin/master
   ```
3. 在每个冲突区域上方，会出现三个按钮：
   - **Accept Current Change**：保留你的修改
   - **Accept Incoming Change**：使用 master 的版本
   - **Accept Both Changes**：两个都保留
   - **Compare Changes**：左右对比查看
4. 逐一处理完所有冲突后，保存文件
5. 在源代码管理面板，点击 `+` 暂存该文件
6. Commit → Push

> **建议**：每天开始工作前先 Merge master，减少冲突积累。

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


## deepseek对话

在 VS Code 里同步 GitHub 项目，本质就是使用 Git 版本控制。别担心，VSCode 把常用的 Git 命令都做成了图形界面，操作起来非常直观。

无论你是 **想把 GitHub 上的项目下载到本地**，还是 **想把自己电脑里的代码上传到 GitHub**，都可以按照下面的步骤来操作。

### 准备工作：打好基础

在开始前，请确保你的电脑上已经安装了这两个必要的软件：

1.  **Git**：这是一个版本管理工具，是同步的基础。
    *   **下载安装**：访问 [Git 官网](https://git-scm.com/downloads)，下载并安装适合你操作系统的版本。
2.  **Visual Studio Code (VS Code)**：我们的主力编辑器。
    *   **下载安装**：访问 [VS Code 官网](https://code.visualstudio.com/)，下载安装。

> 一个小提示：如果你是先装的 VS Code，后装的 Git，**安装完 Git 后，记得重启一下 VS Code**，这样 VS Code 才能识别到 Git 环境。

### 同步策略 (一)：将 GitHub 项目下载到本地 (Clone)

如果你的目标是参与一个已有的 GitHub 项目，或者把它下载到自己的电脑上学习，最直接的方法就是**克隆 (Clone)**。

1.  **复制仓库地址**：在 GitHub 项目页，点击绿色的 **"Code"** 按钮，然后复制仓库的 URL（HTTPS 或 SSH 均可）。

2.  **在 VS Code 中克隆**：
    *   打开 VS Code，点击左侧活动栏的 **"源代码管理"** 图标（或按 `Ctrl+Shift+G`）。
    *   点击该面板顶部的 **"克隆存储库"** 按钮。
    *   在弹出的输入框中**粘贴**你刚刚复制的 GitHub 仓库地址。

3.  **选择本地路径并打开**：
    *   接着，VS Code 会询问你要把它保存在电脑的哪个位置，选择一个你方便管理的文件夹。
    *   克隆完成后，VS Code 会弹出提示，询问你要不要**直接打开**这个项目，点击"打开"即可。

至此，这个 GitHub 项目就已经完整地同步到你的本地电脑上了。

### 同步策略 (二)：将本地项目上传到 GitHub (Push)

如果你是先在电脑上写好了代码，想把它作为一个新项目放到 GitHub 上管理，可以按以下步骤操作：

1.  **在 GitHub 上新建一个空仓库**：在 GitHub 网站上创建一个新的 **Repository (仓库)**。注意：**不要**勾选 "Initialize this repository with a README"，我们需要一个干净的、空的远程仓库。创建完成后，复制浏览器地址栏里的仓库 URL。

2.  **在 VS Code 中初始化本地仓库**：用 VS Code 打开你的本地项目文件夹。打开"源代码管理"面板，点击 **"初始化存储库"** (Initialize Repository) 按钮。

3.  **关联本地与远程仓库**：
    *   在"源代码管理"面板中，点击 **"..."** (更多操作) 按钮，选择 **"远程"** → **"添加远程"**。
    *   在弹出的窗口中，"远程名称" 默认填 `origin`。在 "存储库 URL" 处，粘贴你刚才从 GitHub 复制的仓库地址。

4.  **提交与推送**：
    *   **提交 (Commit)**：在"源代码管理"面板的"更改"区域，点击文件旁的 **"+"** 号将其暂存。在顶部的输入框里写清楚你这回改了啥，然后点击对勾 **"✓"** 完成提交。
    *   **同步 (Sync)**：最后，点击面板顶部的 **"同步更改"** 按钮（或者蓝色的圆圈箭头图标），VS Code 就会把你的代码推送到 GitHub 仓库了。大功告成！

### 持续同步：日常工作流 (Pull/Commit/Push)

当你的本地和远程仓库关联好后，日常的同步操作就很简单了：

| 操作 | 目的 | VS Code 操作 |
| :--- | :--- | :--- |
| **拉取 (Pull)** | 当 GitHub 上的代码有更新时，把它拉取到本地。 | 点击"源代码管理"面板顶部的 **"..."**，选择 **"拉取"**。 |
| **提交 (Commit)** | 保存一个"版本"，记录你的修改。 | 在"更改"区域暂存文件 ("+")，输入提交信息，然后点击"✓"。 |
| **推送 (Push)** | 将本地提交的版本上传到 GitHub。 | 点击"源代码管理"面板顶部的 **"同步更改"** 按钮。 |

### 遇到问题怎么办？

*   **无法克隆或推送？**
    *   **检查 Git 环境**：确保 Git 已安装，并且 VS Code 能识别到。可以在 VS Code 的 `设置` (Settings) 里搜索 `git.path`，看看 Git 的路径是否正确。或者，你也可以直接在 VS Code 的命令行里运行 `git --version`，能正常显示版本号就行。
    *   **检查网络**：确保网络连接稳定。

*   **代码冲突 (Conflict) 了怎么解决？**
    *   当多个人修改了同一个文件的同一处地方，`git pull` 时就会出现冲突。别慌，VS Code 会高亮显示出冲突的代码区域，你需要手动判断并决定保留哪部分，然后保存文件，再把这个解决冲突后的版本 `add` 和 `commit` 一下就行。

*   **想用命令行操作？**
    *   如果你习惯用命令行，可以直接用 VS Code 内置的终端 (`Ctrl + `` `)。常用的 Git 命令如下：
        *   `git clone <仓库URL>`：克隆一个远程仓库。
        *   `git add .`：将所有修改添加到暂存区。
        *   `git commit -m "提交信息"`：提交所有暂存的更改。
        *   `git push`：将本地的提交推送到 GitHub。
        *   `git pull`：从 GitHub 拉取更新到本地。

你目前是想从 GitHub 下载一个现有项目，还是把本地代码推送到新建的仓库呢？可以告诉我你的具体操作场景，我再针对性地给你一些提示～