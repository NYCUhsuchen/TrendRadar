# TrendRadar 學術版快速上手指南

## 🎯 概述

此版本的 TrendRadar 已改造為學術論文監控工具，主要變更：

1. **數據源**: 社交媒體平台 → 學術平台（arXiv, PubMed）
2. **通知方式**: 增加 Email 和 LINE Messaging API 支持
3. **兼容性**: 保留原有所有功能，可同時使用

## 📋 配置步驟

### 步驟 1: 選擇配置模式

#### 模式 A: 純學術模式（推薦新用戶）

```bash
# 使用學術配置模板
cp config/config-academic-example.yaml config/config.yaml
cp config/frequency_words-academic-example.txt config/frequency_words.txt
```

#### 模式 B: 混合模式（高級用戶）

編輯現有的 `config/config.yaml`，在 platforms 中同時配置：

```yaml
platforms:
  # 學術平台
  - id: "arxiv_ai"
    name: "arXiv AI"
    type: "arxiv"
    query: "cat:cs.AI"
    max_results: 30
  
  # 社交媒體平台（原有）
  - id: "zhihu"
    name: "知乎"
    # 不指定 type 或 type: "social"
```

### 步驟 2: 配置通知方式

#### 選項 1: Email 推送（最簡單）

在 `config/config.yaml` 的 webhooks 部分：

```yaml
webhooks:
  email_from: "your-email@gmail.com"
  email_password: "your-app-password"
  email_to: "recipient@example.com,another@example.com"
```

**Gmail 用戶注意**:
1. 開啟兩步驟驗證
2. 生成應用專用密碼: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. 使用應用專用密碼作為 `email_password`

#### 選項 2: LINE 推送（推薦）

