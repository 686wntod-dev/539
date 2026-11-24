# 今彩539 官方網站 API 證據擷取 v10

## 用途與限制
在 GitHub-hosted Ubuntu runner 擷取台灣彩券網站目前使用的 Daily539Result 內部 API。此端點屬網站內部 API，並非台灣彩券公開承諾穩定的 API 合約；API 回傳的期號只能作為候選證據，不能單獨升格為官方原始期別證明。

## 檔案
- `.github/workflows/539-official-capture.yml`：push 變更後自動驗證；亦可手動執行 probe/full。沒有排程。
- `fetch_official_daily539_api_v10.py`：保存原始 response bytes、HTTP headers、URL、UTC時間、SHA256、解析結果及候選對帳。
- `candidates_906.csv`：906列待核實資料，只作日期及五碼比對，不會覆寫主檔、Registry 或預測鎖。

## 已驗證執行（2026-11-24）
- GitHub Actions Run #7，commit `77ca0f2d579a386a94885c43d0e6f5db8a6469f5`，完整成功；Run #6 為前一版成功擷取。
- 35/35月份（2024-01至2026-11）HTTP 200、合法schema；35份raw response與metadata的SHA256/bytes核對通過。
- API資料913列，日期及期號各913個唯一值；日期排序與每列五碼合法性通過。
- 906列候選資料中，905列日期及五碼完全吻合；1列2026-10-23存在同日五碼差異。
- 另有7個API日期未出現在906列候選檔。
- 對帳差異另存於 `api_only_and_conflict_rows.csv`，並以 `evidence/2026-11-24_v10_api_reconciliation_review.csv` 和 `evidence/2026-11-24_secondary_crosscheck_disposition.csv` 留存獨立覆核，不得自動覆寫canonical master。
- Run #7 Artifact SHA256：`300ab24ebce769d525c6d9ad27200f7060595accf981a4064b902718a5fdeb09`。對帳狀態為 `REVIEW_REQUIRED_DIFFERENCES`，8筆API-only或衝突資料均不得自動升格。

## 重新執行
GitHub Actions → `539 Official API Evidence Capture v10`。手動選 `probe` 僅測2026-11；選 `full` 才會抓取35個月份。每次執行都應檢查summary中的 `status` 與 `candidate_reconciliation_status`；擷取成功不代表對帳無差異。

## 升級限制
1. `CAPTURE_COMPLETE` 只表示月份來源擷取成功；候選差異另由 `candidate_reconciliation_status` 表示。
2. API期號需另以官方歷史頁原始證據核對；外部第三方頁只能列次級交叉核對。
3. 禁止直接改寫主檔、歷史預測鎖、Registry v3或正式模型。
4. 此流程不恢復Formal7原始程式、R3 A/B工件或Production部署，也不解除SRC-01至SRC-06 P0 Gate。
5. Artifact保留90天，需另行下載長期封存及校驗SHA256。
