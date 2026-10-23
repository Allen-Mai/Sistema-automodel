# SISTEMA 静态 UI 地图（由 REA 提取）

- 可执行文件：`C:\Program Files (x86)\SISTEMA 3.0.4\SISTEMA.exe`
- SHA-256：`809c99903d39814ed6ebecca4257e69067acdc948f0d1e66a1894c7436599f9c`
- 提取方式：rea（REA：`C:\Users\admin\AppData\Local\Programs\node24\node.exe C:\Users\admin\AppData\Local\Programs\node24\node_modules\rea-agents\scripts\rea.mjs`）
- 生成时间（UTC）：2026-10-23T15:58:02+00:00
- 解析成功的窗体：**93**

本文件由 `tools/sistema/rea_ui_map.py` 自动生成，不要手工编辑。

> 定位约定：Delphi 按 DFM 顺序创建子窗口，Windows 按创建顺序枚举子窗口；
> 且 DFM 里每个控件都带父容器名与精确 Left/Top。
> 因此运行时 hwnd 可以用「父容器 + 类名 + 坐标 + 同类序数」反查到 DFM 组件名，
> 这是替代坐标点击、也替代截图判读的定位方式。

## TFormCCFMeasure

标题：`CCF-Maßnahme`

可寻址窗口类：`TAction`×2, `TActionList`×1, `TBitBtn`×2, `TIFALabeledAdvEditEx`×1, `TLabeledEditEx`×2, `TLabeledMemoEx`×1, `TPanel`×6

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 4 | `TBitBtn` | `BBOk` | Ok | `PanelBBOK` | 4,6 |
| 6 | `TBitBtn` | `BBCancel` | Abbrechen | `PanelBBCancel` | 4,6 |
| 9 | `TLabeledEditEx` | `LEExHeading` |  | `PanelCenter` | 150,31 |
| 10 | `TLabeledEditEx` | `LEExNumber` |  | `PanelCenter` | 150,6 |
| 11 | `TIFALabeledAdvEditEx` | `LEExScore` |  | `PanelCenter` | 150,235 |
| 12 | `TLabeledMemoEx` | `LMExDescription` |  | `PanelCenter` | 150,56 |

## TFormChannel

标题：`Kanal`

可寻址窗口类：`TGroupBox`×2, `TIFALabeledAdvEditEx`×2, `TImage`×2, `TLabel`×2, `TPanel`×4, `TScrollBox`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 5 | `TIFALabeledAdvEditEx` | `LEExMTTFd` |  | `GBMTTFd` | 200,16 |
| 6 | `TIFALabeledAdvEditEx` | `LEExMTTFdLevel` |  | `GBMTTFd` | 520,16 |
| 12 | `TLabel` | `LabChannel` | Kanal | `PanelTop` | 88,6 |
| 13 | `TLabel` | `LabTestChannel` | Testkanal | `PanelTop` | 88,6 |

## TFormChannelManager

标题：`Kanäle`

可寻址窗口类：`TAdvSplitter`×2, `TGroupBox`×3, `TIFABitBtn`×1, `TIFALabeledAdvEditEx`×6, `TPanel`×13, `TScrollBox`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 8 | `TIFALabeledAdvEditEx` | `LEExMTTFdCH1` |  | `PanelMTTFdCH1` | 200,6 |
| 9 | `TIFALabeledAdvEditEx` | `LEExMTTFdLevelCH1` |  | `PanelMTTFdCH1` | 520,6 |
| 16 | `TIFALabeledAdvEditEx` | `LEExMTTFdCHTest` |  | `PanelMTTFdCHTest` | 200,6 |
| 17 | `TIFALabeledAdvEditEx` | `LEExMTTFdLevelCHTest` |  | `PanelMTTFdCHTest` | 520,6 |
| 20 | `TIFABitBtn` | `BtnSwitchCH` | Inhalte Tauschen | `PanelSwitchBtn` | 24,6 |
| 24 | `TIFALabeledAdvEditEx` | `LEExMTTFdCH2` |  | `PanelMTTFdCH2` | 200,6 |
| 25 | `TIFALabeledAdvEditEx` | `LEExMTTFdLevelCH2` |  | `PanelMTTFdCH2` | 520,6 |

## TFormComponent

标题：`Subsystem`

