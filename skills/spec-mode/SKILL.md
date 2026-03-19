---
name: spec-mode
description: Specification-driven development for complex features. Triggers when user mentions "spec", "specification", "规范", or asks to plan a complex feature. Use for multi-file changes, architectural decisions, or when requirements need clarification before implementation.
---

# Spec Mode - Structured Development

This skill creates structured specification documents following the `.kiro/specs/` format used in the project.

## When to Use

Trigger this skill when:
- User mentions "spec", "specification", "规范"
- Complex features spanning multiple files
- Architectural changes requiring design approval
- Requirements need clarification before coding
- User asks to "plan" or "design" before implementing

## Spec Directory Structure

Each spec is a directory under `.kiro/specs/<feature-name>/` containing:

```
.kiro/specs/<feature-name>/
├── requirements.md    # 需求文档（用户故事 + 验收标准）
├── design.md         # 设计文档（架构、技术选型、字段设计）
├── tasks.md          # 任务清单（checkbox 格式）
└── *.md              # 其他实现文档（可选）
```

## Three-Phase Workflow

### Phase 1: Requirements Gathering

**Goal**: Create `requirements.md`

1. Ask clarifying questions about the feature
2. Write user stories in format: "作为[角色]，我希望[功能]，以便[价值]"
3. Define acceptance criteria using WHEN/THEN/SHALL format
4. Identify edge cases and constraints
5. Create terminology glossary if needed

**Output Template**:
```markdown
# 需求文档

## 简介
[功能概述，1-2段]

## 术语表
- **Term**: Definition

## 需求

### 需求 1: [功能名称]

**用户故事：** 作为[角色]，我希望[功能]，以便[价值]。

#### 验收标准

1. WHEN [条件] THEN System SHALL [行为]
2. THE System SHALL [要求]
3. IF [条件] THEN System SHALL [行为]
```

---

### Phase 2: Design & Planning

**Goal**: Create `design.md` and `tasks.md`

1. Propose technical approach and architecture
2. Define data models and API contracts
3. List specific files to create/modify
4. Consider trade-offs and alternatives
5. Break down into granular tasks
6. **Get user approval before proceeding**

**design.md Template**:
```markdown
# 设计文档

## 概述
[设计目标、技术选型]

## 核心设计目标
1. **目标1**: 说明
2. **目标2**: 说明

## 技术选型
| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 | ... |
| 后端 | Spring Boot | ... |

## 架构设计
[组件图、流程图、数据流]

## 数据模型
[实体定义、字段说明]

## API 设计
[接口列表、请求/响应格式]

## 涉及文件清单
| 文件 | 修改类型 | 说明 |
|------|---------|------|
```

**tasks.md Template**:
```markdown
# 任务清单

## 1. 后端开发
- [ ] 1.1 创建数据模型
- [ ] 1.2 实现 Service 层
- [ ] 1.3 实现 Controller 层

## 2. 前端开发
- [ ] 2.1 创建 API 接口
- [ ] 2.2 实现核心组件
- [ ] 2.3 集成路由

## 3. 测试
- [ ] 3.1 单元测试
- [ ] 3.2 集成测试
```

---

### Phase 3: Implementation

**Goal**: Execute tasks and update progress

1. Use `TaskCreate` tool to create trackable tasks from `tasks.md`
2. Execute approved design systematically
3. Update task status with `TaskUpdate` as you progress
4. Test incrementally as you build
5. Document significant decisions
6. Verify against acceptance criteria

**Implementation Flow**:
```
1. Read tasks.md
2. Create tasks using TaskCreate tool
3. For each task:
   - TaskUpdate(status: in_progress)
   - Implement the task
   - Test the implementation
   - TaskUpdate(status: completed)
4. Verify all acceptance criteria met
```

## Tool Integration

### Use TaskCreate for Task Tracking

When starting implementation, convert `tasks.md` into trackable tasks:

```javascript
// Example: Create task from tasks.md
TaskCreate({
  subject: "创建数据模型",
  description: "创建 AdvancedSearchRequest.java, FieldMetadata.java 等 DTO 类",
  activeForm: "创建数据模型中"
})
```

### Use EnterPlanMode for Complex Planning

For very complex features, use `EnterPlanMode` tool to get dedicated planning assistance before creating the spec.

## Communication Style

- Use clear section headers matching the template
- Write in Chinese for requirements and design (match project language)
- Be concise but thorough
- Ask questions early rather than making assumptions
- Present options when multiple approaches are valid
- Confirm understanding before moving to next phase

## Example Trigger Phrases

- "Let's spec out this feature first"
- "I need to plan a complex change"
- "Can you help me design this before coding?"
- "写一个规范文档"
- "创建一个 spec"
