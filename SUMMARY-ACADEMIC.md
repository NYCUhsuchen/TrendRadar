# TrendRadar 學術論文監控工具 - 改造總結

## 📋 項目概述

本次改造將 TrendRadar 從社交媒體熱點監控工具成功轉換為學術論文監控工具，同時保持了原有功能的完整性。

## ✅ 已完成的功能

### 1. 學術平台支持

#### arXiv 集成
- ✅ 支持官方 API (http://export.arxiv.org/api/query)
- ✅ 按類別搜索 (如 cs.AI, cs.CV, cs.LG 等)
- ✅ 按關鍵詞搜索（標題、摘要、作者等）
- ✅ 支持複雜的布爾查詢
- ✅ XML 響應解析和格式化
- ✅ 可配置結果數量和排序方式

**查詢示例**:
```yaml
# 按類別
query: "cat:cs.AI"

# 按關鍵詞
query: "all:transformer+AND+cat:cs.CL"

# 按標題
query: "ti:neural+network"
```

#### PubMed 集成
- ✅ 支持 E-utilities API
- ✅ 生物醫學論文搜索
- ✅ 時間範圍過濾 (days_back)
- ✅ 兩步驟查詢（搜索 + 獲取詳情）
- ✅ XML 響應解析
- ✅ PMID 和完整元數據提取

**查詢示例**:
```yaml
query: "artificial intelligence AND medicine"
query: "cancer therapy[Title]"
query: "COVID-19[MeSH]"
```

### 2. 通知系統增強

#### LINE Messaging API
- ✅ 完整的 LINE Bot 集成
- ✅ 支持純文本消息
- ✅ 支持 Flex Message (卡片式展示)
- ✅ 針對學術論文優化的展示格式
- ✅ 支持批量發送和分頁
- ✅ 移動端體驗優秀

**Flex Message 特性**:
- 論文標題、作者、來源卡片式展示
- 直接點擊按鈕查看論文
- 最多顯示 10 篇論文避免過長

#### Email 推送
- ✅ 原有功能保留並優化
- ✅ 支持 HTML 格式
- ✅ 適配學術論文展示
- ✅ 支持多個收件人
- ✅ 自動識別主流郵箱服務商

### 3. 核心架構改造

#### academic_fetcher.py
```python
class AcademicFetcher:
    - fetch_arxiv_papers()      # arXiv 論文獲取
    - fetch_pubmed_papers()      # PubMed 論文獲取
    - format_for_trendradar()    # 格式轉換
    - _parse_arxiv_xml()         # XML 解析
    - _parse_pubmed_xml()        # XML 解析

def crawl_academic_platforms()  # 批量爬取
```

#### line_notifier.py
```python
class LineNotifier:
    - send_text_message()       # 純文本消息
    - send_flex_message()       # Flex 消息

def send_to_line()              # TrendRadar 集成
def create_paper_flex_message() # Flex 格式生成
```

#### main.py 修改
```python
# 新增導入
from academic_fetcher import crawl_academic_platforms
from line_notifier import send_to_line

# 修改方法
DataFetcher.crawl_websites()     # 支持雙模式
DataFetcher._crawl_social_media() # 原有邏輯分離
send_to_notifications()          # 新增 LINE
_has_notification_configured()   # 新增 LINE 檢查
```

### 4. 配置系統

#### config.yaml 增強
```yaml
# 新增 LINE 配置
webhooks:
  line_channel_access_token: ""
  line_user_id: ""

# 學術平台配置
platforms:
  - id: "arxiv_ai"
    name: "arXiv AI"
    type: "arxiv"          # 新增 type 字段
    query: "cat:cs.AI"     # 新增 query 字段
    max_results: 30        # 新增限制
    
  - id: "pubmed_test"
    type: "pubmed"
    query: "AI AND medicine"
    max_results: 20
    days_back: 7           # PubMed 專用
```

#### 示例配置文件
- ✅ config-academic-example.yaml - 完整學術配置
- ✅ frequency_words-academic-example.txt - 學術關鍵詞
- ✅ 包含詳細的查詢語法說明
- ✅ 涵蓋主要研究領域

### 5. 文檔系統

#### README-ACADEMIC.md
- ✅ 完整的功能介紹
- ✅ 快速開始指南
- ✅ arXiv 查詢語法說明
- ✅ PubMed 查詢語法說明
- ✅ 配置示例
- ✅ 故障排除
- ✅ GitHub Actions 配置

#### QUICKSTART-ACADEMIC.md
- ✅ 分步驟配置指南
- ✅ Email 和 LINE 配置詳解
- ✅ 常見問題解答
- ✅ 最佳實踐建議
- ✅ 查詢語法速查表

#### test_academic.py
- ✅ arXiv API 測試
- ✅ PubMed API 測試
- ✅ 集成測試
- ✅ 完整的錯誤處理

## 🎨 技術特點

### 1. 向後兼容
- ✅ 保留所有原有功能
- ✅ 原有配置文件仍可使用
- ✅ 社交媒體平台繼續工作
- ✅ 可混合配置學術和社交平台

### 2. 模組化設計
- ✅ 學術功能獨立模組
- ✅ 不修改原有核心邏輯
- ✅ 清晰的代碼分離
- ✅ 易於維護和擴展

### 3. 優雅降級
- ✅ 模組導入失敗自動降級
- ✅ 警告信息友好
- ✅ 不影響其他功能運行

### 4. 錯誤處理
- ✅ 完整的異常捕獲
- ✅ 友好的錯誤信息
- ✅ 失敗重試機制（社交媒體）
- ✅ 詳細的日誌輸出

## 📊 支持的功能組合

| 模式 | 數據源 | 通知方式 | 適用場景 |
|------|--------|---------|----------|
| 純學術 | arXiv + PubMed | Email + LINE | 學術研究者 |
| 純社交 | 知乎 + 微博等 | 企業微信 + 飛書 | 熱點監控（原功能） |
| 混合 | 學術 + 社交 | 所有方式 | 綜合需求 |

## 🔄 數據流程

```
配置文件 (config.yaml)
    ↓
平台類型判斷 (type: arxiv/pubmed/social)
    ↓
┌─────────────┴─────────────┐
↓                           ↓
學術平台 API              社交媒體 API
(academic_fetcher)      (原有邏輯)
    ↓                           ↓
格式統一化 (TrendRadar 格式)
    ↓
關鍵詞過濾 (frequency_words.txt)
    ↓
權重計算和排序
    ↓
報告生成 (HTML + 數據)
    ↓
┌───────┴───────┐
↓               ↓
Email 推送   LINE 推送
(HTML格式)   (Flex Message)
```

## 📈 性能和限制

### API 限制
- **arXiv**: 約 3秒/請求（官方建議）
- **PubMed**: 約 3秒/請求 + 0.5秒延遲
- **建議間隔**: 2000-3000ms

### 推送限制
- **LINE Text**: 5000 字符
- **LINE Flex**: 10 個卡片
- **Email**: 無明顯限制

### 數量建議
- **arXiv**: 20-50 篇/平台
- **PubMed**: 10-30 篇/平台
- **總數**: 100-200 篇/天

## 🚀 部署選項

### 1. 本地運行
```bash
python main.py
```

### 2. GitHub Actions
- 定時自動執行
- 無需服務器
- 使用 Secrets 保護憑證

### 3. Docker
- 容器化部署
- 易於遷移
- 環境隔離

### 4. Cron Job
- Linux 服務器定時任務
- 靈活的執行時間
- 低資源消耗

## 🎯 使用場景示例

### 場景 1: AI 研究者
```yaml
platforms:
  - type: arxiv
    query: "cat:cs.AI OR cat:cs.LG"
  - type: arxiv
    query: "all:transformer"

keywords:
  Large Language Model
  Diffusion Model
  @20
```

### 場景 2: 醫學研究者
```yaml
platforms:
  - type: pubmed
    query: "AI AND medical imaging"
    days_back: 7
  - type: pubmed
    query: "cancer therapy"

keywords:
  Deep Learning
  Medical
  Diagnosis
  +treatment
```

### 場景 3: 跨領域研究者
```yaml
platforms:
  - type: arxiv
    query: "cat:cs.AI"
  - type: pubmed
    query: "bioinformatics"
  - id: zhihu  # 社交媒體

keywords:
  AI
  Machine Learning
  Bioinformatics
```

## 🔮 未來擴展方向

### 短期（建議）
- [ ] Google Scholar 支持（需要爬蟲）
- [ ] bioRxiv 支持
- [ ] SSRN 支持
- [ ] 更多 LINE 功能（推播、對話）

### 中期
- [ ] 論文摘要翻譯
- [ ] 相關論文推薦
- [ ] 引用分析
- [ ] 作者追蹤

### 長期
- [ ] AI 摘要生成
- [ ] 個性化推薦算法
- [ ] 協作功能
- [ ] Web UI

## 📝 使用提示

### 最佳實踐
1. **從小範圍開始** - 先配置 1-2 個平台測試
2. **逐步調整** - 根據接收情況調整關鍵詞
3. **合理設置數量** - 避免信息過載
4. **定期檢查** - 確保配置符合需求

### 常見錯誤
1. **忘記設置 type** - 學術平台必須指定 type
2. **查詢語法錯誤** - 參考文檔檢查語法
3. **請求過於頻繁** - 增加 request_interval
4. **Email 認證失敗** - 使用應用專用密碼

## 🎉 總結

本次改造成功實現了：
- ✅ 完整的學術平台支持（arXiv + PubMed）
- ✅ 現代化的通知方式（LINE Messaging API）
- ✅ 保持原有功能完全兼容
- ✅ 詳盡的文檔和示例
- ✅ 靈活的配置系統
- ✅ 優秀的可擴展性

**TrendRadar 現在既是社交媒體監控工具，也是學術論文監控工具！**

## 📞 支持

- 查看 [README-ACADEMIC.md](README-ACADEMIC.md) - 完整文檔
- 查看 [QUICKSTART-ACADEMIC.md](QUICKSTART-ACADEMIC.md) - 快速指南
- 運行 `python test_academic.py` - 測試功能
- 查看配置示例 - config-academic-example.yaml

**祝使用愉快！🚀**
