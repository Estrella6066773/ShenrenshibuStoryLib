# 实现：员工与标签 Buff（Employee）

| 字段 | 值 |
|------|-----|
| 模块键 | Employee |
| 主代码路径 | `Assets/01_Scripts/Employee/` |

## 1. 职责边界

- **负责**：`EmployeeData` 模型、`EmployeeController` 状态变更、`EmployeeRuntimeDataRegistry` 通知、`EmployeeTagSO` / `EmployeeTagDatabaseSO`、标签 Buff 聚合与应用。
- **不负责**：委托状态机（Assignment）；压力数值本体（Stress）。

## 2. 核心类型

| 类型 | 路径 | 说明 |
|------|------|------|
| `EmployeeData` | `Model/EmployeeData.cs` | 运行时数据 |
| `EmployeeController` | `Controller/EmployeeController.cs` | 分配/解除/待处理/开除等 |
| `EmployeeRuntimeDataRegistry` | `Controller/EmployeeRuntimeDataRegistry.cs` | 注册与变更广播 |
| `TagBuffAggregator` | `Model/Tags/TagBuffAggregator.cs` | 从标签列表聚合 `TagBuffSnapshot` |
| `TagBuffSnapshot` / `ITagBuffResolver` | `Model/Tags/` | 快照与解析抽象 |
| 视图 | `View/*` | 卡牌、详情、点击分发等 |

## 3. Buff 通道

`TagModifierChannel` 支持能力、日薪、个人效率、压力获得等（见 `TagBuffAggregator.AccumulateFromTag`）。

## 4. 集成

- 委托与矛盾通过注册表与 `EmployeeStatus` 协作；`EmployeeWorkStateResolver` 供任务进度判断工作时状态。

## 5. 关联需求

- `Docs/ShenrenshibuStoryLib/系统设计/02-需求/需求-员工模型与标签Buff.md`