可寻址窗口类：`TAdvGroupBox`×2, `TAdvOfficeCheckBox`×4, `TAdvPageControl`×1, `TAdvPanel`×1, `TAdvScrollBox`×7, `TAdvTabSheet`×7, `TBevel`×1, `TGroupBox`×14, `THTMLCheckBox`×3, `TIFABitBtn`×20, `TIFACheckBox`×1, `TIFAComboBox`×1, `TIFAHTMLCheckList`×2, `TIFAHintPanel`×4, `TIFALabel`×2, `TIFALabeledAdvEditEx`×18, `TImage`×3, `TLabel`×7, `TLabeledComboBoxEx`×3, `TLabeledComboBoxSSM`×1, `TLabeledEditEx`×20, `TLabeledMemoEx`×13, `TLabeledPanelSSM`×1, `TPanel`×49, `TRadioButton`×10

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 7 | `TLabeledEditEx` | `LEExName` |  | `PanelDocDescription` | 176,4 |
| 8 | `TLabeledEditEx` | `LEExDeviceEquipmentID` |  | `PanelDocDescription` | 176,31 |
| 9 | `TLabeledEditEx` | `LEEXDeviceInventoryNo` |  | `PanelDocDescription` | 176,58 |
| 13 | `TLabeledEditEx` | `LEExDeviceID` |  | `GBDocDetails` | 176,31 |
| 14 | `TLabeledEditEx` | `LEExDevicePartNo` |  | `GBDocDetails` | 176,85 |
| 15 | `TLabeledEditEx` | `LEExDeviceRevisionNo` |  | `GBDocDetails` | 176,112 |
| 16 | `TLabeledEditEx` | `LEExManufacturer` |  | `GBDocDetails` | 176,4 |
| 17 | `TLabeledMemoEx` | `LMEXDeviceUseCase` |  | `GBDocDetails` | 176,168 |
| 18 | `TLabeledMemoEx` | `LMExDeviceUseCaseDocumentation` |  | `GBDocDetails` | 176,222 |
| 19 | `TLabeledEditEx` | `LEExDeviceGroup` |  | `GBDocDetails` | 176,58 |
| 21 | `TAdvOfficeCheckBox` | `CB4_FncTypes` | CB4_FncTypes | `PanelFncTypesCB` | 300,0 |
| 22 | `TAdvOfficeCheckBox` | `CB1_FncTypes` | CB1_FncTypes | `PanelFncTypesCB` | 0,0 |
| 23 | `TAdvOfficeCheckBox` | `CB2_FncTypes` | CB2_FncTypes | `PanelFncTypesCB` | 100,0 |
| 24 | `TAdvOfficeCheckBox` | `CB3_FncTypes` | CB3_FncTypes | `PanelFncTypesCB` | 200,0 |
| 26 | `TLabeledMemoEx` | `LMExDescription` |  | `PanelDocDocument` | 176,5 |
| 27 | `TIFABitBtn` | `BBBrowseDocumentFile` | ... | `PanelDocDocument` | 682,672 |
| 28 | `TIFABitBtn` | `BBOpenDocumentFile` | Öffnen | `PanelDocDocument` | 709,671 |
| 29 | `TLabeledEditEx` | `LEEXDocumentFile` |  | `PanelDocDocument` | 176,671 |
| 36 | `TLabeledEditEx` | `LEExPLDirect` |  | `PanelPLItemsDirect` | 200,74 |
| 37 | `TLabeledComboBoxEx` | `CBExPLSILDirect` |  | `PanelPLItemsDirect` | 200,34 |
| 38 | `THTMLCheckBox` | `CBFaultExclusionPLDirect` | Fehlerausschluss | `PanelPLItemsDirect` | 566,34 |
| 39 | `TIFALabeledAdvEditEx` | `LEExPFHDirect` |  | `PanelPLItemsDirect` | 426,34 |
| 40 | `THTMLCheckBox` | `CBPFHBindingDirect` | test | `PanelPLItemsDirect` | 363,4 |
| 42 | `TLabeledMemoEx` | `LMExDocumentationPLDirect` |  | `PanelPLDirectDoc` | 200,6 |
| 43 | `TLabeledEditEx` | `LEEXDocumentPLDirect` |  | `PanelPLDirectDoc` | 200,95 |
| 44 | `TIFABitBtn` | `BBBrowseDocumentPLDirect` | ... | `PanelPLDirectDoc` | 680,95 |
| 45 | `TIFABitBtn` | `BBOpenDocumentPLDirect` | Öffnen | `PanelPLDirectDoc` | 707,95 |
| 48 | `TRadioButton` | `RBPLDetDirect` | PL bzw. PFH-Wert direkt angeben (Hersteller garantiert die Erfüllung der Anforderungen) | `PanelChoicePLTop` | 0,0 |
| 49 | `TRadioButton` | `RBPLDetSubItems` | PL bzw. PFH-Wert aus Kategorie, MTTFd und DCavg ermitteln | `PanelChoicePLTop` | 0,40 |
| 50 | `TRadioButton` | `RBPLDetSubItemsSimple` | PL bzw. PFH-Wert aus Kategorie,  DCavg ermitteln (Vereinfachtes Verfahren) | `PanelChoicePLTop` | 0,60 |
| 51 | `TRadioButton` | `RBPLDetSILDirect` | SIL bzw. PFH-Wert direkt angeben  (Hersteller garantiert die Erfüllung der Anforderungen) | `PanelChoicePLTop` | 0,20 |
| 57 | `TIFALabeledAdvEditEx` | `LEExPFHSubItems` |  | `Panel_SubItems_PL` | 536,2 |
| 58 | `TLabeledEditEx` | `LEExPLSubItems` |  | `Panel_SubItems_PL` | 200,2 |
| 60 | `TLabeledMemoEx` | `LMExDocumentationPLSubItems` |  | `Panel_SubItems_Doc` | 200,2 |
| 61 | `TLabeledEditEx` | `LEEXDocumentPLSubItems` |  | `Panel_SubItems_Doc` | 200,82 |
| 62 | `TIFABitBtn` | `BBBrowseDocumentPLSubitems` | ... | `Panel_SubItems_Doc` | 680,82 |
| 63 | `TIFABitBtn` | `BBOpenDocumentPLSubitems` | Öffnen | `Panel_SubItems_Doc` | 707,82 |
| 71 | `TLabeledComboBoxEx` | `CBExPLQualitativeAspects` | '-' bedeute, der Performance Level ist kleiner PLa  / 'a' - 'e' steht für  Performance Lev | `Panel_QuatitativeAspects_Choice` | 200,6 |
| 72 | `TLabeledMemoEx` | `LMExPLDocQuatitativeAspects` |  | `Panel_QuatitativeAspects_Choice` | 200,42 |
| 73 | `TIFABitBtn` | `BBBrowseDocumentFileQualitativeAspects` | ... | `Panel_QuatitativeAspects_Choice` | 680,108 |
| 74 | `TLabeledEditEx` | `LEEXDocumentFileQualitativeAspects` |  | `Panel_QuatitativeAspects_Choice` | 200,108 |
| 75 | `TIFABitBtn` | `BBOpenDocumentFileQualitativeAspects` | Öffnen | `Panel_QuatitativeAspects_Choice` | 708,108 |
| 78 | `TLabel` | `Lab20aPldirect` | Als Berechnungsgrundlage verwendet das Programm immer 20 a. | `GBMissionTimePLDirect` | 8,68 |
| 79 | `TIFALabeledAdvEditEx` | `LEExMissionTimePLDirect` |  | `GBMissionTimePLDirect` | 200,24 |
| 80 | `TIFALabeledAdvEditEx` | `LEExMinMissionTimePLdirect` |  | `GBMissionTimePLDirect` | 538,24 |
| 84 | `TLabeledComboBoxEx` | `CBExPLEMI` | Pfade zur Umsetzung der Maßnahmen für die elektromagnetische Störfestigkeit (EMI) eines SR | `Panel_EMI_DetChoice` | 200,6 |
| 85 | `TLabeledMemoEx` | `LMExPLDocEMI` |  | `Panel_EMI_DetChoice` | 200,42 |
| 86 | `TIFABitBtn` | `BBBrowseDocumentFileEMI` | ... | `Panel_EMI_DetChoice` | 680,108 |
| 87 | `TIFABitBtn` | `BBOpenDocumentFileEMI` | Öffnen | `Panel_EMI_DetChoice` | 708,108 |
| 88 | `TLabeledEditEx` | `LEEXDocumentFileEMI` |  | `Panel_EMI_DetChoice` | 200,108 |
| 97 | `TIFAComboBox` | `CBCat` |  | `PanelCatChoice` | 5,5 |
| 101 | `TLabel` | `LabCatReq` | Der Hersteller des Bauteils garantiert die Erfüllung der Anforderungen. | `PanelCatReqManufactor` | 10,8 |
| 102 | `TLabel` | `LabCatConditionsCheck` |  | `PanelCatReqManufactor` | 10,34 |
| 109 | `TLabeledMemoEx` | `LMExCatDoc` |  | `PanelCatDoc` | 176,0 |
| 111 | `TLabeledMemoEx` | `LMExCatStandard` |  | `PanelCatStandart` | 176,6 |
| 112 | `TLabeledEditEx` | `LEEXCatStandardFile` |  | `PanelCatStandart` | 176,86 |
| 113 | `TIFABitBtn` | `BBOpenStandardFileCat` | Öffnen | `PanelCatStandart` | 696,86 |
| 114 | `TIFABitBtn` | `BBBrowseStandardFileCat` | ... | `PanelCatStandart` | 669,87 |
| 120 | `TLabel` | `RBMTTFdDetDirect_HintLabel` | _Dummy for the disable hint | `PanelChoiceMTTFdLeft` | 350,20 |
| 121 | `TRadioButton` | `RBMTTFdDetDirect` | MTTFd-Wert direkt angeben | `PanelChoiceMTTFdLeft` | 0,20 |
| 122 | `TRadioButton` | `RBMTTFdDetSubItems` | MTTFd-Wert aus Blöcken ermitteln | `PanelChoiceMTTFdLeft` | 0,0 |
| 125 | `THTMLCheckBox` | `CBFaultExclusion` | Fehlerausschluss | `GBMTTFdDetDirect` | 180,43 |
| 126 | `TIFALabeledAdvEditEx` | `LEExMTTFd2` |  | `GBMTTFdDetDirect` | 180,16 |
| 127 | `TIFALabeledAdvEditEx` | `LEExMTTFdLevel2` |  | `GBMTTFdDetDirect` | 520,16 |
| 128 | `TLabeledMemoEx` | `LMExMTTFdDoc` |  | `GBMTTFdDetDirect` | 180,70 |
| 129 | `TLabeledEditEx` | `LEEXDocumentFileMTTFd` |  | `GBMTTFdDetDirect` | 180,115 |
| 130 | `TIFABitBtn` | `BBBrowseDocumentFileMTTFd` | ... | `GBMTTFdDetDirect` | 670,115 |
| 131 | `TIFABitBtn` | `BBOpenDocumentFileMTTFd` | Öffnen | `GBMTTFdDetDirect` | 697,115 |
| 134 | `TIFALabeledAdvEditEx` | `LEExMTTFd1` |  | `GBMTTFdDetSubItems` | 180,16 |
| 135 | `TIFALabeledAdvEditEx` | `LEExMTTFdLevel1` |  | `GBMTTFdDetSubItems` | 520,16 |
| 138 | `TLabel` | `Lab20a` | Als Berechnungsgrundlage verwendet das Programm immer 20 a. | `GBMissionTime` | 8,60 |
| 139 | `TIFALabeledAdvEditEx` | `LEExMissionTime` |  | `GBMissionTime` | 180,24 |
| 140 | `TIFALabeledAdvEditEx` | `LEExMinMissionTime` |  | `GBMissionTime` | 520,24 |
| 147 | `TLabel` | `RBDCavgDetDirect_HintLabel` | _Dummy for the disable hint | `PanelChoiceDCavgLeft` | 358,20 |
| 148 | `TRadioButton` | `RBDCavgDetDirect` | DCavg-Wert direkt angeben | `PanelChoiceDCavgLeft` | 0,20 |
| 149 | `TRadioButton` | `RBDCavgDetSubItems` | DCavg-Wert aus Blöcken ermitteln | `PanelChoiceDCavgLeft` | 0,0 |
| 152 | `TIFALabeledAdvEditEx` | `LEExDCavg1` |  | `GBDCavgDetSubItems` | 196,16 |
| 153 | `TIFALabeledAdvEditEx` | `LEExDCavgLevel1` |  | `GBDCavgDetSubItems` | 520,16 |
| 156 | `TIFALabeledAdvEditEx` | `LEExDCavg2` |  | `GBDCavgDetDirect` | 196,16 |
| 157 | `TIFALabeledAdvEditEx` | `LEExDCavgLevel2` |  | `GBDCavgDetDirect` | 520,16 |
| 158 | `TLabeledMemoEx` | `LMExDCavgDoc` |  | `GBDCavgDetDirect` | 196,43 |
| 159 | `TLabeledEditEx` | `LEEXDocumentFileDCavg` |  | `GBDCavgDetDirect` | 196,144 |
| 160 | `TIFABitBtn` | `BBBrowseDocumentFileDCavg` | ... | `GBDCavgDetDirect` | 668,144 |
| 161 | `TIFABitBtn` | `BBOpenDocumentFileDCavg` | Öffnen | `GBDCavgDetDirect` | 695,144 |
| 168 | `TRadioButton` | `RBCCFDetDirect` | Direkte CCF-Bewertung | `PanelChoiceCCFLeft` | 0,20 |
| 169 | `TRadioButton` | `RBCCFDetMeasures` | CCF-Bewertung durch Angabe der angewendeten Maßnahmen | `PanelChoiceCCFLeft` | 0,0 |
| 174 | `TLabeledMemoEx` | `LMExCCFMeasureDoc` |  | `PanelCCFDetMeasure` | 178,6 |
| 175 | `TIFABitBtn` | `BBBrowseMeasureDocumentFileCCF` | ... | `PanelCCFDetMeasure` | 679,542 |
| 176 | `TLabeledEditEx` | `LEEXCCFMeasureDocumentFile` |  | `PanelCCFDetMeasure` | 177,542 |
| 177 | `TIFABitBtn` | `BBOpenMeasureDocumentFileCCF` | Öffnen | `PanelCCFDetMeasure` | 707,542 |
| 179 | `TIFALabeledAdvEditEx` | `LEExCCFReq1` |  | `PannelCCFState` | 520,0 |
| 180 | `TIFALabeledAdvEditEx` | `LEExCCFScore1` |  | `PannelCCFState` | 178,0 |
| 183 | `TIFALabeledAdvEditEx` | `LEExCCFScore2` |  | `GBCCFDetDirect` | 180,14 |
| 184 | `TIFALabeledAdvEditEx` | `LEExCCFReq2` |  | `GBCCFDetDirect` | 520,14 |
| 185 | `TLabeledMemoEx` | `LMExCCFDirectDoc` |  | `GBCCFDetDirect` | 180,41 |
| 186 | `TLabeledEditEx` | `LEEXCCFDirectDocumentFile` |  | `GBCCFDetDirect` | 180,105 |
| 187 | `TIFABitBtn` | `BBBrowseDirectDocumentFileCCF` | ... | `GBCCFDetDirect` | 682,105 |
| 188 | `TIFABitBtn` | `BBOpenDirectDocumentFileCCF` | Öffnen | `GBCCFDetDirect` | 709,105 |
| 195 | `TLabel` | `LabComponent` | Subsystem | `PanelTop` | 88,6 |