1. **創建 LINE Bot**:
   - 訪問 [LINE Developers Console](https://developers.line.biz/)
   - 點擊 "Create a new provider"
   - 創建 "Messaging API" channel
   - 記下 "Channel access token"

2. **獲取 User ID**:
   
   方法一: 使用官方方法
   ```bash
   # 加 Bot 為好友後，Bot 會發送包含 User ID 的訊息
   # 或使用 LINE Official Account Manager 查看
   ```
   
   方法二: 使用第三方工具
   - 搜尋 "LINE User ID 查詢" 相關工具

3. **配置**:
   ```yaml
   webhooks:
     line_channel_access_token: "你的 Channel Access Token"
     line_user_id: "你的 User ID"
   ```

### 步驟 3: 配置學術平台

#### arXiv 配置示例

```yaml
platforms:
  # 按類別搜索
  - id: "arxiv_ai"
    name: "arXiv 人工智能"
    type: "arxiv"
    query: "cat:cs.AI"
    max_results: 30
  
  # 按關鍵詞搜索
  - id: "arxiv_llm"
    name: "arXiv 大語言模型"
    type: "arxiv"
    query: "all:large+language+model"
    max_results: 30
  
  # 複雜查詢
  - id: "arxiv_nlp"
    name: "arXiv NLP"
    type: "arxiv"
    query: "(cat:cs.CL+OR+cat:cs.LG)+AND+ti:transformer"
    max_results: 20
```

#### PubMed 配置示例

```yaml
platforms:
  - id: "pubmed_ai"
    name: "PubMed AI醫學"
    type: "pubmed"
    query: "artificial intelligence AND medicine"
    max_results: 20
    days_back: 7  # 獲取最近7天
  
  - id: "pubmed_cancer"
    name: "PubMed 癌症"
    type: "pubmed"
    query: "cancer therapy[Title]"
    max_results: 20
    days_back: 14
```

### 步驟 4: 配置關鍵詞過濾

編輯 `config/frequency_words.txt`:

```
# 你感興趣的研究主題
Large Language Model
LLM
GPT
Transformer
+training  # 必須包含 "training"
@15        # 最多顯示15篇

Computer Vision
Image
+deep learning

!survey    # 排除綜述
!review    # 排除評論
```

## 🚀 運行

### 本地運行

```bash
python main.py
```

### GitHub Actions 自動化

創建 `.github/workflows/academic-monitor.yml`:

```yaml
name: Academic Monitor

on:
  schedule:
    - cron: '0 1 * * *'  # 每天 UTC 1:00 (北京時間 9:00)
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run monitor
        env:
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          LINE_CHANNEL_ACCESS_TOKEN: ${{ secrets.LINE_CHANNEL_ACCESS_TOKEN }}
          LINE_USER_ID: ${{ secrets.LINE_USER_ID }}
        run: python main.py
```

在 GitHub Repository Settings → Secrets 中添加:
- `EMAIL_FROM`
- `EMAIL_PASSWORD`
- `EMAIL_TO`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_USER_ID`

### Docker 運行

```bash
# 構建鏡像
docker build -t trendradar-academic .

# 運行
docker run -d \
  -v ./config:/app/config \
  -v ./output:/app/output \
  -e EMAIL_FROM="your@email.com" \
  -e EMAIL_PASSWORD="password" \
  -e EMAIL_TO="recipient@email.com" \
  trendradar-academic
```

## 📊 查看結果

### HTML 報告

生成在 `output/日期/html/` 目錄:
- 用瀏覽器直接打開
- 支持移動端
- 可部署到 GitHub Pages

### Email

- HTML 格式，包含完整論文信息
- 點擊標題直接跳轉到論文頁面
- 支持多個收件人

### LINE

- Flex Message 卡片式展示
- 支持快速瀏覽
- 點擊 "查看論文" 按鈕打開原文

## 🔧 常見問題

### Q1: arXiv API 速率限制

**問題**: 請求過於頻繁導致失敗

**解決**:
```yaml
crawler:
  request_interval: 3000  # 增加間隔到3秒
```

### Q2: PubMed 無結果

**問題**: 查詢語法不正確或時間範圍太窄

**解決**:
- 檢查查詢語法
- 增加 `days_back: 30`
- 使用更通用的關鍵詞

### Q3: Gmail 無法發送

**問題**: 使用了賬戶密碼而非應用專用密碼

**解決**:
1. 開啟兩步驟驗證
2. 生成應用專用密碼
3. 使用應用專用密碼

### Q4: LINE 推送失敗

**問題**: Token 或 User ID 錯誤

**解決**:
- 確認 Channel Access Token 正確
- 確認已將 Bot 加為好友
- 檢查 User ID 格式

### Q5: 論文數量太多

**問題**: 每天收到太多論文

**解決**:
```yaml
# 方法1: 減少 max_results
platforms:
  - max_results: 10  # 減少到10篇

# 方法2: 使用關鍵詞過濾
# frequency_words.txt 中添加 @10

# 方法3: 使用更精確的查詢
query: "ti:specific+topic"  # 只搜索標題
```

## 📚 查詢語法參考

### arXiv

```yaml
# 類別搜索
query: "cat:cs.AI"
query: "cat:cs.CV"
query: "cat:cs.LG"

# 字段搜索
query: "ti:neural+network"      # 標題
query: "au:hinton"               # 作者
query: "abs:transformer"         # 摘要
query: "all:machine+learning"    # 所有字段

# 布爾運算
query: "ti:GPT+AND+cat:cs.CL"
query: "(cat:cs.AI+OR+cat:cs.LG)+AND+ti:transformer"
```

### PubMed

```yaml
# 簡單搜索
query: "machine learning"

# 布爾運算
query: "AI AND medicine"
query: "(cancer OR tumor) AND therapy"

# 字段限制
query: "COVID-19[Title]"
query: "Artificial Intelligence[MeSH]"

# 作者搜索
query: "Smith J[Author]"
```

## 💡 最佳實踐

1. **選擇合適的推送模式**
   - `daily`: 每日匯總（推薦）
   - `incremental`: 只推送新論文
   - `current`: 當前榜單

2. **合理設置數量**
   - arXiv: 20-50 篇/平台
   - PubMed: 10-30 篇/平台

3. **使用關鍵詞過濾**
   - 設置感興趣的研究方向
   - 使用過濾詞排除綜述

4. **定時執行**
   - 每天固定時間執行
   - 避免頻繁請求

## 🤝 需要幫助？

- 查看 [README-ACADEMIC.md](README-ACADEMIC.md) 完整文檔
- 參考配置示例文件
- 提交 GitHub Issue

## 🎉 開始使用！

```bash
# 1. 複製配置
cp config/config-academic-example.yaml config/config.yaml
cp config/frequency_words-academic-example.txt config/frequency_words.txt

# 2. 編輯配置文件，填入你的 Email 或 LINE 信息

# 3. 運行
python main.py

# 4. 檢查 output 目錄和郵箱/LINE
```
