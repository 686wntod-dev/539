# Stage208｜今彩539 50期 Rolling-Origin Shadow 診斷
日期：2026-11-26
狀態：HISTORICAL_ROLLING_ORIGIN_SHADOW_DIAGNOSTIC_ONLY

## 目的與範圍
本階段沿用已恢復的 4037-row GPT 生成 Cleanroom master，對 AI-1 W20、AI-3 K=2000 與 R3 CR1 18F LOGIT reverse challenger 做 50 個連續目標期的嚴格時間序列 rolling-origin 診斷。每個目標期只使用該期之前資料；R3 每個 fold 使用前 1000 個目標期訓練。這是新的 Cleanroom/Shadow 診斷，不是 Stage179 原始 trainer 的重演。

## 輸入與完整性
- Master：`AI3_Legacy_Full4037_Rebuilt_v2.csv`
- Rows：4037；日期：2014-01-01 至 2026-11-16
- SHA256：`6c18084eab2966e4afc37e45fa916ad4a77414f07733a2947e321851c56e1628`
- 日期唯一、期別唯一、每期 5 個不同號碼、號碼範圍 01–39：PASS
- 評估期：2026-09-19 至 2026-11-16，共 50 期
- R3 每折訓練窗：前 1000 期；所有特徵只取目標期之前資料：PASS

## 結果
| 模組 | 50期 Pool10 命中總數 | 平均每期命中 | Bootstrap 95% CI | 隨機 Pool10 期望 |
|---|---:|---:|---:|---:|
| AI-1 W20 | 58 | 1.16 | 0.92–1.40 | 1.282 |
| AI-3 K=2000 | 57 | 1.14 | 0.90–1.38 | 1.282 |

- AI-1：13 期 0 命中；18 期達 2 碼以上。
- AI-3：13 期 0 命中；17 期達 2 碼以上。
- 兩者平均均低於隨機期望點估計，信賴區間仍涵蓋隨機期望；目前沒有證據顯示優於隨機。

### R3 CR1 反向排除
- 正確排除：426 / 500 個排除名額
- 反向排除精準度：85.20%
- 錯誤排除（開獎號碼落入排除10）：74
- Wilson 95% CI：81.82%–88.04%
- 隨機排除精準度基準：87.18%
- 隨機基準預期錯誤排除數：64.10；本次觀察 74

R3 本次點估計低於隨機基準，信賴區間亦未支持 90% 目標。這不構成長期劣於隨機的確證，但足以否決「已達 90%」的宣稱。

## 重現性
- 新執行腳本 SHA256：`3661abeba081dbd86ca3d9fbbddc76b2ce0d97f78b6dc5a922268eaddf9d075c`
- 結果 CSV SHA256：`4d26aabe48128d24cc15468e2356885c736e8c81077002fef728733acb400c4c`
- Acceptance JSON SHA256：`fd85cd62c2e6e94832d9f59f054cea4ad7d92ef66c8a447b6b0c338e34d7669f`
- 獨立第二次執行：CSV 與 Acceptance JSON SHA256 完全相同，PASS

## 限制與治理
1. 本階段是歷史 rolling-origin 回放，不是事前不可變封存的 prospective lock。
2. AI-1、AI-3 是明確標記的 Cleanroom reconstruction，不是 Stage179 原始 trainer。
3. R3 是 CR1 18F LOGIT reverse challenger，不是 Stage179 R3 原始訓練流程。
4. 50 期不足以證明 90% 排除率或模型優勢；需持續逐期事前鎖定並累積獨立前瞻樣本。
5. 未修改任何既有 Master、歷史 Lock、Stage179 輸出或 Production Registry；未建立正式預測鎖。
6. Production 維持 `BLOCKED_P0_HOLD`；本階段不得視為升級或正式模型投票資格。

## 下一步
維持 R3 Shadow-only，開始新的逐期 pre-draw immutable shadow lock；每期完整記錄 10 碼排除清單、資料 cutoff、模型/特徵/程式 SHA，開獎後自動評分。至少累積 100 個獨立前瞻目標期後再評估 90% 指標，並同時報告隨機基準與 Wilson 區間。