## TFormConfig

标题：`Optionen`

可寻址窗口类：`TIFABitBtn`×3, `TListBox`×1, `TPanel`×4, `TScrollBox`×1, `TSplitter`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 7 | `TIFABitBtn` | `BBOk` | Ok | `PanelButtons` | 8,70 |
| 8 | `TIFABitBtn` | `BBAccept` | Uebernehmen | `PanelButtons` | 8,8 |
| 9 | `TIFABitBtn` | `BBCancel` | Abbrechen | `PanelButtons` | 8,39 |

## TFormConfigCommon

可寻址窗口类：`TCheckBox`×9, `TColumnComboBox`×2, `TComboBox`×1, `TGroupBox`×3, `TLabel`×1, `TLabeledEditSSM`×1, `TPanel`×19, `TValueListEditor`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 32 | `TLabel` | `LabRound` | Auf wieviel Stellen hinter dem Komma soll die Anzeige gerundet werden? | `PanelText` | 5,5 |

## TFormConfigContext

可寻址窗口类：`TCheckBox`×14, `TGroupBox`×4, `TImage`×4, `TPanel`×12

## TFormConfigExpert

可寻址窗口类：`TCheckBox`×10, `TLabeledEditSSM`×1, `TPanel`×12

## TFormConfigView

可寻址窗口类：`TCheckBox`×10, `TIFALabeledAdvComboBox`×4, `TLabeledEditSSM`×1, `TPanel`×15

## TFormContext

可寻址窗口类：（无）

## TFormDCMeasureDevice

标题：`DC-Maßnahme`

可寻址窗口类：`TAction`×3, `TActionList`×1, `TIFABitBtn`×1, `TIFALabel`×1, `TImageList`×1, `TLabel`×1, `TLabeledEditEx`×5, `TLabeledMemoEx`×2, `TPanel`×7

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 3 | `TLabel` | `LabInsuffPLs` | Diese Massnahme allein ist nicht ausreichend für die required Perfomance Levels: | `PanelBottom` | 322,137 |
| 5 | `TLabeledMemoEx` | `LMExDependency` |  | `PanelBottom` | 328,24 |
| 6 | `TLabeledEditEx` | `LEExDC` |  | `PanelBottom` | 185,78 |
| 7 | `TLabeledEditEx` | `LEExDCLevel` |  | `PanelBottom` | 185,105 |
| 8 | `TLabeledEditEx` | `LEExDCMax` |  | `PanelBottom` | 185,51 |
| 9 | `TLabeledEditEx` | `LEEXDCMin` |  | `PanelBottom` | 185,24 |
| 14 | `TLabeledMemoEx` | `LMExDescription` |  | `PanelTop` | 185,33 |
| 15 | `TLabeledEditEx` | `LEExHeading` |  | `PanelTop` | 185,5 |
| 17 | `TIFABitBtn` | `BBLib` | Bibliothek | `PanelBibEdit` | 8,5 |

## TFormInfoMessage

可寻址窗口类：`TBitBtn`×1, `TIFALabel`×1, `TIFALabeledMemo`×1, `TImageList`×1, `TPanel`×2

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 2 | `TBitBtn` | `BBOk` | Ok | `PanelBottom` | 6,3 |

## TFormLib

标题：`SISTEMA - Bibliothek`

