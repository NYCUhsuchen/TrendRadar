# TrendRadar 學術論文監控工具

TrendRadar 學術版是基於原 TrendRadar 專案改造的學術論文監控工具，支持監控 arXiv、PubMed 等學術平台的最新論文，並通過 Email 和 LINE 等方式推送。

## ✨ 核心功能

### 學術平台支持

- **arXiv** - 支持按類別或關鍵詞搜索最新論文
  - 計算機科學（CS）各子領域
  - 數學、物理、統計學等
  - 支持複雜查詢語法

- **PubMed** - 支持生物醫學領域論文搜索
  - 醫學、生物學、藥學等
  - 支持 MeSH 主題詞搜索
  - 可設置時間範圍

### 智能推送

- **Email 推送** - 精美的 HTML 格式郵件報告
- **LINE 推送** - 支持 Flex Message 豐富展示
- 保留原有的其他通知渠道（飛書、釘釘等）

### 關鍵詞過濾

- 按研究領域、技術關鍵詞過濾論文
- 支持必須詞、過濾詞、數量限制
- 按配置順序或熱度排序

## 🚀 快速開始

### 1. 環境準備

```bash
# 克隆項目
git clone https://github.com/你的用戶名/TrendRadar.git
cd TrendRadar

# 安裝依賴
pip install -r requirements.txt
```

### 2. 配置學術平台

複製學術配置示例：

```bash
cp config/config-academic-example.yaml config/config.yaml
cp config/frequency_words-academic-example.txt config/frequency_words.txt
```

編輯 `config/config.yaml`：

```yaml
platforms:
  # arXiv - 人工智能
  - id: "arxiv_ai"
    name: "arXiv AI"
    type: "arxiv"
    query: "cat:cs.AI"  # 按類別搜索
    max_results: 30
  
  # arXiv - 大語言模型（關鍵詞搜索）
  - id: "arxiv_llm"
    name: "arXiv LLM"
    type: "arxiv"
    query: "all:large+language+model"  # 關鍵詞搜索
    max_results: 30
  
  # PubMed - AI 醫學
  - id: "pubmed_ai_med"
    name: "PubMed AI醫學"
    type: "pubmed"
    query: "artificial intelligence AND medicine"
    max_results: 20
    days_back: 7  # 最近7天
```

### 3. 配置關鍵詞

編輯 `config/frequency_words.txt`，設置感興趣的研究主題：

```
# 大語言模型
Large Language Model
LLM
GPT
BERT
Transformer
+training

# 計算機視覺
Computer Vision
Image
Object Detection
+deep learning

# 過濾詞
!survey
!review
```

### 4. 配置通知方式

#### 方式一：Email 推送（推薦）

```yaml
webhooks:
  email_from: "your-email@gmail.com"
  email_password: "your-app-password"  # Gmail 需使用應用專用密碼
  email_to: "recipient@example.com"
```

#### 方式二：LINE 推送（推薦）

