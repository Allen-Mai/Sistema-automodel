# SISTEMA 建模规范

> **适用**：本机 SISTEMA **3.0.4**（对应 **ISO 13849-1:2023**）中建立、维护和交付机器安全回路评估项目。
> **目的**：统一项目结构、参数来源与校验口径，让不同人（或脚本/AI）建出的项目**结构一致、参数可追溯、结果可复核**。
> 本规范同时是生成器 `tools/sistema/sistema_auto.py` 的输入契约。

---

## 0. 一句话流程

```
风险评估定 PLr → 画原理电路图(功能/测试通道) → 结构分析定类别 → 在 SISTEMA 里按六层层级建模
→ 逐层填参数(数据来自厂家/附录D/附录C) → 校验 Messages 无红叉 → PL ≥ PLr → 保存交付
```

---

## 1. 工程与文件规范

| 项 | 规范 |
|---|---|
| 软件版本 | **SISTEMA 3.x**（3.0.4 实测）。2.x 仅用于维护 2015 版旧项目；2015 版过渡期到 **2027-05-15** |
| 项目文件 | `.ssm`（tiOPF XML）。同目录会自动出现 `.ssm_backup` 与打开期间的 `.<项目名>~ssm` 锁文件 |
| 标准标识 | 项目内 `normversion` 必须是 `ISO 13849-1:2023, ISO 13849-2:2012` |
| 目录约定 | `…\SISTEMA V2 测试建模\<编号>-<设备名>\<设备名>.ssm`，同目录放 `Documents\`、`Standards\` |
| 文件命名 | 与设备名一致（中文可用），**不要**用 `新建项目`/`test` 之类 |
| 保存纪律 | 定稿后 `Ctrl+S`；交付前确认锁文件已释放（关闭项目后 `.<名>~ssm` 应消失） |

---

## 2. 层级结构规范（六层）

```
PR 项目        Project          一个 .ssm = 一台设备（或一个可独立评估的子机）
└ SF 安全功能   Safety Function  PLr(要求) vs PL(实际)、PFHd
  └ SB 子系统   Subsystem       一条串联链的一个环节：Cat / MTTFd / DCavg / CCF / PFHd
    ├ CH 通道   Channel         功能通道 ch1、ch2
    └ TE 测试通道 Test Channel  类别 2 需要的定期测试路径（chTest）
      └ BL 块   Block           通道内的功能单元：MTTFd、DC、位号
        └ EL 元素 Element       元件的具体数据（B10d、nop…）