可寻址窗口类：`TAction`×43, `TActionManager`×1, `TActionToolBar`×2, `TAdvMainMenu`×1, `TAdvMenuOfficeStyler`×1, `TAdvPanel`×7, `TAdvSplitter`×4, `TBevel`×1, `TIFABitBtn`×4, `TIFAPopupMenu`×1, `TImageList`×1, `TMemo`×1, `TMenuItem`×71, `TPanel`×6, `TPopupMenu`×2, `TStatusBar`×1, `TtiVTTreeView`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 13 | `TIFABitBtn` | `BitBtn3` | Aenderungen uebernehmen | `PanelTVBtn` | 7,4 |
| 14 | `TIFABitBtn` | `BitBtn1` | Auswahl laden | `PanelTVBtn` | 7,35 |
| 15 | `TIFABitBtn` | `BitBtn2` | Schliessen | `PanelTVBtn` | 7,103 |
| 16 | `TIFABitBtn` | `BitBtn4` | Laden && Schliessen | `PanelTVBtn` | 7,66 |
| 74 | `TMenuItem` | `ExpandAll1` |  | `PMTV` | 0,0 |
| 75 | `TMenuItem` | `Einklappen1` |  | `PMTV` | 0,0 |
| 76 | `TMenuItem` | `N13` | - | `PMTV` | 0,0 |
| 77 | `TMenuItem` | `Hinzufgen1` |  | `PMTV` | 0,0 |
| 78 | `TMenuItem` | `AusVDMABibliothekladen1` |  | `PMTV` | 0,0 |
| 79 | `TMenuItem` | `Lschen1` |  | `PMTV` | 0,0 |
| 80 | `TMenuItem` | `Auswahlladen1` |  | `PMTV` | 0,0 |
| 81 | `TMenuItem` | `Bibliothek1` |  | `PMTV` | 0,0 |
| 82 | `TMenuItem` | `BaumansichtDrucken1` |  | `PMTV` | 0,0 |
| 83 | `TMenuItem` | `N2` | - | `PMTV` | 0,0 |
| 84 | `TMenuItem` | `Ausschneiden1` |  | `PMTV` | 0,0 |
| 85 | `TMenuItem` | `Kopieren1` |  | `PMTV` | 0,0 |
| 86 | `TMenuItem` | `Einfgen1` |  | `PMTV` | 0,0 |
| 87 | `TMenuItem` | `N5` | - | `PMTV` | 0,0 |
| 88 | `TMenuItem` | `Einsnachobenverschieben1` |  | `PMTV` | 0,0 |
| 89 | `TMenuItem` | `Einsnachuntenverschieben1` |  | `PMTV` | 0,0 |
| 90 | `TMenuItem` | `SortierenAZ1` |  | `PMTV` | 0,0 |
| 91 | `TMenuItem` | `SortierenZA1` |  | `PMTV` | 0,0 |
| 92 | `TMenuItem` | `N15` | - | `PMTV` | 0,0 |
| 93 | `TMenuItem` | `Filtern1` |  | `PMTV` | 0,0 |
| 94 | `TMenuItem` | `Suchen1` |  | `PMTV` | 0,0 |
| 96 | `TMenuItem` | `Hierherverschieben1` |  | `PMTVDrop` | 0,0 |
| 97 | `TMenuItem` | `Hierherkopieren1` |  | `PMTVDrop` | 0,0 |
| 98 | `TMenuItem` | `N1` | - | `PMTVDrop` | 0,0 |
| 99 | `TMenuItem` | `Abbrechen1` |  | `PMTVDrop` | 0,0 |
| 101 | `TMenuItem` | `NeueBibliothekerstellen1` |  | `PMLib` | 0,0 |
| 102 | `TMenuItem` | `N3` | - | `PMLib` | 0,0 |
| 103 | `TMenuItem` | `Bibliothekhinzufgen1` |  | `PMLib` | 0,0 |
| 104 | `TMenuItem` | `Netzwerkbibliothekhinzufgen1` |  | `PMLib` | 0,0 |
| 105 | `TMenuItem` | `Bibliothekentfernen1` |  | `PMLib` | 0,0 |
| 106 | `TMenuItem` | `N4` | - | `PMLib` | 0,0 |
| 107 | `TMenuItem` | `Hilfe1` |  | `PMLib` | 0,0 |
| 108 | `TMenuItem` | `N9` | - | `PMLib` | 0,0 |
| 109 | `TMenuItem` | `ErneutausDatenbankladen1` |  | `PMLib` | 0,0 |
| 110 | `TMenuItem` | `Info1` |  | `PMLib` | 0,0 |
| 111 | `TMenuItem` | `N16` | - | `PMLib` | 0,0 |
| 112 | `TMenuItem` | `nderungenbernehmen2` |  | `PMLib` | 0,0 |
| 114 | `TMenuItem` | `MMFile` | Datei | `MM` | 0,0 |
| 115 | `TMenuItem` | `Bibliothekhinzufgen2` |  | `MMFile` | 0,0 |
| 116 | `TMenuItem` | `N6` | - | `MMFile` | 0,0 |
| 117 | `TMenuItem` | `Bibliothekhinzufgen3` |  | `MMFile` | 0,0 |
| 118 | `TMenuItem` | `Netzwerkbibliothekhinzufgen2` |  | `MMFile` | 0,0 |
| 119 | `TMenuItem` | `Bibliothekentfernen2` |  | `MMFile` | 0,0 |
| 120 | `TMenuItem` | `N7` | - | `MMFile` | 0,0 |
| 121 | `TMenuItem` | `Bibliothekschtzen1` |  | `MMFile` | 0,0 |
| 122 | `TMenuItem` | `N8` | - | `MMFile` | 0,0 |
| 123 | `TMenuItem` | `Info2` |  | `MMFile` | 0,0 |
| 124 | `TMenuItem` | `N12` | - | `MMFile` | 0,0 |
| 125 | `TMenuItem` | `Abbrechen2` |  | `MMFile` | 0,0 |
| 126 | `TMenuItem` | `MMEdit` | Bearbeiten | `MM` | 0,0 |
| 127 | `TMenuItem` | `Hinzufgen2` |  | `MMEdit` | 0,0 |
| 128 | `TMenuItem` | `Lschen2` |  | `MMEdit` | 0,0 |
| 129 | `TMenuItem` | `N10` | - | `MMEdit` | 0,0 |
| 130 | `TMenuItem` | `nderungenbernehmen1` |  | `MMEdit` | 0,0 |
| 131 | `TMenuItem` | `N11` | - | `MMEdit` | 0,0 |
| 132 | `TMenuItem` | `VDMABibliothek1` |  | `MMEdit` | 0,0 |
| 133 | `TMenuItem` | `N17` | - | `MMEdit` | 0,0 |
| 134 | `TMenuItem` | `BibliothekMigrationToolffnen1` |  | `MMEdit` | 0,0 |
| 135 | `TMenuItem` | `N18` | - | `MMEdit` | 0,0 |
| 136 | `TMenuItem` | `Exportieren1` |  | `MMEdit` | 0,0 |
| 137 | `TMenuItem` | `Importieren1` |  | `MMEdit` | 0,0 |
| 138 | `TMenuItem` | `MMView` | Ansicht | `MM` | 0,0 |
| 139 | `TMenuItem` | `Kontext1` |  | `MMView` | 0,0 |
| 140 | `TMenuItem` | `Meldungen1` |  | `MMView` | 0,0 |
| 141 | `TMenuItem` | `InfozurBibliothek1` |  | `MMView` | 0,0 |
| 142 | `TMenuItem` | `N14` | - | `MMView` | 0,0 |
| 143 | `TMenuItem` | `Aktualisieren1` |  | `MMView` | 0,0 |
| 144 | `TMenuItem` | `MMHelp` | Hilfe | `MM` | 0,0 |
| 145 | `TMenuItem` | `Hilfe2` |  | `MMHelp` | 0,0 |
| 146 | `TMenuItem` | `Wasistdas1` |  | `MMHelp` | 0,0 |
| 147 | `TMenuItem` | `HerstellerBibliotheken1` |  | `MMHelp` | 0,0 |

## TFormLibCCFMeasures

标题：`Bibliothek CCF-Maßnahmen`

可寻址窗口类：`TAction`×6, `TActionManager`×1, `TActionToolBar`×1, `TBevel`×1, `TIFABitBtn`×3, `TIFAMarkedStringGrid`×1, `TImage`×1, `TImageList`×1, `TLabeledEditEx`×1, `TMenuItem`×3, `TPanel`×5, `TPopupMenu`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 4 | `TIFABitBtn` | `BBCancel` | Abbrechen | `PanelBottom` | 600,6 |
| 5 | `TIFABitBtn` | `BBLoad` | Auswahl laden | `PanelBottom` | 778,6 |
| 6 | `TIFABitBtn` | `BBSetChanges` | Aenderungen uebernehmen | `PanelBottom` | 384,6 |
| 9 | `TLabeledEditEx` | `LEExLib` |  | `PanelTop` | 90,12 |
| 16 | `TMenuItem` | `MenuItem1` |  | `PM` | 0,0 |
| 17 | `TMenuItem` | `MenuItem2` |  | `PM` | 0,0 |
| 18 | `TMenuItem` | `MenuItem3` |  | `PM` | 0,0 |

