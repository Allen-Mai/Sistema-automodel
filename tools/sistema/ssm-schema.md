# SISTEMA `.ssm` 文件结构参考

> 数据来源：**35 个 IFA Report 2/2017e 官方示例项目**（`ssmversion 2.0.8`）+ 本机 SISTEMA 3.0.4 生成的项目。
> 这份文档是"**直接生成合法 .ssm**"这条自动化路线的实现依据。

## 0. 文件格式

tiOPF XML：

```xml
<xmldocdata>
  <table table_name="projectops">
    <fields><field field_name="oid"/>…</fields>
    <rows><row oid="…" name="…" …/></rows>
  </table>
  …
</xmldocdata>
```

**每一列都是 `<row>` 的一个 XML 属性**——所以每张表就是一个 `list[dict]`。
解析用 `xml.etree.ElementTree` 即可，见 `tools/sistema/ssm_inspect.py`、`extract_examples.py`。

## 1. 表与完整字段清单

### projectops（PR 项目，恒 1 行）

```
oid, ssmversion, normversion, isprotected, name, author, tester, manager, document,
documentation, filename, machinename, standardsfolder, documentsfolder, createdate,
status, number, version
```

### sfops（SF 安全功能）

```
oid, ssmversion, normversion, isprotected, projectopoid, name, document, documentation,
plr, plrdet, plrdocumentation, plrdocument, plrstandard, plrstandardfile,
reaction, requestfrequency, responsetime, priority,
plrgraphdocumentation, plrgraphdocument,
riskparamf, riskparamp, riskparams, wparameter,
safestate, sftype, triggerevent, opmode,
plcal, pfhcal
```

- `plr` 要求等级，`plcal` / `pfhcal` 是**算出来的实际值**（打开项目会重算）
- `riskparamf` / `riskparamp` / `riskparams` 是风险图的 F/P/S 参数，`wparameter` 对应 P 参数的新表述

### componentops（SB 子系统）

```
oid, ssmversion, normversion, isprotected, sfopoid, name, document,
catstandard, catstandardfile, catconditionsrelevant,
ccfscore, ccfscoredet, ccfdocumentation, ccfdocument,
dcavg, dcavgdet, dcavgdocumentation,
mttfddocumentation, mttfd, mttfddet,
pfh, pldet, pldocumentation,
isplpfhbind, pldirectnobind, pldirectsoftware, sildirectnobind,
useworstcasemttfd, reducedtestingrate, catconditions, plconditions,
libversion, libname, libid, liburl, libinfo, libfilename, language,
manufacturer, manufacturericonfilename, manufacturer_bool_a/b/c, manufacturer_text_a/b/c,
deviceid, devicegroup, deviceiconfilename, description, partno, revision,
equipmentid, inventoryno, functiontypes, missiontime,
cat, catdocumentation, usecase, usecasedocumentation, archive,
deviceidreadonly, devicevaluedatareadonly,
device_bool_a/b/c, device_text_a/b/c,
sildirectbindcal, pldirectbindcal, plsubitemscal, plsubitemssimplecal,
pfhsubitemscal, pfhsubitemssimplecal
```

- **没有 `pl` 字段！** PL 只存在于 `pldirect*cal` / `plsubitemscal` / `plsubitemssimplecal` 里。
  给 `componentops` 写 `pl` 属性会报错：`Element 'row', attribute 'pl': The attribute 'pl' is not allowed.`（错误码 1866）
- `pfh` 在官方示例里**所有子系统都是 `3,8E-5`**（模板默认值），真正有效的是 `plsubitemscal` + `pfhsubitemscal` 系列

### channelops（CH / TE 通道）

```
oid, ssmversion, normversion, isprotected, channeltype, componentopoid, name
```

每个子系统固定 3 个通道：`ch1`、`ch2`、`chTest`（`name` 通常为空）。

### blocops / elementops（BL 块 / EL 元素，字段完全相同）

```
oid, ssmversion, normversion, isprotected, parentopoid, name, document,
dc, dcdet, dcmeasureopoid, dcdocumentation, dcmeasuredocumentation,
mttfddocumentation, mttfd, b10d, technology, nop, nopday, nophour, nopcycle,
b10, lambda, mttf, mtbf, rdfb10, rdfmttf, rdfb10readonly, rdfmttfreadonly,
calcmttfddet, calcb10ddet, mttfddet,
libversion, libname, libid, liburl, libinfo, libfilename, language,
manufacturer, manufacturericonfilename, manufacturer_bool_a/b/c, manufacturer_text_a/b/c,
deviceid, devicegroup, deviceiconfilename, description, partno, revision,
equipmentid, inventoryno, functiontypes, missiontime,
cat, catdocumentation, usecase, usecasedocumentation, archive,
deviceidreadonly, devicevaluedatareadonly,
device_bool_a/b/c, device_text_a/b/c
```

