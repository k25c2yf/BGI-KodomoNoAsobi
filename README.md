# 《孩子的遊戲》／コドモノアソビ — 編譯／安裝說明

倉庫：<https://github.com/k25c2yf/BGI-KodomoNoAsobi>

本文件說明如何由譯文 txt **回寫成遊戲可用散檔**，以及如何裝入原版遊戲目錄。  
對齊目前倉庫實際檔名與 `outputbig5.bat`／`outputgb.bat` 流程（勿使用已棄用的重打 `script.arc` 做法）。

---

## 1. 環境需求

| 項目 | 說明 |
|------|------|
| OS | Windows（bat 用 `copy`／`mkdir`；Linux／macOS 可改跑同等 `python` 指令） |
| Python | **Python 3**（標準庫即可；`BGIScriptInserter_Lib.py` 無第三方依賴） |
| 遊戲本體 | 正版／合法取得的《孩子的遊戲》日文版安裝目錄 |
| 本倉庫 | `git clone` 後備齊 `source/`、`big5/` 或 `gbk/`、圖與 sysprg 目錄 |

確認：

```bat
python --version
```

---

## 2. 倉庫目錄說明

與 bat／插入腳本**同層**的主要目錄與檔案：

| 路徑 | 用途 |
|------|------|
| `source/` | 原版劇本 DSC 散檔（無副檔名；約 141＋系統／雜項章） |
| `big5/` | **繁中**譯文 `●地址●正文` txt，檔名 **`<章>.txt`**（**無** `_tc` 後綴） |
| `gbk/` | **簡中**譯文，檔名 **`<章>.txt`**（**無** `_sc` 後綴） |
| `BIG5PIC/` | 繁中圖／UI 資源（bat 結尾複製進產出目錄） |
| `GBKPIC/` | 簡中圖／UI 資源 |
| `sysprg_big5/` | 繁中 **UTF-8** 系統模組散檔（`*._bp` 等）＋字型 |
| `sysprg_gbk/` | 簡中 **UTF-8** 系統模組散檔 |
| `outputbig5.bat` | 繁中一鍵回寫（141 章）→ 產出 `outputbig5/` |
| `outputgb.bat` | 簡中一鍵回寫（141 章）→ 產出 `outputgbk/` |
| `BGIScriptInserter_Lib.py` | **UTF-8** 回寫工具（**必須用此檔**） |
| `BGIScriptInserter_Lib-jp.py` | Shift-JIS／日文回寫（**不要用於本漢化**） |
| `KodomoNoAsobi_UTF8_FIX.exe` | UTF-8 遊戲主程式（部署時替換用） |
| `BGIScriptDumper_Lib.py` 等 | 抽文本／輔助工具（編譯主流程不強制） |

> 舊包／`README.txt` 曾寫 `insert_big5.bat`／`insert_gbk.bat`；**目前 GitHub 主線檔名為** `outputbig5.bat`／`outputgb.bat`，語意相同。

譯文格式示例：

```text
●000123●這是譯文內容\r第二行
```

人名用語（對白／旁白）：**丹生清澄**、**賽拉**、**美智留**、**楪**、**佳津美**。

圖片製作偏好：**PNG** 為源檔格式；匯入遊戲資源時再轉成倉庫／引擎所需格式放入 `BIG5PIC/`／`GBKPIC/`。

---

## 3. 回寫（編譯）步驟

### 3.1 繁中

1. 確認 `source/`、`big5/`、`BIG5PIC/`、`sysprg_big5/`、`BGIScriptInserter_Lib.py` 齊全。  
2. 於倉庫根目錄雙擊或執行：

```bat
outputbig5.bat
```

3. 腳本會：
   - `mkdir outputbig5`
   - 對 141 章執行：  
     `python BGIScriptInserter_Lib.py ./source/<章> ./big5/<章>.txt ./outputbig5/<章>`
   - `copy .\BIG5PIC\*.  .\outputbig5`
   - `copy .\sysprg_big5\*.*  .\outputbig5`