## TFormLibDCMeasures

标题：`Bibliothek DC-Maßnahmen`

可寻址窗口类：`TAction`×6, `TActionManager`×1, `TActionToolBar`×1, `TBevel`×1, `TIFABitBtn`×3, `TIFAMarkedStringGrid`×1, `TImage`×1, `TImageList`×1, `TLabeledEditEx`×1, `TMenuItem`×3, `TPanel`×5, `TPopupMenu`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 4 | `TLabeledEditEx` | `LEExLib` |  | `PanelTop` | 88,12 |
| 11 | `TIFABitBtn` | `BBCancel` | Abbrechen | `PanelBottom` | 257,6 |
| 12 | `TIFABitBtn` | `BBLoad` | Auswahl laden | `PanelBottom` | 453,6 |
| 13 | `TIFABitBtn` | `BBSetChanges` | Aenderungen uebernehmen | `PanelBottom` | 44,6 |
| 22 | `TMenuItem` | `MenuItem1` |  | `PM` | 0,0 |
| 23 | `TMenuItem` | `MenuItem2` |  | `PM` | 0,0 |
| 24 | `TMenuItem` | `MenuItem3` |  | `PM` | 0,0 |

## TFormLoadFile

可寻址窗口类：`TImage`×2, `TLabel`×1, `TPanel`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 4 | `TLabel` | `Label1` |  | `MainPanel` | 89,6 |

## TFormMain

标题：`SISTEMA`

可寻址窗口类：`TAction`×55, `TActionManager`×1, `TActionToolBar`×2, `TAdvFocusHelper`×1, `TAdvMainMenu`×1, `TAdvMenuOfficeStyler`×1, `TAdvPanel`×6, `TAdvSplitter`×4, `TIFAHint`×1, `TImageList`×2, `TMenuItem`×85, `TPanel`×4, `TPopupMenu`×2, `TRvCustomConnection`×9, `TRvProject`×1, `TRvRenderPDF`×1, `TRvSystem`×1, `TStatusBar`×1, `TtiVTTreeView`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 78 | `TMenuItem` | `ExpandAll1` |  | `PMTV` | 0,0 |
| 79 | `TMenuItem` | `EbeneEinklappen1` |  | `PMTV` | 0,0 |
| 80 | `TMenuItem` | `N14` | - | `PMTV` | 0,0 |
| 81 | `TMenuItem` | `Hinzufgen1` |  | `PMTV` | 0,0 |
| 82 | `TMenuItem` | `Lschen1` |  | `PMTV` | 0,0 |
| 83 | `TMenuItem` | `AusVDMABibliothekladen1` |  | `PMTV` | 0,0 |
| 84 | `TMenuItem` | `Bibliothek1` |  | `PMTV` | 0,0 |
| 85 | `TMenuItem` | `IndieBibliohtekkopieren1` |  | `PMTV` | 0,0 |
| 86 | `TMenuItem` | `N2` | - | `PMTV` | 0,0 |
| 87 | `TMenuItem` | `BaumansichtDrucken1` |  | `PMTV` | 0,0 |
| 88 | `TMenuItem` | `Ausschneiden1` |  | `PMTV` | 0,0 |
| 89 | `TMenuItem` | `Kopieren1` |  | `PMTV` | 0,0 |
| 90 | `TMenuItem` | `Einfgen1` |  | `PMTV` | 0,0 |
| 91 | `TMenuItem` | `N3` | - | `PMTV` | 0,0 |
| 92 | `TMenuItem` | `Einsnachobenverschieben1` |  | `PMTV` | 0,0 |
| 93 | `TMenuItem` | `Einsnachuntenverschieben1` |  | `PMTV` | 0,0 |
| 94 | `TMenuItem` | `SortierenAZ1` |  | `PMTV` | 0,0 |
| 95 | `TMenuItem` | `SortierenZA1` |  | `PMTV` | 0,0 |
| 96 | `TMenuItem` | `N16` | - | `PMTV` | 0,0 |
| 97 | `TMenuItem` | `Filtern1` |  | `PMTV` | 0,0 |
| 98 | `TMenuItem` | `Suchen1` |  | `PMTV` | 0,0 |
| 99 | `TMenuItem` | `N4` | - | `PMTV` | 0,0 |
| 100 | `TMenuItem` | `Schlieen1` |  | `PMTV` | 0,0 |
| 101 | `TMenuItem` | `Alleschlieen1` |  | `PMTV` | 0,0 |
| 103 | `TMenuItem` | `Hierherverschieben1` |  | `PMTVDrop` | 0,0 |
| 104 | `TMenuItem` | `Hierherkopieren1` |  | `PMTVDrop` | 0,0 |
| 105 | `TMenuItem` | `N1` | - | `PMTVDrop` | 0,0 |
| 106 | `TMenuItem` | `Abbrechen1` |  | `PMTVDrop` | 0,0 |
| 117 | `TMenuItem` | `MMFile` | Datei | `MM` | 0,0 |
| 118 | `TMenuItem` | `Neu1` |  | `MMFile` | 0,0 |
| 119 | `TMenuItem` | `Offnen1` |  | `MMFile` | 0,0 |
| 120 | `TMenuItem` | `N5` | - | `MMFile` | 0,0 |
| 121 | `TMenuItem` | `Speichern1` |  | `MMFile` | 0,0 |
| 122 | `TMenuItem` | `Speichernunter1` |  | `MMFile` | 0,0 |
| 123 | `TMenuItem` | `Projektschlieen1` |  | `MMFile` | 0,0 |
| 124 | `TMenuItem` | `Alleschlieen2` |  | `MMFile` | 0,0 |
| 125 | `TMenuItem` | `N7` | - | `MMFile` | 0,0 |
| 126 | `TMenuItem` | `ExportierenalsPDF1` |  | `MMFile` | 0,0 |
| 127 | `TMenuItem` | `Drucken1` |  | `MMFile` | 0,0 |
| 128 | `TMenuItem` | `RecentFilesStart` | - | `MMFile` | 0,0 |
| 129 | `TMenuItem` | `RecentFilesFinish` | - | `MMFile` | 0,0 |
| 130 | `TMenuItem` | `Beenden1` |  | `MMFile` | 0,0 |
| 131 | `TMenuItem` | `MMEdit` | Bearbeiten | `MM` | 0,0 |
| 132 | `TMenuItem` | `Ausschneiden2` |  | `MMEdit` | 0,0 |
| 133 | `TMenuItem` | `Kopieren2` |  | `MMEdit` | 0,0 |
| 134 | `TMenuItem` | `Einfgen2` |  | `MMEdit` | 0,0 |
| 135 | `TMenuItem` | `N8` | - | `MMEdit` | 0,0 |
| 136 | `TMenuItem` | `Neu2` |  | `MMEdit` | 0,0 |
| 137 | `TMenuItem` | `Lschen2` |  | `MMEdit` | 0,0 |
| 138 | `TMenuItem` | `AusBibliothekladen1` |  | `MMEdit` | 0,0 |
| 139 | `TMenuItem` | `IndieBibliohtekkopieren2` |  | `MMEdit` | 0,0 |
| 140 | `TMenuItem` | `N9` | - | `MMEdit` | 0,0 |
| 141 | `TMenuItem` | `Neu3` |  | `MMEdit` | 0,0 |
| 142 | `TMenuItem` | `VDMABibliothek1` |  | `MMEdit` | 0,0 |
| 143 | `TMenuItem` | `N10` | - | `MMEdit` | 0,0 |
| 144 | `TMenuItem` | `Spracheauswhlen1` |  | `MMEdit` | 0,0 |
| 145 | `TMenuItem` | `N11` | - | `MMEdit` | 0,0 |
| 146 | `TMenuItem` | `Optionen1` |  | `MMEdit` | 0,0 |
| 147 | `TMenuItem` | `MMView` | Ansicht | `MM` | 0,0 |
| 148 | `TMenuItem` | `Zusammenfassung1` |  | `MMView` | 0,0 |
| 149 | `TMenuItem` | `N12` | - | `MMView` | 0,0 |
| 150 | `TMenuItem` | `Meldungen1` |  | `MMView` | 0,0 |
| 151 | `TMenuItem` | `Kontext1` |  | `MMView` | 0,0 |
| 152 | `TMenuItem` | `Hilfe2` |  | `MMView` | 0,0 |
| 153 | `TMenuItem` | `N15` | - | `MMView` | 0,0 |
| 154 | `TMenuItem` | `Aktualisieren1` |  | `MMView` | 0,0 |
| 155 | `TMenuItem` | `MMHelp` | Hilfe | `MM` | 0,0 |
| 156 | `TMenuItem` | `Hilfe3` |  | `MMHelp` | 0,0 |
| 157 | `TMenuItem` | `Wasistdas1` |  | `MMHelp` | 0,0 |
| 158 | `TMenuItem` | `Wizard1` |  | `MMHelp` | 0,0 |
| 159 | `TMenuItem` | `N17` | - | `MMHelp` | 0,0 |
| 160 | `TMenuItem` | `ErsteSchritte1` |  | `MMHelp` | 0,0 |
| 161 | `TMenuItem` | `NeuerungenSISTEMA20Beta1` |  | `MMHelp` | 0,0 |
| 162 | `TMenuItem` | `Versionsberprfung1` |  | `MMHelp` | 0,0 |
| 163 | `TMenuItem` | `SISTEMAFehlerliste1` |  | `MMHelp` | 0,0 |
| 164 | `TMenuItem` | `SISTEMANewsletterRegistrierung1` |  | `MMHelp` | 0,0 |
| 165 | `TMenuItem` | `N18` | - | `MMHelp` | 0,0 |
| 166 | `TMenuItem` | `SISTEMAHompage1` |  | `MMHelp` | 0,0 |
| 167 | `TMenuItem` | `SISTEMAKochbuch1` |  | `MMHelp` | 0,0 |
| 168 | `TMenuItem` | `SISTEMAFAQPDF1` |  | `MMHelp` | 0,0 |
| 169 | `TMenuItem` | `IFA13849Portal1` |  | `MMHelp` | 0,0 |
| 170 | `TMenuItem` | `N13` | - | `MMHelp` | 0,0 |
| 171 | `TMenuItem` | `HerstellerBibliotheken1` |  | `MMHelp` | 0,0 |
| 172 | `TMenuItem` | `N19` | - | `MMHelp` | 0,0 |
| 173 | `TMenuItem` | `Info1` |  | `MMHelp` | 0,0 |

