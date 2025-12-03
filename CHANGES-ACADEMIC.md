# TrendRadar 學術版 - 簡化說明

## 變更摘要

本版本已將 TrendRadar 簡化為只專注於**學術論文監控**和**Email/LINE 通知**的工具。

### ✅ 保留的功能

1. **學術平台支持**
   - arXiv 論文搜索
   - PubMed 論文搜索
   - 支持自定義查詢語法

2. **通知渠道**
   - ✅ Email 推送（支持 HTML 格式）
   - ✅ LINE 推送（支持 Flex Message）

3. **核心模組**
   - `main.py` - 主程序（已簡化，從 5000+ 行減少到約 700 行）
   - `academic_fetcher.py` - 學術平台數據獲取
   - `line_notifier.py` - LINE 通知模組
   - `test_academic.py` - 測試腳本

4. **配置文件**
   - `config/config.yaml` - 主配置
   - `config/config-simplified.yaml` - 簡化配置模板

### ❌ 移除的功能

1. **社交媒體平台爬蟲**
   - ❌ 知乎、微博、抖音、bilibili 等
   - ❌ 百度熱搜、今日頭條等
   - ❌ newsnow API 集成

2. **多餘通知渠道**
   - ❌ 飛書（Feishu）
   - ❌ 釘釘（DingTalk）
   - ❌ 企業微信（WeWork）
   - ❌ Telegram
   - ❌ ntfy
   - ❌ Bark
   - ❌ Slack

3. **Web 相關功能**
   - ❌ GitHub Pages 網頁生成
   - ❌ 複雜的 HTML 報告（保留簡單版本）
   - ❌ 圖片保存功能
   - ❌ 熱點權重計算
   - ❌ 推送時間窗口控制

4. **MCP 伺服器**
   - ❌ AI 分析功能
   - ❌ MCP 工具和服務
   - ❌ 所有 mcp_server/ 目錄內容

5. **其他功能**
   - ❌ 頻率詞統計
   - ❌ 關鍵詞匹配和過濾
   - ❌ 新增標題檢測
   - ❌ 當日汇总/增量模式選擇
   - ❌ 版本更新檢查

## 代碼統計

- **原始 main.py**: 5,014 行
- **簡化後 main.py**: ~700 行
- **減少比例**: 約 86%

## 文件對照

### 保留的文件

```
TrendRadar/
├── main.py                      # ✅ 已簡化
├── academic_fetcher.py          # ✅ 保留
├── line_notifier.py            # ✅ 保留
├── test_academic.py            # ✅ 保留
├── requirements.txt            # ✅ 保留
├── config/
│   ├── config.yaml            # ✅ 保留（需更新）
│   ├── config-simplified.yaml # ✅ 新增（簡化模板）
│   └── config-academic-example.yaml # ✅ 保留
└── README-ACADEMIC-SIMPLIFIED.md # ✅ 新增（使用指南）
```

### 備份的文件

```
main_original_backup.py         # 原始 main.py 備份
```

### 可移除的文件/目錄

如果你只需要學術監控功能，可以刪除以下內容：

```
mcp_server/                     # MCP 伺服器（AI 分析）
docker/                         # Docker 相關
index.html                      # GitHub Pages 網頁
setup-*.sh                      # 設置腳本
setup-*.bat                     # Windows 設置腳本
start-http.*                    # HTTP 伺服器啟動腳本
README.md                       # 原始 README（包含社交媒體功能）
README-EN.md                    # 英文 README
README-MCP-*.md                 # MCP 相關文檔
README-Cherry-Studio.md         # Cherry Studio 文檔
QUICKSTART-ACADEMIC.md          # 舊的快速開始文檔
```

## 使用方式

### 1. 最小化安裝

```bash
# 只保留必要文件
git clone https://github.com/NYCUhsuchen/TrendRadar.git
cd TrendRadar

# 刪除不需要的文件（可選）
rm -rf mcp_server/ docker/ 
rm index.html setup-*.sh setup-*.bat start-http.*
rm README.md README-EN.md README-MCP-*.md README-Cherry-Studio.md

# 使用簡化版 README
cp README-ACADEMIC-SIMPLIFIED.md README.md
```

### 2. 配置

```bash
# 複製簡化配置
cp config/config-simplified.yaml config/config.yaml

# 編輯配置文件，設置：
# 1. 學術平台（arXiv, PubMed）
# 2. Email 推送（必須）
# 3. LINE 推送（可選）
```

### 3. 運行

```bash
# 安裝依賴
pip install -r requirements.txt

# 執行監控
python main.py
```

## 配置示例