```

**插入约束**（SISTEMA 强制，放错层级会被拒绝）：

```
EL → 只能进 BL ／ BL → 只能进 CH·TE ／ CH·TE → 属于 SB ／ SB → 只能进 SF ／ SF → 属于 PR
```

**结构约定**：

- 一个 **SF** 下的多个 **SB 是串联的**，按信号流从输入到输出排列（如 急停按钮 → 安全继电器 → 输出切断）。
- 每个 **SB 固定拥有三个通道** `ch1` / `ch2` / `chTest`；即使不用也保留，**不要删除**。
- **设定 Category 后 SISTEMA 会自动生成通道**，不需要手工建 CH。
- 汇总方向：BL → CH → SB → SF → PR。

---

## 3. 命名规范

| 层 | 规范 | 示例 |
|---|---|---|
| PR | 设备名（与文件名一致） | `移印机` |
| SF | **完整句子**：触发事件 + 安全相关反应 + 危险部件（Cookbook 6 要求） | `Actuation of the emergency stop devices leads to STO of all pad-printing axes` |
| SB | 功能角色 + 元件概要（含数量/型号） | `Emergency stop devices (6 x XB4BS84441)`、`PNOZ c1 safety relay`、`SV630 STO inputs (8 axes)` |
| CH | **保持默认** `Channel 1 / Channel 2`，不重命名 | — |
| BL | **位号**（现场图纸上的标识），多件串联可用区间写法 | `S1..S6.1`、`KA1`、`KA2` |
| EL | 型号（厂家订货号） | `XB4BS84441`、`G7SA-4A2B`、`SV630 STO` |

**为什么 BL 用位号而不是型号**：位号对应现场实际器件，便于复核与整改；型号放在 EL（以及 BL 的 `deviceid`/`partno` 字段）。

---

## 4. 子系统形态的选择（关键决策）

**判据：厂家是否给出了该部件的 PL/PFH（或 SIL/PFH）与类别。**

| 形态 | 适用对象 | SISTEMA 中的做法 |
|---|---|---|
| **封装子系统**<br>Encapsulated | 安全 PLC、安全模块、**认证安全继电器**（PNOZ、G9SX…）、变频器安全功能（STO/SS1）等**厂家已给 PL/PFH** 的部件 | 子系统 → `PL` 标签 → **`Enter PL / PFH directly`** → 填厂家值；Category 在下一标签填。**通道保持为空，不拆解内部结构** |
| **刚性结构子系统**<br>Rigid structure | 自己用元件搭出来的通道（按钮串联、接触器/继电器回路等） | 子系统 → `PL` 标签 → **`Determine PL / PFH from Category, MTTFd and DCavg`** → 再逐项填 Cat / MTTFd / DCavg / CCF，并建块 |

> ⚠️ 常见错误：把 PNOZ/G9SX 这类认证安全继电器当成 Cat 4 的刚性结构子系统建。那样 SISTEMA 会要求你提供
> MTTFd / DCavg / CCF，而这些数据厂家并不以该形式给出 —— 应当走封装子系统，直接填厂家的 PL/PFH。

封装子系统的两个开关：

- 勾选相应复选框后 **PL 与 PFH 会按平均值互相推算**（只填一个即可）。
- 若能排除所有危险元件故障 → 勾 **`Failure exclusion`**（PFH = 0）。

---

## 5. 参数填写规范

### 5.1 各层必填项

| 层 | 必填 | 说明 |
|---|---|---|
| SF | 安全功能描述、**PLr** | PLr 由风险图（S/P/F，2023 版 P 参数基于五因素）或机器专用标准给出 |
| SB | **Category** | `B / 1 / 2 / 3 / 4`；2023 版的核心架构单元 |
| SB | MTTFd、DCavg、CCF | 单通道 ≤100 a（**Cat 4 ≤2500 a**）；Cat 2/3/4 必须给 DCavg；CCF **≥65** |
| CH | 通道类型 | 功能通道 / 测试通道（Cat 2 必须有测试通道） |
| BL | MTTFd、DC | 分 输入 / 逻辑 / 输出 三种角色 |
| EL | B10d 或 MTTFd | 机电件给 B10d + nop；电子件给 MTTFd（B10d 置 0） |

### 5.2 参数分级（ISO 13849-1）

| 参数 | 分级 |
|---|---|
| MTTFd | 低 3~10 a ／ 中 10~30 a ／ 高 30~100 a（**Cat 4 通道上限 2500 a**） |
| DC | 无 <60% ／ 低 60~90% ／ 中 90~99% ／ 高 ≥99% |

### 5.3 类别与诊断覆盖率的匹配（必须自检）

| 类别 | 结构 | DCavg | CCF | 最大 PL |
|---|---|---|---|---|
| B | 单通道，基本安全原则 | 无 | 不相关 | b |
| 1 | 单通道，经验证元件与原则 | 无 | 不相关 | c |
| 2 | 单通道 + 定期测试 | 低~中 | ≥65 | d |
| 3 | 冗余，单一故障不致功能丧失 | **低~中** | ≥65 | d |
| 4 | 冗余，故障累积不致功能丧失 | **高（≥90%）** | ≥65 | e |

> ⚠️ **DCavg 只有"低"（60~90%）时不能选 Cat 4**，SISTEMA 会报
> `The current configuration does not allow to calculate the PFH value using the standard`。

### 5.4 计算公式（备查）

- `MTTFd = B10d / (0.1 × nop)`，`nop = d_op × h_op × 3600 / t_cycle`
- `DCavg = Σ(DCᵢ/MTTFdᵢ) ÷ Σ(1/MTTFdᵢ)`（按 MTTFd 加权）
- 通道 MTTFd（部件计数法）：`1/MTTFd = Σ(1/MTTFdᵢ)`；两通道不等时按标准 D.2 对称化
- 串联子系统：组合 PFHd = 各 PFHd 之和；组合 PL 受"最低 PL"与"PFHd 总和对应的 PL"双限
- **PL/PFHd 以 SISTEMA 计算结果为准**，不要用简化公式替代

### 5.5 数据来源与追溯（优先级从高到低）

1. **元件厂家数据**（样本/安全手册）—— 首选，需在项目文档里记录来源
2. **EN ISO 13849-1 附录 D** 的既有数据集合
3. **EN ISO 13849-1 附录 C 典型值** —— SISTEMA 内置为 `Typical component values` 按钮
4. DC 值可用 **`DC-rating by choosing measures`** 调 **附录 E** 的诊断措施表；标准给区间时取区间内具体值

> 用典型值时必须在 `Documentation` / `Use case` 字段注明依据，否则复核时无法追溯。

---

## 6. 元件细分规范（块 / 元素）

| 元件类型 | 建法 | 示例值 |
|---|---|---|
| **机电/气动件**（按钮、接触器、继电器、阀） | **必须细分到元素级**，在元素上填 `B10d` + `nop`；块上选 `Determine MTTFd-value from elements`、`Determine DC-value from elements` | 接触器 `b10d=5000000, nop=240`；急停按钮 `b10d=127500, nop=1` |
| **电子件**（PLC、变频器、安全模块、电容） | 直接给 MTTFd，`b10d=0`、`nop` 不设 | PLC `mttfd=10`；变频器 `mttfd=35`；电容 `mttfd=45662` |

> **依据**：官方 35 个示例项目中 256 个块配了 244 个元素，凡带 B10d 的元件都拆到了元素级。
> 把 B10d 填在块级 SISTEMA 也能算，但与官方结构不一致，且不利于按元件追溯。

块/元素的 `Function` 按信号流标注：`Input` / `Logic` / `Output`。

---

## 7. 建模流程

### 7.1 结构分析（建模前的纸面工作）

1. 在原理电路图上标出**功能通道**与**测试通道**
2. 沿"元件最少的那条功能通道"，从左到右（传感器 → 执行器）把元件依次写成块
3. 逐个块按类别特征（冗余 / 测试 / 经验证元件）归入相应类别的子系统
4. 若厂家已声明 PL/PFH → 作为**封装子系统**，不再拆解
5. 判决：单个未检测故障后仍保持安全功能 → **Cat 3**；第二个未检测故障后仍保持 → **Cat 4**；
   有测试通道且测试能触发安全状态 → **Cat 2**；无冗余无测试 → **Cat 1 / B**

> 不符合"指定架构"的元件布置**无法用 SISTEMA 分析**（需改结构或改用 Markov 等方法，见 IEC 61508-6 附录 B）。

### 7.2 在 SISTEMA 里录入（官方 Cookbook 1 第 4 章）

| 步 | 操作 | 界面落点 |
|---|---|---|
| 1 | 新建项目 | `New` → 填 Project name |
| 2 | 建安全功能 | `Safety function` 标签 → `New`（或选中项目按 **Ctrl+Insert**） |
| 3 | 设 PLr | SF → `PLr` 标签 |
| 4 | 加子系统 | SF → `Subsystems` 标签 → `New` |
| 5 | 封装子系统 | 见 §4 上格 |
| 6 | 刚性结构子系统 | 选 `Determine PL / PFH from Category, MTTFd and DCavg`，然后依次填 `Category`（并逐条评估类别要求）→ `MTTFd` → `DCavg` → `CCF` |
| 7 | 输入块 | **选定 Category 后自动生成通道**；在 Channel 下 `New` 建块 |
| 8 | 输入元素 | 块的 `Elements` 标签 → `New`（凡有 B10d 的元件） |
| 9 | 填安全数据 | `MTTFd` 标签（四选一：从元素 / 直接输入 / **从 B10D 计算** / 从 λ·MTTF·MTBF）；`DC` 标签（三选一：从元素 / 直接输入 / 从措施清单） |
| 10 | 检查 | 消息窗口无红叉 → 左下角读出结果 → **PL ≥ PLr** |

### 7.3 结果不达标时的调整顺序

1. 提高元件 MTTFd / 换更高 B10d 的型号
2. 改善故障检测（提高 DC，或增加诊断措施）
3. 提高类别（Cat 2 → 3 → 4），但必须同时满足该类别对 DCavg / CCF 的要求
4. 拆分子系统 / 改用封装子系统

---

## 8. 交付前校验清单

- [ ] 每个 SF 的 **PL ≥ PLr**，Messages 无红叉
- [ ] 每个 Cat 2/3/4 子系统的 **CCF ≥ 65**（有 CCF 措施清单或直接评分依据）
- [ ] Cat 4 子系统的 **DCavg ≥ 90%**；Cat 3 的 DCavg 在 60~90%
- [ ] **凡带 B10d 的元件都已细分到元素级**
- [ ] 所有 MTTFd > 3 a（或由 B10d+nop 算出）
- [ ] SF 名称含**触发事件 + 反应 + 危险部件**三要素
- [ ] 参数来源（厂家数据 / 附录 C / 附录 D）已在文档字段注明
- [ ] 项目已 `Ctrl+S` 保存，锁文件已释放
- [ ] （如导出）PDF 报告已生成归档

---

## 9. 自动化建模

### 9.1 生成器

```bash
python tools/sistema/sistema_auto.py demo  <out.ssm>              # 内置移印机急停示例
python tools/sistema/sistema_auto.py build <spec.json> <out.ssm>  # 吃结构化描述
python tools/sistema/sistema_auto.py show  <file.ssm>             # 查看已有项目结构
python tools/sistema/sistema_auto.py schema <template.ssm>        # 打印模板的列定义
```

**工作原理**：拿一个本机 SISTEMA 保存的 `.ssm` 当**模板**，继承它的字段声明、表集合、每列默认值与数字格式，
只重建数据行 —— 这样字段名与格式永远跟当前软件版本一致。

**生成前的自检**（脚本内置）：CCF<65、Cat 4 配低 DCavg、Cat 3/4 通道缺块、MTTFd≤3、带 B10d 未拆到元素级。

### 9.2 生成后的必做动作

新生成的项目打开后会报 `PLr not reached` —— 因为 `plcal` / `pfhcal` 是 **SISTEMA 计算后回写的字段**，
脚本只能写占位值。**这不是文件缺陷**（手工建的项目未触发重算时同样如此）。

```
脚本生成骨架 → SISTEMA 打开核对 → 界面里改一次参数（切换 Category 或改 PLr）触发重算 → Ctrl+S
```

### 9.3 写文件时的四条硬规则（生成器已实现，手改文件时同样适用）

| 规则 | 违反后果 |
|---|---|
| **每张表的所有声明列都要写出来**，空值写 `""` | 缺列 → `Error reading field <Document>`，文件打不开 |
| **只能写 `<fields>` 声明过的列** | 未知属性 → **错误码 1866** |
| 表集合与表顺序由模板决定（含 `messagehelperops` 等辅助表） | 造表/漏表都可能被拒 |
| 数字格式随版本：**3.0.4 用点号**（`0.65`），2.0.8 官方示例用逗号 | 照抄 2.0.8 示例会踩坑 |

---

## 10. 错误速查表

| 报错 | 原因 | 修法 |
|---|---|---|
| `Invalid MTTFD value: -1` / `lower than or equal to 3` | 块的 MTTFd 非法 | 给 B10d+nop 让软件算，或直接给 >3 的值 |
| `Invalid B10D value: -1` | 电子件 B10d 为空 | 显式写 `b10d=0` |
| `The attribute 'pl' is not allowed`（1866） | 给子系统写了 `pl` | PL 存在 `plsubitemscal` / `pldirectbindcal` |
| `The attribute 'pldirectcal' is not allowed`（1866） | 用了 2.0.8 的旧列名 | 3.0.4 改名为 **`pldirectbindcal`** |
| `Error reading field <Document>` | **漏写了列** | 所有声明列都要写，空值 `""` |
| `The current configuration does not allow to calculate the PFH value using the standard` | 类别与 DCavg/MTTFd 不匹配 | Cat 4 需 DCavg ≥90%；否则降到 Cat 3；单器件子系统用 `detDirect` |
| `Not all the conditions of the chosen category are met` | 类别要求未逐条满足（常见是 CCF<65） | 补 CCF 措施或降类别 |
| `PLr is not reached`（刚生成的项目） | `plcal`/`pfhcal` 未重算 | 界面里改一次参数触发重算 |
| `The project '…' is already loaded` | 重复打开同一项目 | 先 `Close Project`（Ctrl+F4） |

---

## 11. 相关文档

| 文档 | 内容 |
|---|---|
| `skills/sistema-safety-assessment/SKILL.md` | 本规范的**操作细则版**：软件界面、Win32 消息自动化、`.ssm` XML 结构、ISO 13849-1:2023 条款、IFA 官方资源、急停建模参照模板 |
| `tools/sistema/ssm-schema.md` | `.ssm` 九张表的完整字段清单、枚举取值、oid 关联、7 条实测失败案例 |
| IFA *SISTEMA Cookbook 1* | 从原理电路图到 SISTEMA 建模的官方流程（本规范 §7 的来源） |
| IFA *SISTEMA Cookbook 6* | 安全功能的定义要素（本规范 §3 的 SF 命名依据） |
| IFA Report 2/2017e | 52 个应用示例（35 个 `.ssm` 示例项目，急停参照见 Example_10） |

---

*本规范随实践更新；修订时请同步 `skills/sistema-safety-assessment/SKILL.md` 与 `ssm-schema.md`。*