## TFormMessageHelperListUI

标题：`Meldungen`

可寻址窗口类：`TAction`×4, `TActionList`×1, `TAdvGlowButton`×1, `TIFAAdvListView`×1, `TImageList`×2, `TMenuItem`×4, `TPanel`×2, `TPopupMenu`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 6 | `TMenuItem` | `Bearbeiten1` |  | `PM` | 0,0 |
| 7 | `TMenuItem` | `Meldungbearbeiten1` |  | `PM` | 0,0 |
| 8 | `TMenuItem` | `ListederkommentierenMeldungenaktualisieren1` |  | `PM` | 0,0 |
| 9 | `TMenuItem` | `KommentarzurMeldungentfernen1` |  | `PM` | 0,0 |

## TFormMessageListUI

标题：`Meldungen`

可寻址窗口类：`TAction`×3, `TActionList`×1, `TIFAMarkedStringGrid`×1, `TMenuItem`×3, `TPopupMenu`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 3 | `TMenuItem` | `Auswhlen1` |  | `PM` | 0,0 |
| 4 | `TMenuItem` | `Bearbeiten1` |  | `PM` | 0,0 |
| 5 | `TMenuItem` | `Speicher1` |  | `PM` | 0,0 |

## TFormNop

标题：`Nop`

可寻址窗口类：`TBitBtn`×2, `TButton`×1, `TIFALabeledAdvEdit`×3, `TImage`×1, `TPanel`×5

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 10 | `TBitBtn` | `BBCancel` | Abbrechen | `PanelBtn` | 221,36 |
| 11 | `TBitBtn` | `BBOk` | Ok | `PanelBtn` | 326,36 |
| 12 | `TButton` | `BBLastValue` | Letzte Werte laden | `PanelBtn` | 221,0 |

## TFormProject

标题：`Projekt-Optionen`

可寻址窗口类：`TAdvPageControl`×1, `TAdvPanel`×3, `TAdvScrollBox`×2, `TAdvTabSheet`×2, `TBevel`×2, `TIFABitBtn`×6, `TIFAHintPanel`×1, `TImage`×2, `TLabel`×1, `TLabeledComboBoxEx`×1, `TLabeledEditEx`×14, `TLabeledMemoEx`×1, `TPanel`×5

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 7 | `TLabeledEditEx` | `LEExName` |  | `GBFileData` | 202,6 |
| 8 | `TLabeledEditEx` | `LEExFileName` |  | `GBFileData` | 202,33 |
| 9 | `TLabeledEditEx` | `LEExChecksum` |  | `GBFileData` | 202,60 |
| 10 | `TIFABitBtn` | `BBRefreshChecksum` |  | `GBFileData` | 561,60 |
| 11 | `TLabeledEditEx` | `LEExLastChange` |  | `GBFileData` | 202,87 |
| 12 | `TLabeledEditEx` | `LEExCreateDate` |  | `GBFileData` | 202,114 |
| 13 | `TLabeledEditEx` | `LEExStandardsFolder` |  | `GBFileData` | 202,141 |
| 14 | `TIFABitBtn` | `BBBrowseStandardsFolder` | ... | `GBFileData` | 562,141 |
| 15 | `TLabeledEditEx` | `LEExDocumentsFolder` |  | `GBFileData` | 202,168 |
| 16 | `TIFABitBtn` | `BBBrowseDocumentsFolder` | ... | `GBFileData` | 562,168 |
| 17 | `TIFABitBtn` | `BBResetCreateDate` | Erstellungsdatum der Projektdatei zurücksetzen… | `GBFileData` | 561,114 |
| 19 | `TLabeledComboBoxEx` | `LCBExStatus` |  | `GBDetails` | 202,8 |
| 20 | `TLabeledEditEx` | `LEExNumber` |  | `GBDetails` | 202,35 |
| 21 | `TLabeledEditEx` | `LEExVersion` |  | `GBDetails` | 202,62 |
| 22 | `TLabeledEditEx` | `LEExAuthor` |  | `GBDetails` | 202,89 |
| 23 | `TLabeledEditEx` | `LEExManager` |  | `GBDetails` | 202,116 |
| 24 | `TLabeledEditEx` | `LEExTester` |  | `GBDetails` | 202,143 |
| 26 | `TLabeledEditEx` | `LEExMachine` |  | `GBDocumentation` | 202,7 |
| 27 | `TLabeledMemoEx` | `LMExDocumentation` |  | `GBDocumentation` | 202,34 |
| 28 | `TLabeledEditEx` | `LEEXDocumentFile` |  | `GBDocumentation` | 202,73 |
| 29 | `TIFABitBtn` | `BBBrowseDocumentFile` | ... | `GBDocumentation` | 489,73 |
| 30 | `TIFABitBtn` | `BBOpenDocumentFile` | Öffnen | `GBDocumentation` | 513,73 |
| 41 | `TLabel` | `LabProject` | Projekt | `PanelTop` | 88,6 |

## TFormReport12

标题：`Report Preview`

