---
name: git-history-cleanup
description: 安全整理并重写 Git 分支历史，在最终仓库 Tree 完全不变的前提下压缩碎片提交、移除已完全回滚或净效果为零的提交链，并用 Tree SHA 做等价校验。用户明确要求“整理最近提交”“合并碎片提交”“清理 revert/临时提交”“重写历史但代码不能变”时使用；不用于普通代码修改，也不得在未获授权时强推共享分支。
---

# Git 历史整理

目标不是“让日志好看”，而是把一段已经完成的开发历史重新组织成少量、可解释、符合仓库规范的逻辑提交，同时证明整理前后的最终仓库状态完全一致。

## 核心不变量

历史整理成功的最高优先级条件是：

```text
OLD_HEAD^{tree} == NEW_HEAD^{tree}
```

Git Tree SHA 相同意味着最终目录结构、文件内容、文件模式、子树与 gitlink 等 Git 记录完全一致。提交数量变少、`git diff` 为空、测试通过都不能替代这个条件。

只要最终 Tree SHA 不相同，就不得把整理后的历史写回目标分支。

## 使用边界

适合：

- 一段时间内产生了大量 fixup、临时、占位、误提交或重复提交。
- 功能经历“新增 → 修复 → 回滚”，最终希望删除已经没有净效果的历史噪声。
- 多个连续提交实际上属于同一个逻辑改动，希望合并成一个清晰提交。
- 用户明确要求重写 `main` / `master` 等分支历史，但要求最终代码完全不变。
- 本地 clone 不可用，但运行环境有 GitHub/GitLab 等低层 Git object API，可以基于 tree/blob/commit/ref 重建历史。

不适合：

- 用户只想修改一个 commit message，且不需要大范围整理。
- 目标分支是多人共享分支，而用户没有明确授权历史重写。
- 分支包含需要长期保留的发布 tag、审计锚点或第三方作者提交，但影响尚未评估。
- 无法建立可恢复的备份分支或无法确认目标分支当前 HEAD。

## 第一原则：最终状态是事实来源

不要只根据 commit message 判断某个提交是否该保留。先看最终净效果：

```bash
git log --graph --decorate --oneline <BASE>..<TARGET>
git diff --name-status <BASE>..<TARGET>
git diff --stat <BASE>..<TARGET>
```

分类时遵循：

- **保留**：最终状态中仍然存在的独立业务/工程改动。
- **合并**：同一功能的连续实现、修复和收尾，最终可表达为一个逻辑提交。
- **删除**：新增后又被完整回滚、创建后删除、临时占位、错误文件等最终净效果为零的提交链。
- **谨慎处理 merge**：只有在不需要保留分支拓扑语义时才线性化；否则优先保留 merge 结构。
- **禁止 no-op commit**：如果新提交的 tree 与父提交完全相同，不创建该提交。

一个提交“看起来有意义”不等于它最终仍然有净效果；一个 revert “看起来是撤销”也不代表前面的所有提交都应该机械保留。

## 阶段 0：读取仓库规则

在生成任何新 commit 之前，先检查仓库内约束：

- `AGENTS.md`
- `CLAUDE.md`
- `CONTRIBUTING.md`
- `git-commit-convention.md`
- `.github/` 中的 CI / branch policy

如果仓库定义了 commit message 规范，所有重建提交都必须遵守。不要把整理历史当成绕过提交规范的机会。

如果多个旧作者身份可能其实属于同一个人，只有在用户明确确认后才合并身份；不要擅自把其他人的提交归到当前用户。

## 阶段 1：冻结旧 HEAD，并先备份

分析完成后，**在真正开始改历史前重新读取一次目标分支**。这是为了避免分析期间目标分支又有新提交。

```bash
TARGET=master
git fetch origin
OLD_HEAD=$(git rev-parse "origin/$TARGET")
OLD_TREE=$(git rev-parse "$OLD_HEAD^{tree}")
```

然后立刻建立备份：

```bash
BACKUP="backup/history-before-$(date +%Y%m%d)"
git branch "$BACKUP" "$OLD_HEAD"
git push origin "$BACKUP"
```

必须记录：

```text
目标分支
OLD_HEAD
OLD_TREE
备份分支
整理区间 BASE
```

如果目标分支在“最初分析”与“冻结”之间发生移动，以最新 HEAD 为准，重新计算 commit 区间和最终 Tree；不要继续使用旧快照。