- EL 复用 BL 的表结构（层级靠 `parentopoid` 区分）
- 空元素的模板值：`mttfd=10 dc=0 b10d=0 nop=-2 tech=tecUnknown`

### dcmeasureops（DC 措施）

```
oid, ssmversion, normversion, isprotected, dcmax, dcmin, dc, dependency,
description, documentation, document, heading, insufficientpls, dcmid
```

官方示例里是 `dcmin=0, dcmax=0,99, dc=0` 这样的区间定义。

### ccfmeasureops（CCF 措施）

```
oid, ssmversion, normversion, isprotected, componentopoid, description,
documentation, document, heading, number, score, ccfmid
```

每行一条措施，`score` 是该措施得分，子系统总分记在 `componentops.ccfscore`。

### libmetadata（库元数据）

```
ssmversion, normversion, isprotected, lastchange, info, name, author, url,
standardsfolder, documentsfolder, lib_bool_a/b/c, lib_text_a/b/c, oid
```

## 2. 枚举取值（写错会被拒绝或误读）

| 字段 | 取值 |
|---|---|
| `plr`, `plcal`, `plsubitemscal`, `plsubitemssimplecal`, `pldirectcal` | `plN`（无）/ `plA` / `plB` / `plC` / `plD` / `plE` |
| `cat` | `catB`（**B 是大写字母**）/ `cat1` / `cat2` / `cat3` / `cat4` |
| `technology` | `tecElectronic` / `tecElectromechanic` / `tecPneumatic` / `tecHydraulic` / `tecMechanic` / `tecUnknown` |
| `functiontypes` | `fncInput` / `fncLogic` / `fncOutput` / `fncUnknown` |
| `channeltype` | `ch1` / `ch2` / `chTest` |
| `plrdet`, `pldet`, `mttfddet`, `dcavgdet`, `ccfscoredet`, `calcmttfddet` | `detDirect`（本级直接给值）/ `detSubItems`（由下级汇总）/ `calcMTTFdMTTF`（由 MTTF 推算） |
| `sftype`, `reaction` | 自由文本（官方示例里英/德混用） |
| `normversion` | `ISO 13849-1:2023, ISO 13849-2:2012`（新版）/ `ISO 13849-1:2015, ISO 13849-2:2012`（官方示例） |
| `ssmversion` | 官方示例为 `2.0.8`；新格式见本机 SISTEMA 3.0.4 保存的文件 |

## 3. 数字格式（最容易踩的坑）

- **小数点用逗号**（德语区域设置）：`PFHcal=4,23E-6`、`mttfd=518,887505188875`、`pfh=3,16227766016838E-5`
- **`-2` 是"未设置"占位符**：`nop=-2`、`mttfd=-2`
- `b10d=0` 表示不使用 B10d（改由 MTTFd 直接给）
- `dc=0` / `dcavg=0` / `ccf=0` 即 0 %

## 4. oid 层级关联

```
projectops.oid  ←  sfops.projectopoid
sfops.oid       ←  componentops.sfopoid
componentops.oid ←  channelops.componentopoid
channelops.oid  ←  blocops.parentopoid
blocops.oid     ←  elementops.parentopoid
```

`oid` 是 tiOPF 的 GUID 字符串（形如 `E1E20000-…` 的 16 字节 oid 的文本形式），生成时用随机 GUID 即可。

## 5. 生成项目时不要碰的字段

| 字段 | 原因 |
|---|---|
| `componentops.pl` | **该属性不存在**，写了直接报错 1866 |
| `sfops.plcal` / `sfops.pfhcal` | 软件算的值；填错不致命（打开会重算），但会先显示旧值 |
| `componentops.pfh` | 模板默认 `3,8E-5`；真正生效的是 `*cal` 系列 |
| `blocops.mttfd` | 必须 > 3，否则报 `A MTTFD value lower than or equal to 3 is not accepted` |
| `blocops.b10d` | 电子件必须为 `0`（空值会报 `Invalid B10D value: -1`） |

## 6. 已验证的失败案例（避免重蹈）

| 报错 | 原因 | 修法 |
|---|---|---|
| `Invalid MTTFD value: -1` / `lower than or equal to 3` | 块的 mttfd 非法 | 机电件给 B10d+nop 让它算，或直接给 >3 的值 |
| `Invalid B10D value: -1` | 电子件 b10d 为空 | 显式写 `b10d=0` |
| `The attribute 'pl' is not allowed`（1866） | 给 componentops 写了 pl | 改用 `plsubitemscal` / `pldirectcal` |
| `The current configuration does not allow to calculate the PFH value using the standard` | 类别与 DCavg/MTTFd 不匹配 | 单器件子系统用 `pldet=detDirect`；Cat 4 要求 DCavg 高，DC 只有 Low 时要降到 Cat 3 |
| 生成的 SF 只有 `PL=a` | 沿用了 SB 的模板 `pfh` 缓存 | 打开后在界面里改一下参数触发重算，或直接在 `plsubitemscal` 里写正确值 |