可寻址窗口类：`TAction`×14, `TActionManager`×1, `TAdvMainMenu`×1, `TAdvMenuOfficeStyler`×1, `TEdit`×2, `TImageList`×1, `TLabel`×4, `TMenuItem`×21, `TOpenDialog`×1, `TPopupMenu`×1, `TSaveDialog`×1, `TScrollBox`×1, `TStatusBar`×1, `TTimer`×1, `TToolBar`×1, `TToolButton`×15

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 12 | `TLabel` | `Panel1` | Seite | `ToolBar1` | 169,0 |
| 14 | `TLabel` | `PageLabel` | von 3000 | `ToolBar1` | 266,0 |
| 20 | `TLabel` | `Panel3` | Zoom | `ToolBar1` | 437,0 |
| 22 | `TLabel` | `Panel2` |  % | `ToolBar1` | 529,0 |
| 26 | `TMenuItem` | `MMFile` | Datei | `MM` | 0,0 |
| 27 | `TMenuItem` | `Open1` |  | `MMFile` | 0,0 |
| 28 | `TMenuItem` | `SaveAs1` |  | `MMFile` | 0,0 |
| 29 | `TMenuItem` | `Print1` |  | `MMFile` | 0,0 |
| 30 | `TMenuItem` | `N1` | - | `MMFile` | 0,0 |
| 31 | `TMenuItem` | `Exit1` |  | `MMFile` | 0,0 |
| 32 | `TMenuItem` | `MMPage` | Seite | `MM` | 0,0 |
| 33 | `TMenuItem` | `First1` |  | `MMPage` | 0,0 |
| 34 | `TMenuItem` | `Previous1` |  | `MMPage` | 0,0 |
| 35 | `TMenuItem` | `Next1` |  | `MMPage` | 0,0 |
| 36 | `TMenuItem` | `Last1` |  | `MMPage` | 0,0 |
| 37 | `TMenuItem` | `N2` | - | `MMPage` | 0,0 |
| 38 | `TMenuItem` | `GotoPage1` |  | `MMPage` | 0,0 |
| 39 | `TMenuItem` | `MMZoom` | Zoom | `MM` | 0,0 |
| 40 | `TMenuItem` | `In1` |  | `MMZoom` | 0,0 |
| 41 | `TMenuItem` | `Out1` |  | `MMZoom` | 0,0 |
| 42 | `TMenuItem` | `N3` | - | `MMZoom` | 0,0 |
| 43 | `TMenuItem` | `Page2` |  | `MMZoom` | 0,0 |
| 44 | `TMenuItem` | `PageWidth1` |  | `MMZoom` | 0,0 |
| 46 | `TMenuItem` | `In2` |  | `PM` | 0,0 |
| 47 | `TMenuItem` | `Out2` |  | `PM` | 0,0 |

## TFormSettings

标题：`Settings`

可寻址窗口类：`TAdvEdit`×2, `TGroupBox`×2, `THTMLButton`×2, `THTMLCheckBox`×1, `TImageList`×2, `TPanel`×2

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 6 | `THTMLCheckBox` | `cbCreateDstFilesInSourceDirectory` | <FONT face="Arial" size="10">Creation of the destination files directly in the source dire | `GBFileSettings` | 14,69 |

## TFormSF

标题：`Sicherheitsfunktion-Optionen`

可寻址窗口类：`TAdvPageControl`×1, `TAdvScrollBox`×4, `TAdvTabSheet`×4, `TBevel`×2, `TGroupBox`×9, `TIFAAdvSplitter`×1, `TIFABitBtn`×10, `TIFALabel`×1, `TImage`×3, `TImageList`×1, `TLabel`×20, `TLabeledComboBoxEx`×3, `TLabeledEditEx`×14, `TLabeledMemoEx`×9, `TPanel`×33, `TRadioButton`×5, `TStaticText`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 6 | `TLabeledMemoEx` | `LMExTriggerEvent` |  | `PanelDocumentation` | 211,89 |
| 7 | `TLabeledMemoEx` | `LMExSafeState` |  | `PanelDocumentation` | 211,259 |
| 8 | `TLabeledMemoEx` | `LMExReaction` |  | `PanelDocumentation` | 211,174 |
| 9 | `TLabeledMemoEx` | `LMExDocumentation` |  | `PanelDocumentation` | 211,460 |
| 10 | `TLabeledEditEx` | `LEExName` |  | `PanelDocumentation` | 211,8 |
| 11 | `TLabeledEditEx` | `LEEXDocumentFile` |  | `PanelDocumentation` | 211,916 |
| 12 | `TLabeledComboBoxEx` | `LCBExSFType` |  | `PanelDocumentation` | 211,62 |
| 13 | `TIFABitBtn` | `BBOpenDocumentFile` | Öffnen | `PanelDocumentation` | 684,916 |
| 14 | `TIFABitBtn` | `BBBrowseDocumentFile` | ... | `PanelDocumentation` | 657,916 |
| 15 | `TLabeledEditEx` | `LEExRequestFrequency` |  | `PanelDocumentation` | 211,378 |
| 16 | `TLabeledEditEx` | `LEExResponseTime` |  | `PanelDocumentation` | 211,405 |
| 17 | `TLabeledEditEx` | `LEExPriority` |  | `PanelDocumentation` | 211,432 |
| 18 | `TLabeledEditEx` | `LEExSFK` |  | `PanelDocumentation` | 211,35 |
| 19 | `TLabeledEditEx` | `LEExOpMode` |  | `PanelDocumentation` | 211,351 |
| 20 | `TLabeledMemoEx` | `LMExInterfaces` |  | `PanelDocumentation` | 211,305 |
| 25 | `TRadioButton` | `RBPLrDetDirect` | PLr-Wert direkt angeben | `PanelChoicePLrLeft` | 0,0 |
| 26 | `TRadioButton` | `RBPLrDetGraph` | PLr-Wert aus Risikograph ermitteln | `PanelChoicePLrLeft` | 0,20 |
| 31 | `TIFABitBtn` | `BBBrowsePLrDocFile` | ... | `PanelPLrDirect` | 646,77 |
| 32 | `TIFABitBtn` | `BBBrowsePLrStandardFile` | ... | `PanelPLrDirect` | 645,201 |
| 33 | `TIFABitBtn` | `BBOpenPLrDocFile` | Öffnen | `PanelPLrDirect` | 674,77 |
| 34 | `TIFABitBtn` | `BBOpenPLrStandardFile` | Öffnen | `PanelPLrDirect` | 672,201 |
| 35 | `TLabeledComboBoxEx` | `LCBExPLr` |  | `PanelPLrDirect` | 220,0 |
| 36 | `TLabeledEditEx` | `LEEXPLrDocFile` |  | `PanelPLrDirect` | 220,77 |
| 37 | `TLabeledEditEx` | `LEEXPLrStandardFile` |  | `PanelPLrDirect` | 220,201 |
| 38 | `TLabeledMemoEx` | `LMExPLrStandard` |  | `PanelPLrDirect` | 220,113 |
| 39 | `TLabeledMemoEx` | `LMExPLrDoc` |  | `PanelPLrDirect` | 220,27 |
| 47 | `TLabel` | `LabP1Text` | Möglich unter bestimmten Bedingungen | `GBPossibility` | 80,24 |
| 48 | `TLabel` | `LabP2Text` | Kaum möglich | `GBPossibility` | 80,56 |
| 49 | `TLabel` | `LabP1` | P1 | `GBPossibility` | 48,24 |
| 50 | `TLabel` | `LabP2` | P2 | `GBPossibility` | 48,56 |
| 51 | `TLabel` | `LabP1Check` |  | `GBPossibility` | 16,24 |
| 52 | `TLabel` | `LabP2Check` |  | `GBPossibility` | 16,56 |
| 55 | `TLabel` | `LabS1Text` | Leichte (üblicherweise reversible) Verletzung | `GBSeverity` | 80,24 |
| 56 | `TLabel` | `LabS2Text` | Schwere (üblicherweise irreversible) Verletzung, einschließlich Tod | `GBSeverity` | 80,56 |
| 57 | `TLabel` | `LabS1` | S1 | `GBSeverity` | 48,24 |
| 58 | `TLabel` | `LabS2` | S2 | `GBSeverity` | 48,56 |
| 59 | `TLabel` | `LabS1Check` |  | `GBSeverity` | 16,24 |
| 60 | `TLabel` | `LabS2Check` |  | `GBSeverity` | 16,56 |
| 63 | `TLabel` | `LabF1Text` | Selten bis öfter und/oder kurze Dauer der Exposition | `GBFrequency` | 80,24 |
| 64 | `TLabel` | `LabF2Text` | Häufig bis dauernd und/oder lange Dauer der Exposition | `GBFrequency` | 80,56 |
| 65 | `TLabel` | `LabF1` | F1 | `GBFrequency` | 48,24 |
| 66 | `TLabel` | `LabF2` | F2 | `GBFrequency` | 48,56 |
| 67 | `TLabel` | `LabF1Check` |  | `GBFrequency` | 16,24 |
| 68 | `TLabel` | `LabF2Check` |  | `GBFrequency` | 16,56 |
| 70 | `TLabeledEditEx` | `LEEXRiskGraphPLr` |  | `PanelRiskGraphPLr` | 218,8 |
| 74 | `TRadioButton` | `RBWParUnknown` | nicht bekannt | `PanelWRBLeft` | 0,0 |
| 75 | `TRadioButton` | `RBWParHigh` | hoch | `PanelWRBLeft` | 240,0 |
| 76 | `TRadioButton` | `RBWParLow` | niedrig | `PanelWRBLeft` | 120,0 |
| 79 | `TLabel` | `LabWParmeter` | Eintrittswahrscheinlichkeit des Gefährdungsereignisses: | `PanelLabelWParameter` | 16,0 |
| 82 | `TLabeledEditEx` | `LEEXGraphPLrFile` |  | `PanelRsikGraphDoc` | 220,140 |
| 83 | `TIFABitBtn` | `BBBrowseGraphPLrFile` | ... | `PanelRsikGraphDoc` | 645,140 |
| 84 | `TIFABitBtn` | `BBOpenGraphPLrFile` | Öffnen | `PanelRsikGraphDoc` | 672,140 |
| 85 | `TLabeledMemoEx` | `LMExGraphPLrDoc` |  | `PanelRsikGraphDoc` | 220,2 |
| 92 | `TLabeledEditEx` | `LEExPFH` |  | `PanelPLData` | 500,0 |
| 93 | `TLabeledEditEx` | `LEExPL` | PL-Wert der Sicherheitsfunktion, ermittelt auf der Grundlage der enthaltenen Teilsysteme | `PanelPLData` | 180,0 |
| 110 | `TLabeledComboBoxEx` | `CBExPLEMI` | Pfade zur Umsetzung der Maßnahmen für die elektromagnetische Störfestigkeit (EMI) eines SR | `Panel_EMI_Choice` | 180,6 |
| 111 | `TLabeledMemoEx` | `LMExPLDocEMI` |  | `Panel_EMI_Choice` | 180,42 |
| 112 | `TIFABitBtn` | `BBBrowseDocumentFileEMI` | ... | `Panel_EMI_Choice` | 644,108 |
| 113 | `TIFABitBtn` | `BBOpenDocumentFileEMI` | Öffnen | `Panel_EMI_Choice` | 671,108 |
| 114 | `TLabeledEditEx` | `LEEXDocumentFileEMI` |  | `Panel_EMI_Choice` | 180,108 |
| 120 | `TLabel` | `LabSF` | Sicherheitsfunktion | `PanelTop` | 88,6 |