### 最小配置（只使用 Email）

```yaml
crawler:
  request_interval: 2000
  enable_crawler: true
  use_proxy: false

notification:
  enable_notification: true
  webhooks:
    email_from: "your@gmail.com"
    email_password: "your-app-password"
    email_to: "recipient@gmail.com"

platforms:
  - id: "arxiv_ai"
    name: "arXiv AI"
    type: "arxiv"
    query: "cat:cs.AI"
    max_results: 30
```

### 完整配置（Email + LINE）

```yaml
crawler:
  request_interval: 2000
  enable_crawler: true
  use_proxy: false

notification:
  enable_notification: true
  webhooks:
    email_from: "your@gmail.com"
    email_password: "your-app-password"
    email_to: "recipient@gmail.com"
    line_channel_access_token: "your-channel-token"
    line_user_id: "your-user-id"

platforms:
  - id: "arxiv_ai"
    name: "arXiv AI"
    type: "arxiv"
    query: "cat:cs.AI"
    max_results: 30
  
  - id: "pubmed_ai"
    name: "PubMed AI"
    type: "pubmed"
    query: "artificial intelligence"
    max_results: 20
    days_back: 7
```

## 依賴項

簡化後只需要以下依賴：

```
requests>=2.32.5,<3.0.0    # HTTP 請求
pytz>=2025.2,<2026.0        # 時區處理
PyYAML>=6.0.3,<7.0.0        # YAML 配置
```

移除的依賴：
- `fastmcp` - MCP 伺服器
- `websockets` - WebSocket 支持

## 常見問題

### Q: 為什麼移除這麼多功能？

A: 根據使用者需求，本版本專注於學術論文監控和基本通知功能，移除了不必要的社交媒體和 Web 功能，使代碼更簡潔易維護。

### Q: 如果我需要原始功能怎麼辦？

A: 原始 main.py 已備份為 `main_original_backup.py`。如需使用原始功能：

```bash
cp main_original_backup.py main.py
```

### Q: 能否只保留 Email 推送？

A: 可以。在 `config.yaml` 中只配置 `email_*` 相關設置，不配置 `line_*` 即可。

### Q: 如何定時執行？

A: 使用 cron（Linux/Mac）或 Windows 任務計劃程序。詳見 README-ACADEMIC-SIMPLIFIED.md

## 技術變更詳情

### main.py 簡化內容

移除的類和函數：
- `PushRecordManager` - 推送記錄管理（不需要時間窗口控制）
- `DataFetcher._crawl_social_media()` - 社交媒體爬蟲
- `split_content_into_batches()` - 消息分批發送（簡化通知）
- `generate_html_report()` - 複雜 HTML 報告生成
- `count_word_frequency()` - 頻率詞統計
- `matches_word_groups()` - 關鍵詞匹配
- 所有其他通知渠道發送函數（飛書、釘釘等）
- 版本檢查相關函數
- GitHub Pages 相關函數

保留的函數：
- `load_config()` - 配置加載（簡化）
- `get_beijing_time()` - 時間處理
- `ensure_directory_exists()` - 目錄管理
- `save_papers_to_file()` - 文件保存
- `send_to_email()` - Email 發送
- `generate_simple_html_report()` - 簡單 HTML 報告
- `send_notifications()` - 通知發送（簡化）
- `AcademicMonitor` - 主監控類（簡化）

### 配置文件變更

`config/config.yaml` 移除的配置段：
- `report.mode` - 報告模式
- `report.rank_threshold` - 排名閾值
- `report.sort_by_position_first` - 排序優先級
- `report.max_news_per_keyword` - 數量限制
- `notification.push_window` - 推送時間窗口
- `notification.*_batch_size` - 批次大小
- `weight.*` - 權重配置
- 所有社交媒體平台配置
- 所有非 Email/LINE 的 webhook 配置

## 遷移指南

如果你正在從完整版 TrendRadar 遷移到學術簡化版：

1. **備份原始配置**
   ```bash
   cp config/config.yaml config/config_full_backup.yaml
   ```

2. **使用簡化配置模板**
   ```bash
   cp config/config-simplified.yaml config/config.yaml
   ```

3. **遷移學術平台配置**
   - 從備份文件中複製 arXiv 和 PubMed 相關配置
   - 移除所有社交媒體平台配置

4. **遷移通知配置**
   - 只保留 `email_*` 和 `line_*` 相關配置
   - 移除其他通知渠道配置

5. **測試運行**
   ```bash
   python main.py
   ```

## 支持

如有問題，請查看 README-ACADEMIC-SIMPLIFIED.md 或提交 Issue。