4. 完成後看 `outputbig5\`：內含劇本散檔（無副檔名）、圖、系統 `._bp` 等，即可部署。

### 3.2 簡中

同理執行：

```bat
outputgb.bat
```

產出目錄為 **`outputgbk\`**（注意：bat 檔名是 `outputgb`，資料夾是 `outputgbk`）。

### 3.3 單章手動回寫

```bat
python BGIScriptInserter_Lib.py <source散檔> <譯文txt> <輸出路徑>
```

例：

```bat
python BGIScriptInserter_Lib.py .\source\Custom .\big5\Custom.txt .\outputbig5\Custom
```

`Lib.py` 會：偵測 DSC → 解壓 → UTF-8 回寫 → 用原 key 再壓；裸 Buriko 則只回寫。

---

## 4. 裝入遊戲（部署）

**建議順序：**

1. **備份**整個遊戲目錄（至少：`*.exe`、`script.arc`、`sysprg.arc`、已有散檔）。  
2. 用倉庫內的 **`KodomoNoAsobi_UTF8_FIX.exe`** 替換原版主程式（或改名後啟動 UTF-8 版）。  
   - **不要**自行改 EXE 內「啟動／檔案檢查」相關字串；已修好的 UTF-8 EXE 直接用。  
3. **原版 `script.arc` 不要改、不要刪、不要重打。**  
4. 把 `outputbig5\`（或 `outputgbk\`）裡的：
   - **141 章劇本散檔**（無副檔名的 DSC）
   - 圖資源
   - 系統 `*._bp`（及 bat 一併拷出的字型等）  
   **全部複製到遊戲目錄根**（與 EXE、`script.arc` 同層）。  
   BGI 會**優先讀散檔**，arc 內同名項可被覆蓋。  
5. 若目錄裡仍有原版 **`sysprg.arc`（cp932）**：請**更名或移走**，改用上面拷入的 **UTF-8 系統散檔**。  
   否則人名牌／選項／UI 字串會對不上或亂碼。  
6. 啟動 UTF-8 EXE 測試開場、選項、存讀檔、人名牌。

### 部署對照

| 做法 | 結果 |
|------|------|
| 散檔 DSC ＋ 原版 `script.arc` 不動 | ✅ 正確 |
| UTF-8 `sysprg` 散檔，移走原版 `sysprg.arc` | ✅ 正確 |
| 重打／重壓整包 `script.arc` | ❌ 會 ERR，**已棄用** |
| 繼續用原版 cp932 `sysprg.arc` | ❌ 人名牌對唔上 |
| 用 `BGIScriptInserter_Lib-jp.py` 回寫 | ❌ 選項／字串變回日文或錯位 |

---

## 5. 注意事項（必讀）

1. **只用 `BGIScriptInserter_Lib.py`（UTF-8）**  
   倉庫雖附帶 `BGIScriptInserter_Lib-jp.py`，那是 Shift-JIS 日文插入器。用它會令**選項變回日文**、編碼錯亂。目前主線 `output*.bat` **已不再呼叫** `-jp.py`；請勿自行加回第二輪 jpname。

2. **譯文檔名**  
   bat 讀的是 `big5\00com_01.txt` 這種 **`<章>.txt`**，不是 `*_tc.txt`。若你本地譯稿帶 `_tc`／`_sc`，請先改名或複製成 bat 期望檔名。

3. **不要重打 arc**  
   全解壓再重封 `script.arc`／系統 entry 會導致 `scrmain` 等 IP 越界 **Error!!**。散檔部署即可。

4. **EXE**  
   必須配合 UTF-8 主程式；替換前備份。勿手改啟動路徑／完整性檢查字串。

5. **繁／簡不要混拷**  
   同一遊戲目錄只放一套：`outputbig5` **或** `outputgbk`，勿混 BIG5PIC／GBKPIC／兩套 sysprg。

6. **章數**  
   兩個 bat 各約 **141** 次插入呼叫，對應全劇本章（含 `Custom`、`MakerLogo` 等）。

---

## 6. 常見問題

**Q. 跑 bat 出現 `Can't find file`？**  
A. 檢查 `source\<章>` 與 `big5\<章>.txt`（或 gbk）是否存在、檔名是否多了 `_tc`。

