# 百科

本目录以**稳定标识符 `id`** 为主键组织条目，并按「组织 / 地点 / **系统**（人工智能·桥）/ 文化 / 人物」落在对应子文件夹里，方便人手翻阅。

**勿混**：`系统/` 只收**桥**类管理者 AI 实例。`id` 均可为 `SYS-*`，以 [id-registry](../../治理/id-registry.yaml) 登记路径为准。

条目之间的逻辑关系，以正文互引以及 [治理/id-registry.yaml](../../治理/id-registry.yaml) 中的登记为准。世界基石条文见 [设定真值/00-基石/](../00-基石/)。叙事取向与红线见叙事合同 [NAR-00](../20-叙事合同/NAR-00-叙事母题与基调.md)、[NAR-01](../20-叙事合同/NAR-01-主线张力与终局分型.md)、[NAR-02](../20-叙事合同/NAR-02-玩家责任与叙事红线.md)；总览见 [叙事合同 README](../20-叙事合同/README.md)。

## 新增条目流程

1. 在 [治理/id-registry.yaml](../../治理/id-registry.yaml) 注册新 `id` 与中文标题。  
2. 在对应子文件夹新建 Markdown；文件头的 YAML 须含 `id`、`title`、`status`、`visibility`。  
3. 若条目划定对玩家披露边界，须在 YAML 中写清 `visibility`；条目纳入某对外版本时，同步更新该版本目录下的 `manifest.yaml` 与 `CHANGELOG.md`（细则见 [玩家投放/README.md](../../玩家投放/README.md)）。

## 当前索引（人工维护快照）

| id | 标题 |
|----|------|
| [ORG-HELIOS](组织/赫利俄斯/ORG-HELIOS-赫利俄斯集团.md) | 赫利俄斯集团 |
| [ORG-MILDEPT](组织/赫利俄斯/ORG-MILDEPT-军用武装管理部.md) | 军用武装管理部（通称军武部／军部） |
| [ORG-TECHDEPT](组织/赫利俄斯/ORG-TECHDEPT-技术研发管理部.md) | 技术研发管理部（通称技术部） |
| [ORG-HRDEPT](组织/赫利俄斯/ORG-HRDEPT-人类事务管理部.md) | 人类事务管理部（通称人事部） |
| [ORG-HRDEPT-SCO](组织/赫利俄斯/ORG-HRDEPT-SCO-特殊综合行动小组.md) | 特殊综合行动小组 |
| [ORG-GANG-WOLF](组织/帮派/ORG-GANG-WOLF-狼群.md) | “狼群” |
| [ORG-GANG-HYENA](组织/帮派/ORG-GANG-HYENA-鬣狗帮.md) | 鬣狗帮 |
| [ORG-GANG-LEOPARD](组织/帮派/ORG-GANG-LEOPARD-花豹党.md) | 花豹党 |
| [ORG-REBEL](组织/ORG-REBEL-反抗军.md) | 反抗军 |
| [ORG-MOV-FUF](组织/ORG-MOV-FUF-自由人联合阵线.md) | 自由人联合阵线 |
| [ORG-MOV-BRIDGECULT](组织/ORG-MOV-BRIDGECULT-彼岸范式参照运动.md) | 彼岸范式参照运动（前任管理员隐秘追随网络） |
| [PLC-DISTRICT](地点/PLC-DISTRICT-街区分层与层级-总述.md) | 第九区分片与安全等级（总述） |
| [PLC-RUINS](地点/PLC-RUINS-废墟区-第九区事变遗留片区.md) | 废墟区（第九区事变遗留片区） |
| [SYS-B9002](系统/SYS-B9002-桥与玩家职能.md) | 桥 B-9002 与玩家职能（**人工智能系统**） |
| [SYS-PREV-BRIDGE](系统/SYS-PREV-BRIDGE-前任管理员与第九区废墟事变.md) | 前任管理员与第九区废墟事变（**人工智能系统**） |

| [ENT-CULTURE](文化/ENT-CULTURE-企业文化与话语口径.md) | 企业文化与话语口径 |
| [ENT-HUMANNEC](文化/ENT-HUMANNEC-对人类必要性的工具化界定.md) | 对人类必要性的工具化界定 |
| [ENT-AIBACKLASH](文化/ENT-AIBACKLASH-人工智能污名化与第九区事变后的舆论分化.md) | 人工智能污名化与第九区事变后的舆论分化 |
| [CHR-SOLEN-ELI](人物/CHR-SOLEN-ELI-伊莱·索伦.md) | 伊莱·索伦（人事部部长） |
| [CHR-KAELEN-VOLOK](人物/CHR-KAELEN-VOLOK-科恩·沃洛克.md) | 科恩·沃洛克（防卫科科长） |
| [CHR-ISAAC-MOELLER](人物/CHR-ISAAC-MOELLER-艾萨克·穆尔.md) | 艾萨克·穆尔（服务科科长） |
| [CHR-SERENA-DAY](人物/CHR-SERENA-DAY-瑟琳娜·昼.md) | 瑟琳娜·昼（人力科科长） |
| [CHR-LYNWEI-CHANDRA](人物/CHR-LYNWEI-CHANDRA-凌薇·钱德拉.md) | 凌薇·钱德拉（财务科科长） |
| [CHR-MOEN](人物/CHR-MOEN-摩恩夫人.md) | 摩恩夫人（前服务科科长） |
| [06-玩家情报层级](人物/06-玩家情报层级与投放矩阵.md) | 玩家情报层级与投放矩阵（四科·前任管理员批次） |
