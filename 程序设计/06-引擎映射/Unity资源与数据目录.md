# Unity 资源与数据目录

| 字段 | 内容 |
|------|------|
| 状态 | 已定稿（基线） |
| 最后更新 | 2026-05-26 |
| 关联 | [实现-数据资产布局](../04-实现/实现-数据资产布局.md)、[仓库布局.md](../../仓库布局.md) |

## Assets 编号目录

| 目录 | 用途 |
|------|------|
| `01_Scripts/` | 全部 C#；按功能模块分子文件夹 |
| `02_Arts/` | 美术 |
| `03_Prefab/` | 预制体 |
| `04_Data/` | **运行时策划数据主目录**（SO、对话、邮件事件等） |
| `05_Scenes/` | 场景 |
| `06_Animation/` | 动画 |

文档：`Docs/`（仓库根，Git 管理，不导入 Unity）。

## `04_Data` 分区（摘要）

| 区域 | 路径模式 | 用途 |
|------|-----------|------|
| 对话与剧情 | `04_Data/对话dat/` | 频道、角色库、剧情演出 |
| 消息系统 | `04_Data/MessageSystem/` | 邮件事件、模板库 |
| 标签 | `04_Data/标签系统/` | `EmployeeTagSO` 等 |
| 压力 | `04_Data/压力系统/` | 压力事件定义 |

完整表见 `Docs/ShenrenshibuStoryLib/程序设计/04-实现/实现-数据资产布局.md`。

## `00_Data` 与菜单常量

`ShenRenShiBuAssetMenu` 中部分创建菜单指向 `Assets/00_Data/`。发布前应统一：

- **方案 A**：改菜单常量，新建资产默认进 `04_Data`；或  
- **方案 B**：文档化 `00_Data` 为草稿区，定期合并入 `04_Data`。

## 脚本模块 ↔ 数据

| 模块 | 典型 SO / 数据路径 |
|------|-------------------|
| Employee | `04_Data/标签系统/` |
| Assignment | `04_Data/` 下委托相关（见 IMPL） |
| MessageSystem | `04_Data/MessageSystem/` |
| DialogSystem | `04_Data/对话dat/` |
| Stress | `04_Data/压力系统/` |

## 技术债（仓库卫生）

| 项 | 建议 |
|----|------|
| `Assets/MailTemplateDatabaseSO.cs` 根目录散落 | 迁入 `04_Data/MessageSystem/` 或 `01_Scripts` 旁路并删根目录副本 |
| 模块内 `Docs/*.md`（如 Assignment） | 长期并入 `Docs/ShenrenshibuStoryLib/程序设计/` 或 `04-实现` |

## 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05-26 | 初稿：对齐 `实现-数据资产布局` 与仓库布局 |