## 阶段 2：确定整理基线 BASE

BASE 应该是“本次需要整理的历史窗口之前，最后一个保持不动的提交”。

```bash
git merge-base <target> <known-good-ref>
git log --oneline <candidate-base>..<OLD_HEAD>
```

不要为了得到漂亮数字而随意扩大整理窗口。BASE 越早，重写影响越大，旧 commit SHA 失效范围也越大。

## 阶段 3：选择整理策略

### 策略 A：交互式 rebase

适合线性历史、提交数量不多、revert 链简单的情况：

```bash
git rebase -i <BASE>
```

按需使用：

- `pick`：保留
- `reword`：改提交信息
- `squash` / `fixup`：合并
- `drop`：删除

存在重要 merge 结构时使用支持 merge 的方式，而不是无脑拉平。

无论 rebase 多简单，结束后仍然必须做最终 Tree SHA 校验。

### 策略 B：最终 Tree 驱动重建

适合以下复杂场景：

- 大量“新增 → 修复 → revert”交叉出现。
- 合并提交和线性提交混杂。
- 需要把几十个碎片提交压缩成少量语义提交。
- 本地 Git 无法使用，只能通过 GitHub 等平台的 blob/tree/commit/ref API 操作。
- 希望把“最终代码绝不变化”提升为对象级硬约束。

核心做法：**把冻结的 OLD_TREE 当成最终事实来源，用 BASE 作为起点，逐组把最终状态中的精确 blob/subtree 应用到合成历史中。**

伪代码：

```text
parent_commit = BASE
current_tree = BASE_TREE

for logical_group in groups:
    current_tree = apply_exact_final_entries(current_tree, logical_group.paths)

    if current_tree == parent_commit.tree:
        skip  # no-op

    parent_commit = create_commit(
        message=logical_group.message,
        tree=current_tree,
        parent=parent_commit,
    )

assert current_tree == OLD_TREE
NEW_HEAD = parent_commit
```

### Tree 重建时的重要细节

1. **优先复用最终 Tree 中已经存在的 blob/subtree SHA**，不要无理由重新生成文件内容。
2. 每个逻辑提交只吸收属于自己的路径变化。
3. 如果一个顶层模块还包含“以后才应该出现”的改动，不要提前把整个模块 subtree 一次替换成最终版本；应在该模块内部构造中间 tree。
4. 每创建一个逻辑提交后，都检查它与父提交的 tree 是否真的不同。
5. 最后一条提交生成后，先比较 `NEW_TREE` 与 `OLD_TREE`，相同后才能考虑移动目标 ref。
6. 如果低层 API 生成的 commit 不带签名，而仓库要求 signed commits，应改用能够签名的本地 Git / 正常平台合并流程，不要悄悄降低签名要求。

## 阶段 4：逻辑提交怎么分组

优先按“最终意图”而不是旧提交时间顺序机械分组。

推荐规则：

- 一个功能 + 为了让该功能正确工作的连续修复 → 一个功能提交。
- 同一模块内互不相关的两个功能 → 分成两个提交。
- 新增某功能，后来完整 revert，最终完全不存在 → 整条链删除。
- 临时日志、占位文件、错误提交，后来完整删除 → 删除。
- 先删后加，最终形成一个明确的新实现 → 只保留能解释最终状态的逻辑历史。
- 大范围 merge 如果只是带入一个独立功能，可压缩成对应功能提交；如果 merge 拓扑本身有审计/协作意义则保留。
- 文档、CI、构建、业务功能尽量按职责拆开，不把无关路径塞进同一个“万能提交”。

提交信息必须重新按照当前仓库规范生成，不照抄旧历史里的 `tmp`、`修改`、`fix bug` 等低质量消息。

## 阶段 5：目标分支更新前的硬校验

至少执行以下三类验证。

### 1. Tree SHA 等价

```bash
NEW_TREE=$(git rev-parse "$NEW_HEAD^{tree}")

test "$OLD_TREE" = "$NEW_TREE"
```

这是最重要的证明。

### 2. 提交间 diff 为空

```bash
git diff --exit-code "$OLD_HEAD" "$NEW_HEAD" --
git diff --summary "$OLD_HEAD" "$NEW_HEAD"
```

应该没有文件内容、文件模式、重命名等差异。

### 3. 备份仍然指向冻结的旧历史

```bash
test "$(git rev-parse "$BACKUP")" = "$OLD_HEAD"
```