## TFormSplash

标题：`Info über SISTEMA`

可寻址窗口类：`THTMLabel`×1, `TIFALabel`×5, `TImage`×1, `TLabel`×3, `TPanel`×11, `TProgressBar`×1, `TShape`×1, `TTimer`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 14 | `TLabel` | `LabVersionVal` | SISTEMA Version | `PanelVersions` | 132,0 |
| 15 | `TLabel` | `LabNormVersionVal` | Norm Version | `PanelVersions` | 132,22 |
| 19 | `TLabel` | `LabSpecialVersion` | Vorabversion für Firma [XXX], nur zur internen Verwendung, Weitergabe nicht erlaubt. | `PanelSpecialVersion` | 16,0 |

## TFormSSMMessageListUIAbs

标题：`Meldungen`

可寻址窗口类：`TAction`×4, `TActionList`×1, `TIFAMarkedStringGrid`×1, `TMenuItem`×4, `TPopupMenu`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 3 | `TMenuItem` | `Auswhlen1` |  | `PM` | 0,0 |
| 4 | `TMenuItem` | `Bearbeiten1` |  | `PM` | 0,0 |
| 5 | `TMenuItem` | `KommentarzumHinweisentfernen1` |  | `PM` | 0,0 |
| 6 | `TMenuItem` | `Speicher1` |  | `PM` | 0,0 |

## TFormT10DDeviceListUI

标题：`Meldungen`

可寻址窗口类：`TAction`×2, `TActionList`×1, `TAdvGlowButton`×1, `TIFAAdvListView`×1, `TImageList`×2, `TMenuItem`×2, `TPanel`×2, `TPopupMenu`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 6 | `TMenuItem` | `Bearbeiten1` |  | `PM` | 0,0 |
| 7 | `TMenuItem` | `Gertelisteaktualisieren1` |  | `PM` | 0,0 |

## TFormVersionDiff

标题：`Versionsdifferenz`

可寻址窗口类：`TBitBtn`×1, `TImage`×1, `TLabel`×1, `TLabeledMemoEx`×1, `TPanel`×1

| 顺序 | 类 | DFM 名称 | 文本/标题 | 父容器 | 位置 |
|---|---|---|---|---|---|
| 2 | `TLabel` | `LabelInfo` | Versionsdifferenz | `PanelMain` | 46,16 |
| 4 | `TLabeledMemoEx` | `LMExMessage` |  | `PanelMain` | 8,72 |
| 5 | `TBitBtn` | `BBOk` | Ok | `PanelMain` | 498,348 |

## 其它窗体（同样已解析入库）

`TCUSBTNFORM`, `TCUSTOMIZERFORM`, `TFINDDIALOGFORM`, `TFORMADDRESSBOOKUI`, `TFORMADDRESSCONTACTSUI`, `TFORMADVMEMOEDITOR`, `TFORMAPPEXCEPTION`, `TFORMBOOLPROPERTYUI`, `TFORMCLOSE`, `TFORMCOLORPROPERTYUI`, `TFORMCONFIGMGRUI`, `TFORMCONFIGPATHS`, `TFORMCONFIGVDMA`, `TFORMCONTACTSUI`, `TFORMCONTACTUI`, `TFORMDBMIGRATIONMGR`, `TFORMDBUPDATING`, `TFORMDESARC`, `TFORMDEVICEABS`, `TFORMEXTENDEDSEARCH`, `TFORMFILEDIRPROPERTYUI`, `TFORMFILEINUSE`, `TFORMFILENAMEPROPERTYUI`, `TFORMFILTERPANEL`, `TFORMGEP`, `TFORMHELP`, `TFORMHTMLBROWSER`, `TFORMIFAMEMO_EDITOR`, `TFORMIMPEXP`, `TFORMITEMMANAGER`, `TFORMLIBINFO`, `TFORMLIBINFOMSG`, `TFORMLIBNAME`, `TFORMLIBPROPERTY`, `TFORMLIBTYPESELECTORA`, `TFORMLIBTYPESELECTORB`, `TFORMLVLIB`, `TFORMLVVDMAABS`, `TFORMMESSAGEHELPERUI`, `TFORMNETWORKDBSELECTION`, `TFORMOPENURLUI`, `TFORMPFHRISKCHARTDIAGRAMM`, `TFORMPROGRESS`, `TFORMPROGRESSCONV`, `TFORMPROGRESSSSM`, `TFORMREPORTCONTACTINFORMATION`, `TFORMREPORTPRINTOPTION`, `TFORMREPORTSETUP`, `TFORMREPORTSTATUS`, `TFORMRESCUEPR`, `TFORMSAVEDEBUGDETAILS`, `TFORMSEARCHPANEL`, `TFORMSSMDEBUG`, `TFORMVALUEPROPERTYUI`, `TFORMVDMA66413LANGUAGEUI`, `TFORMVDMA66413UI`, `TFORMVDMADETAILUI`, `TFORMVDMADEVICEUI`, `TFORMVDMAMANUFACTUREUI`, `TFORMVDMAPROCESSUI`, `TFORMVDMAUSECASE`, `TRAVEPREVIEWFORM`, `TREPLACEDIALOGFORM`, `TRPSETUPFORM`, `TRPSTATUSFORM`

## 未能解析的资源

- TMECONTACTFORM: unknown TValueType 105
- TMEDETAILSFORM: unknown TValueType 105
- TMESCRSHOTFORM: unknown TValueType 105