1. 創建 LINE Messaging API Channel
   - 訪問 [LINE Developers Console](https://developers.line.biz/)
   - 創建 Provider 和 Messaging API Channel
   - 獲取 Channel Access Token

2. 獲取 User ID 或 Group ID
   - 可使用 LINE Bot 發送消息給自己獲取 User ID
   - 或將 Bot 加入群組獲取 Group ID

3. 配置：

```yaml
webhooks:
  line_channel_access_token: "你的 Channel Access Token"
  line_user_id: "你的 User ID 或 Group ID"
```

### 5. 運行

```bash
python main.py
```

## 📖 arXiv 查詢語法

### 按類別搜索

```yaml
query: "cat:cs.AI"  # 人工智能
query: "cat:cs.CV"  # 計算機視覺
query: "cat:cs.LG"  # 機器學習
query: "cat:cs.CL"  # 自然語言處理
```

### 按關鍵詞搜索

```yaml
# 標題中包含
query: "ti:neural+network"

# 摘要中包含
query: "abs:transformer"

# 所有字段
query: "all:machine+learning"

# 組合查詢
query: "ti:GPT+AND+cat:cs.CL"
```

### 主要類別

- `cs.AI` - 人工智能
- `cs.CV` - 計算機視覺
- `cs.LG` - 機器學習
- `cs.CL` - 自然語言處理
- `cs.RO` - 機器人學
- `cs.CR` - 密碼學與安全
- `stat.ML` - 統計-機器學習

## 📖 PubMed 查詢語法

```yaml
# 簡單搜索
query: "machine learning"

# 邏輯運算
query: "artificial intelligence AND medicine"
query: "(cancer OR tumor) AND therapy"

# MeSH 主題詞
query: "Artificial Intelligence[MeSH]"

# 標題搜索
query: "COVID-19[Title]"
```

## 🔧 高級配置

### 推送模式

```yaml
report:
  mode: "daily"  # 每日匯總所有論文
  # mode: "incremental"  # 只推送新增論文
  # mode: "current"  # 推送當前榜單
```

### 排序和數量控制

```yaml
report:
  sort_by_position_first: true  # 按配置順序優先（推薦）
  max_news_per_keyword: 20  # 每個關鍵詞最多20篇
```

在 `frequency_words.txt` 中：

```
Transformer
GPT
BERT
@10  # 這組最多顯示10篇
```

### 定時執行（使用 cron）

```bash
# 每天早上 9 點執行
0 9 * * * cd /path/to/TrendRadar && python main.py
```

## 📊 輸出格式

### Email 報告

- 精美的 HTML 格式
- 按關鍵詞分類展示
- 包含論文標題、作者、摘要
- 點擊標題直接訪問論文

### LINE 推送

- 使用 Flex Message 卡片式展示
- 支持快速瀏覽和點擊查看
- 移動端體驗優秀

### HTML 文件

- 自動保存到 `output/日期/html/` 目錄
- 可用瀏覽器打開查看
- 支持 GitHub Pages 部署

## ⚙️ GitHub Actions 自動化

創建 `.github/workflows/academic-monitor.yml`：

```yaml
name: Academic Paper Monitor

on:
  schedule:
    - cron: '0 1 * * *'  # 每天早上 9 點（UTC+8）
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run monitor
        env:
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          LINE_CHANNEL_ACCESS_TOKEN: ${{ secrets.LINE_CHANNEL_ACCESS_TOKEN }}
          LINE_USER_ID: ${{ secrets.LINE_USER_ID }}
        run: python main.py
```

在 GitHub Secrets 中配置：
- `EMAIL_FROM`
- `EMAIL_PASSWORD`
- `EMAIL_TO`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

## 🔍 故障排除

### arXiv API 限流

arXiv API 有速率限制，建議：
- 設置 `request_interval: 3000` (3秒)
- 減少 `max_results`
- 避免頻繁請求

### PubMed 無結果

- 檢查查詢語法是否正確
- 嘗試增加 `days_back`
- 使用更通用的關鍵詞

### LINE 推送失敗

- 確認 Channel Access Token 正確
- 確認 User ID 或 Group ID 正確
- 檢查 Bot 是否已加入群組（如果推送到群組）

## 📝 示例配置

### AI 研究者

```yaml
platforms:
  - id: "arxiv_llm"
    type: "arxiv"
    query: "cat:cs.CL+OR+cat:cs.LG"
    max_results: 50
  
  - id: "arxiv_cv"
    type: "arxiv"
    query: "cat:cs.CV"
    max_results: 30
```

```
Large Language Model
GPT
BERT
Transformer
Diffusion
Vision-Language
@15
```

### 醫學研究者

```yaml
platforms:
  - id: "pubmed_ai_med"
    type: "pubmed"
    query: "artificial intelligence AND medical imaging"
    max_results: 30
    days_back: 7
  
  - id: "pubmed_cancer"
    type: "pubmed"
    query: "cancer therapy"
    max_results: 20
    days_back: 7
```

```
AI
Deep Learning
Machine Learning
+medical
+diagnosis

Cancer
Tumor
Therapy
+treatment

!review
!survey
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 License

GPL-3.0 License

## 🙏 致謝

- 基於 [TrendRadar](https://github.com/sansan0/TrendRadar) 項目改造
- arXiv API 提供學術論文數據
- PubMed E-utilities 提供生物醫學論文數據