**Q. 遊戲仍顯示日文選項？**  
A. 確認沒用 `-jp.py`；確認 `Custom` 等選項章已回寫進遊戲目錄；確認 EXE 為 UTF-8 版。

**Q. 人名牌亂碼／仍是日文系統字？**  
A. 移走 `sysprg.arc`，改用 `sysprg_big5`／`sysprg_gbk` 散檔。

**Q. 想從 DSC 抽譯文？**  
A. 可用倉庫內 `BGIScriptDumper_Lib.py`／`BGIScriptDumper_Lib-full.py`（與本編譯流程獨立）。

---

## 7. 可貼入 README 的精簡片段

見同目錄 `README_編譯片段.md`，或下文「附錄」。

---

## 8. 最後用 Enigma Virtual Box（推薦發行方式）

對齊同組《戀想關係》[`BGI-RensouRelation`](https://github.com/k25c2yf/BGI-RensouRelation) 流程：bat 產出散檔後，用 **Enigma Virtual Box（EVB）** 把漢化散檔虛擬進 UTF-8 EXE，玩家目錄不必散落上百個 DSC／`._bp`。

倉庫已附工具目錄：`Enigma Virtual Box/`（含 `enigmavb.exe`）。亦可自官網下載：<https://enigmaprotector.com/en/downloads.html>  
**本倉庫目前沒有現成 `.evb` 專案檔**；每次用 GUI 選 Input／加入檔案／Process 即可（可另存 `.evb` 方便重打）。

獨立逐步說明見同目錄 [`Enigma_Virtual_Box_封裝.md`](./Enigma_Virtual_Box_封裝.md)。

### 8.1 前提

1. 已跑完 `outputbig5.bat` 或 `outputgb.bat`，產出目錄齊全。  
2. 輸入主程式固定用 **`KodomoNoAsobi_UTF8_FIX.exe`**（勿改 EXE 內啟動／檔案檢查字串）。  
3. 繁／簡**各打一套**，不要混 `BIG5PIC` 與 `GBKPIC`、不要混兩套 `sysprg`。  
4. **不要**把原版 **`sysprg.arc`（cp932）** 加進虛擬檔；發行目錄也應移走／更名該 arc。  
5. **不要**把 **`script.arc`** 打進 EVB；原版 arc 留在遊戲目錄給引擎讀，漢化靠虛擬散檔覆蓋。  
6. **不要**虛擬 `UserData`／存檔目錄（否則存讀檔會寫不進實體碟）。

### 8.2 要掛進虛擬根的內容（與 EXE 同層）

`output*.bat` 結尾已把 PIC 與 `sysprg_*` **扁平拷進**產出目錄，故**最簡做法**是只掛產出目錄內的檔案到 `%DEFAULT FOLDER%`（虛擬根＝EXE 旁），**不要多一層** `outputbig5\` 資料夾名。

| 繁中（BIG5） | 簡中（GBK） | 說明 |
|--------------|-------------|------|
| `outputbig5\` 內全部檔案 | `outputgbk\` 內全部檔案 | 約 141 章 DSC（無副檔名）＋圖＋`*._bp`＋字型 |

產出目錄內應包含（缺一就回頭檢查 bat／來源目錄）：

| 類型 | 例 |
|------|----|
| 劇本散檔 DSC | `00com_01`、`Custom`、`yuzu25`…（無副檔名） |
| 圖／UI | `SGCnf*`、`SGBSV*` 等（來自 `BIG5PIC`／`GBKPIC`） |
| 系統模組 | `scrmain._bp`、`logwnd._bp`、`sysmsg._bp`…（來自 `sysprg_big5`／`sysprg_gbk`） |
| 字型 | `HuiFont29.ttf`、`PixlMpls12.ttf` |

**等價拆開掛載**（同《戀想關係》寫法；虛擬路徑仍須落在 EXE 旁根目錄）：

- 繁：`outputbig5/`（僅劇本散檔亦可）＋ `BIG5PIC/` ＋ `sysprg_big5/`（含 ttf）  
- 簡：`outputgbk/` ＋ `GBKPIC/` ＋ `sysprg_gbk/`

### 8.3 GUI 步驟（繁中例）

1. 執行 `outputbig5.bat`，確認 `outputbig5\` 齊全。  
2. 開啟 `Enigma Virtual Box\enigmavb.exe`。  
3. **Enter Input File Name：** 選倉庫根的 `KodomoNoAsobi_UTF8_FIX.exe`。  
4. **Enter Output File Name：** 例 `KodomoNoAsobi-BIG5.exe`（勿與 Input 同名覆寫源檔）。  
5. **Add → Add Folder Recursive**（或先把 `outputbig5` 內檔案拷到暫存扁平目錄再加）：  
   - 選 `outputbig5`  
   - 虛擬路徑對到 **`%DEFAULT FOLDER%`**，使檔名直接出現在 EXE 旁（`%DEFAULT FOLDER%\Custom`），**不要**變成 `%DEFAULT FOLDER%\outputbig5\Custom`。  
6. 核對 Files 清單：有 DSC、`._bp`、圖、ttf；**無** `sysprg.arc`／`script.arc`／`UserData`。  
7. 點 **Process**。成功後訊息含 `File successfully saved`。  
8. 可選：**File → Save** 存成 `KodomoNoAsobi-BIG5.evb` 以便下次重打。

簡中：改跑 `outputgb.bat`，掛 `outputgbk\`，輸出例 `KodomoNoAsobi-GBK.exe`。

### 8.4 發給玩家時的遊戲目錄

| 留在實體目錄 | 說明 |
|--------------|------|
| 原版各 `*.arc`（**含** `script.arc`） | 語音／動畫等；劇本仍由虛擬散檔優先覆蓋 |
| 封裝後的 `KodomoNoAsobi-BIG5.exe` 或 `-GBK.exe` | 用此啟動 |
| （可選）原版未封裝 EXE 備份 | 除錯用 |

| 必須移走／更名 | 說明 |
|----------------|------|
| `sysprg.arc` | 否則仍可能讀到 cp932 系統字，人名牌／UI 錯亂 |

玩家**不必**再手動拷 141 散檔；測試開場、選項、存讀檔、人名牌。

### 8.5 注意

- 虛擬根多一層資料夾名 → 引擎找不到散檔，等於沒打上補丁。  
- 勿把繁簡兩套同時掛進同一 EXE。  
- 部分 BGI 作品對 EVB 較挑；本作流程與《戀想關係》相同。若異常，先改回「散檔部署」（第 4 節）對照，再檢查虛擬路徑是否扁平。  
- EVB 免費版主要做虛擬化，不是強度殼；勿當防逆向方案。

---

## 附錄：流程一覽

```text
big5|gbk 譯文 txt  +  source DSC
        │
        ▼
BGIScriptInserter_Lib.py（UTF-8）← 禁止 -jp.py
        │
        ▼
outputbig5|outputgbk  （＋ PIC ＋ sysprg 散檔）
        │
        ├─（開發／除錯）複製到遊戲目錄 ＋ UTF-8 EXE
        │              script.arc 原封 ｜ sysprg.arc 移走
        │
        └─（發行推薦）Enigma Virtual Box
                       Input: KodomoNoAsobi_UTF8_FIX.exe
                       虛擬根: 產出目錄內檔案（扁平，勿多一層資料夾名）
                       Output: KodomoNoAsobi-BIG5.exe / -GBK.exe
                       遊戲目錄: 原版 arc 保留；sysprg.arc 移走；用封裝 EXE 啟動
```
