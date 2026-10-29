孩子的遊戲／コドモノアソビ　散檔劇本回寫批次（t221）
================================================

本包取代先前 t214 的 make_loose_tc.bat／make_loose_sc.bat 風格，
改用用戶提供的完整 141 章 insert bat 格式。

檔案
----
  BGIScriptInserter_Lib.py   UTF-8 回寫工具（DSC 自動解壓→回寫→原 key 再壓）
  insert_big5.bat            繁中批次（一字不差＝用戶附件）
  insert_gbk.bat             簡中批次（一字不差＝用戶附件）
  README.txt                 本說明

目錄約定（與 bat 同層）
----------------------
  source/          原版 DSC 散檔（有無副檔名皆可；工具會自動解壓再壓）
  big5/            繁中譯文 txt，檔名 <章>.txt（無 _tc 後綴）
  gbk/             簡中譯文 txt，檔名 <章>.txt（無 _sc 後綴）
  outputbig5/      繁中回寫後 DSC 散檔＋圖＋系統（bat 自動 mkdir）
  outputgbk/       簡中回寫後 DSC 散檔＋圖＋系統（bat 自動 mkdir）
  BIG5PIC/         繁中圖資源（bat 結尾 copy 入 outputbig5）
  GBKPIC/          簡中圖資源（bat 結尾 copy 入 outputgbk）
  sysprg_big5/     UTF-8 系統 ._bp 散檔（繁）
  sysprg_gbk/      UTF-8 系統 ._bp 散檔（簡）

用法
----
1. 把本包四個檔與上述目錄放在同一工作目錄。
2. 確認 source／big5 或 gbk／圖／系統目錄已備齊。
3. 跑 insert_big5.bat（繁）或 insert_gbk.bat（簡）。
4. 完成後 outputbig5／outputgbk 內即為可部署散檔。

注意
----
- 請用本包的 BGIScriptInserter_Lib.py（UTF-8 版）。
  不要用 BGIScriptInserter_Lib-jp.py（日文方式回寫會令選項／人名牌錯位）。
- 部署：原版 script.arc 不要改；把 output* 裡的散檔（劇本 DSC、圖、系統 ._bp）
  放到遊戲目錄即可。需配合 UTF-8 EXE（KodomoNoAsobi_UTF8_FIX.exe）。
- 若 sysprg.arc 仍在遊戲目錄，請先更名／移走，改用散檔系統模組。

章數
----
兩個 bat 各 141 行 BGIScriptInserter 呼叫，對應全章劇本。