如果在托管平台操作，还应比较备份分支与冻结的旧 SHA，确认 `ahead=0`、`behind=0` 或等价状态。

## 阶段 6：先发布清理分支，再改目标分支

复杂整理优先先得到一个独立清理分支，例如：

```text
refactor/clean-history-YYYYMMDD
```

先验证：

- 清理分支 HEAD = 计划中的 NEW_HEAD。
- 清理分支 Tree = OLD_TREE。
- 备份分支仍然 = OLD_HEAD。
- BASE → 新 HEAD 的提交数量与计划一致。

然后**再次读取目标分支远端 HEAD**。如果它已经不等于冻结的 `OLD_HEAD`，停止强推并重新评估；不能覆盖别人刚提交的新工作。

本地 Git 优先使用带 lease 的强推：

```bash
git push \
  --force-with-lease="$TARGET:$OLD_HEAD" \
  origin "$NEW_HEAD:refs/heads/$TARGET"
```

使用 GitHub 等 API 的 `update_ref(force=true)` 时，也要先读取当前 ref，并手工实现同样的 lease 语义：

```text
current_target_head == OLD_HEAD
```

只有成立才允许 force update。

## 阶段 7：改完目标分支后再验证一次

重新读取目标分支：

```bash
git fetch origin
FINAL_HEAD=$(git rev-parse "origin/$TARGET")
FINAL_TREE=$(git rev-parse "$FINAL_HEAD^{tree}")

test "$FINAL_HEAD" = "$NEW_HEAD"
test "$FINAL_TREE" = "$OLD_TREE"
```

再确认：

- 备份分支仍指向旧 HEAD。
- 清理分支与目标分支一致。
- BASE 到目标分支的新提交数量正确。
- 分支保护、required checks、CI 状态已重新检查。

### Tree 相同不等于“新 commit 的 CI 已通过”

历史重写会产生新的 commit SHA。即使最终 Tree 与旧代码完全一致，也不要把旧 SHA 的 CI 状态当作新 SHA 的 CI 结果。

如果新 SHA 没有 workflow run / status check，应明确报告：

```text
代码 Tree 已证明完全一致；当前新提交没有可确认的 CI 运行，因此不宣称测试已通过。
```

## 本地克隆如何同步

历史重写后，旧本地分支会与远端分叉。

### 本地没有未提交工作

```bash
git fetch origin
git checkout <target>
git reset --hard origin/<target>
```

### 本地还有工作

不要直接 `reset --hard`。先：

```bash
git status
git branch backup/local-before-history-sync
```

再根据实际情况 commit/stash 本地工作，把本地独有提交 rebase 或 cherry-pick 到新的目标分支。

## 回滚

备份分支是历史重写的恢复点，不要刚整理完就删除。

需要回滚时：

1. 先读取目标分支当前 HEAD，确认没有整理后新增的其他工作。
2. 读取备份分支，确认仍然是 `OLD_HEAD`。
3. 用 `--force-with-lease` 或 API 的等价保护把目标分支恢复到旧 SHA。
4. 再验证目标 Tree / HEAD。

如果目标分支在整理后已经有新提交，不允许直接把它粗暴恢复到备份点；先保护新增工作。

## 最终报告必须包含

完成后至少向用户报告：

- 整理前目标 HEAD。
- 整理前目标 Tree SHA。
- 整理后目标 HEAD。
- 整理后目标 Tree SHA。
- 两个 Tree SHA 是否完全相同。
- BASE 与整理前/后的提交数量。
- 哪些类型的提交链被合并或删除。
- 备份分支名称与它是否仍精确指向旧 HEAD。
- 清理分支与目标分支是否一致。
- 新 SHA 是否真的有 CI / workflow 结果。
- 本地 clone 应如何同步。

不要只说“代码没变”。应给出可核验的 Git 对象证据。

## 禁止事项

- 未经用户明确授权强推共享分支。
- 没建备份就开始破坏性重写。
- 只看 commit message，不看最终净效果。
- 最终 Tree 不相同仍继续 force push。
- 目标分支在冻结后又移动，却仍覆盖旧快照。
- 把别人的提交作者改成当前用户，除非身份已明确确认。
- 因为“Tree 一样”就宣称新 SHA 的 CI 已通过。
- 整理完成后立即删除唯一备份分支。
- 给有未提交工作的本地 clone 直接执行 `reset --hard`。