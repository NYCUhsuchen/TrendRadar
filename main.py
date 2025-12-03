# coding=utf-8

import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pytz
import yaml

# 導入學術平台和 LINE 通知模組
try:
    from academic_fetcher import crawl_academic_platforms
    ACADEMIC_SUPPORT = True
except ImportError:
    ACADEMIC_SUPPORT = False
    print("警告: 未找到 academic_fetcher 模組，學術平台支持已禁用")

try:
    from line_notifier import send_to_line
    LINE_SUPPORT = True
except ImportError:
    LINE_SUPPORT = False
    print("警告: 未找到 line_notifier 模組，LINE 通知支持已禁用")


VERSION = "4.0.0-academic"


# === SMTP邮件配置 ===
SMTP_CONFIGS = {
    # Gmail（使用 STARTTLS）
    "gmail.com": {"server": "smtp.gmail.com", "port": 587, "encryption": "TLS"},
    # QQ邮箱（使用 SSL，更稳定）
    "qq.com": {"server": "smtp.qq.com", "port": 465, "encryption": "SSL"},
    # Outlook（使用 STARTTLS）
    "outlook.com": {
        "server": "smtp-mail.outlook.com",
        "port": 587,
        "encryption": "TLS",
    },
    "hotmail.com": {
        "server": "smtp-mail.outlook.com",
        "port": 587,
        "encryption": "TLS",
    },
    "live.com": {"server": "smtp-mail.outlook.com", "port": 587, "encryption": "TLS"},
    # 网易邮箱（使用 SSL，更稳定）
    "163.com": {"server": "smtp.163.com", "port": 465, "encryption": "SSL"},
    "126.com": {"server": "smtp.126.com", "port": 465, "encryption": "SSL"},
    # 新浪邮箱（使用 SSL）
    "sina.com": {"server": "smtp.sina.com", "port": 465, "encryption": "SSL"},
    # 搜狐邮箱（使用 SSL）
    "sohu.com": {"server": "smtp.sohu.com", "port": 465, "encryption": "SSL"},
    # 天翼邮箱（使用 SSL）
    "189.cn": {"server": "smtp.189.cn", "port": 465, "encryption": "SSL"},
    # 阿里云邮箱（使用 TLS）
    "aliyun.com": {"server": "smtp.aliyun.com", "port": 465, "encryption": "TLS"},
}


# === 配置管理 ===
def load_config():
    """加载配置文件"""
    config_path = os.environ.get("CONFIG_PATH", "config/config.yaml")

    if not Path(config_path).exists():
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    print(f"配置文件加载成功: {config_path}")

    # 构建配置 - 只保留學術和通知相關配置
    config = {
        "REQUEST_INTERVAL": config_data["crawler"]["request_interval"],
        "USE_PROXY": config_data["crawler"]["use_proxy"],
        "DEFAULT_PROXY": config_data["crawler"]["default_proxy"],
        "ENABLE_CRAWLER": os.environ.get("ENABLE_CRAWLER", "").strip().lower()
        in ("true", "1")
        if os.environ.get("ENABLE_CRAWLER", "").strip()
        else config_data["crawler"]["enable_crawler"],
        "ENABLE_NOTIFICATION": os.environ.get("ENABLE_NOTIFICATION", "").strip().lower()
        in ("true", "1")
        if os.environ.get("ENABLE_NOTIFICATION", "").strip()
        else config_data["notification"]["enable_notification"],
        "PLATFORMS": config_data["platforms"],
    }

    # 通知渠道配置（只保留 Email 和 LINE）
    notification = config_data.get("notification", {})
    webhooks = notification.get("webhooks", {})

    # 邮件配置
    config["EMAIL_FROM"] = os.environ.get("EMAIL_FROM", "").strip() or webhooks.get(
        "email_from", ""
    )
    config["EMAIL_PASSWORD"] = os.environ.get(
        "EMAIL_PASSWORD", ""
    ).strip() or webhooks.get("email_password", "")
    config["EMAIL_TO"] = os.environ.get("EMAIL_TO", "").strip() or webhooks.get(
        "email_to", ""
    )
    config["EMAIL_SMTP_SERVER"] = os.environ.get(
        "EMAIL_SMTP_SERVER", ""
    ).strip() or webhooks.get("email_smtp_server", "")
    config["EMAIL_SMTP_PORT"] = os.environ.get(
        "EMAIL_SMTP_PORT", ""
    ).strip() or webhooks.get("email_smtp_port", "")

    # LINE配置
    config["LINE_CHANNEL_ACCESS_TOKEN"] = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "").strip() or webhooks.get(
        "line_channel_access_token", ""
    )
    config["LINE_USER_ID"] = os.environ.get("LINE_USER_ID", "").strip() or webhooks.get(
        "line_user_id", ""
    )

    # 输出配置来源信息
    notification_sources = []
    if config["EMAIL_FROM"] and config["EMAIL_PASSWORD"] and config["EMAIL_TO"]:
        from_source = "环境变量" if os.environ.get("EMAIL_FROM") else "配置文件"
        notification_sources.append(f"邮件({from_source})")

    if config["LINE_CHANNEL_ACCESS_TOKEN"] and config["LINE_USER_ID"]:
        token_source = "环境变量" if os.environ.get("LINE_CHANNEL_ACCESS_TOKEN") else "配置文件"
        user_source = "环境变量" if os.environ.get("LINE_USER_ID") else "配置文件"
        notification_sources.append(f"LINE({token_source}/{user_source})")

    if notification_sources:
        print(f"通知渠道配置来源: {', '.join(notification_sources)}")
    else:
        print("未配置任何通知渠道")

    return config


print("正在加载配置...")
CONFIG = load_config()
print(f"TrendRadar Academic v{VERSION} 配置加载完成")
print(f"监控平台数量: {len(CONFIG['PLATFORMS'])}")


# === 工具函数 ===
def get_beijing_time():
    """获取北京时间"""
    return datetime.now(pytz.timezone("Asia/Shanghai"))


def format_date_folder():
    """格式化日期文件夹"""
    return get_beijing_time().strftime("%Y年%m月%d日")


def format_time_filename():
    """格式化时间文件名"""
    return get_beijing_time().strftime("%H时%M分")


def ensure_directory_exists(directory: str):
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_output_path(subfolder: str, filename: str) -> str:
    """获取输出路径"""
    date_folder = format_date_folder()
    output_dir = Path("output") / date_folder / subfolder
    ensure_directory_exists(str(output_dir))
    return str(output_dir / filename)


# === 數據保存 ===
def save_papers_to_file(results: Dict, id_to_name: Dict, failed_ids: List) -> str:
    """保存論文到文件"""
    file_path = get_output_path("txt", f"{format_time_filename()}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        for id_value, papers_data in results.items():
            # id | name 或 id
            name = id_to_name.get(id_value)
            if name and name != id_value:
                f.write(f"{id_value} | {name}\n")
            else:
                f.write(f"{id_value}\n")

            # 按排名排序論文
            for idx, (title, info) in enumerate(papers_data.items(), 1):
                url = info.get("url", "")
                mobile_url = info.get("mobileUrl", "")
                line = f"{idx}. {title}"
                
                if url:
                    line += f" [URL:{url}]"
                if mobile_url:
                    line += f" [MOBILE:{mobile_url}]"
                f.write(line + "\n")

            f.write("\n")

        if failed_ids:
            f.write("==== 以下平台請求失敗 ====\n")
            for id_value in failed_ids:
                f.write(f"{id_value}\n")

    return file_path


# === 郵件發送 ===
def send_to_email(
    from_email: str,
    password: str,
    to_email: str,
    report_type: str,
    html_content: str,
    custom_smtp_server: Optional[str] = None,
    custom_smtp_port: Optional[int] = None,
) -> bool:
    """发送邮件通知"""
    try:
        domain = from_email.split("@")[-1].lower()

        if custom_smtp_server and custom_smtp_port:
            # 使用自定义 SMTP 配置
            smtp_server = custom_smtp_server
            smtp_port = int(custom_smtp_port)
            # 根据端口判断加密方式：465=SSL, 587=TLS
            if smtp_port == 465:
                use_tls = False  # SSL 模式（SMTP_SSL）
            elif smtp_port == 587:
                use_tls = True   # TLS 模式（STARTTLS）
            else:
                # 其他端口优先尝试 TLS（更安全，更广泛支持）
                use_tls = True
        elif domain in SMTP_CONFIGS:
            # 使用预设配置
            config = SMTP_CONFIGS[domain]
            smtp_server = config["server"]
            smtp_port = config["port"]
            use_tls = config["encryption"] == "TLS"
        else:
            print(f"未识别的邮箱服务商: {domain}，使用通用 SMTP 配置")
            smtp_server = f"smtp.{domain}"
            smtp_port = 587
            use_tls = True

        msg = MIMEMultipart("alternative")

        # 严格按照 RFC 标准设置 From header
        sender_name = "TrendRadar Academic"
        msg["From"] = formataddr((sender_name, from_email))

        # 设置收件人
        recipients = [addr.strip() for addr in to_email.split(",")]
        if len(recipients) == 1:
            msg["To"] = recipients[0]
        else:
            msg["To"] = ", ".join(recipients)

        # 设置邮件主题
        now = get_beijing_time()
        subject = f"TrendRadar 學術論文報告 - {report_type} - {now.strftime('%m月%d日 %H:%M')}"
        msg["Subject"] = Header(subject, "utf-8")

        # 设置其他标准 header
        msg["MIME-Version"] = "1.0"
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        # 添加纯文本部分（作为备选）
        text_content = f"""
TrendRadar 學術論文報告
========================
報告類型：{report_type}
生成時間：{now.strftime('%Y-%m-%d %H:%M:%S')}

請使用支持HTML的郵件客戶端查看完整報告內容。
        """
        text_part = MIMEText(text_content, "plain", "utf-8")
        msg.attach(text_part)

        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        print(f"正在发送邮件到 {to_email}...")
        print(f"SMTP 服务器: {smtp_server}:{smtp_port}")
        print(f"发件人: {from_email}")

        try:
            if use_tls:
                # TLS 模式
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                server.set_debuglevel(0)  # 设为1可以查看详细调试信息
                server.ehlo()
                server.starttls()
                server.ehlo()
            else:
                # SSL 模式
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
                server.set_debuglevel(0)
                server.ehlo()

            # 登录
            server.login(from_email, password)

            # 发送邮件
            server.send_message(msg)
            server.quit()

            print(f"邮件发送成功 [{report_type}] -> {to_email}")
            return True

        except smtplib.SMTPServerDisconnected:
            print(f"邮件发送失败：服务器意外断开连接，请检查网络或稍后重试")
            return False

    except smtplib.SMTPAuthenticationError as e:
        print(f"邮件发送失败：认证错误，请检查邮箱和密码/授权码")
        print(f"详细错误: {str(e)}")
        return False
    except Exception as e:
        print(f"邮件发送失败 [{report_type}]：{e}")
        import traceback
        traceback.print_exc()
        return False


# === HTML 報告生成 ===
def generate_simple_html_report(results: Dict, id_to_name: Dict, failed_ids: List) -> str:
    """生成簡單的 HTML 報告"""
    now = get_beijing_time()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrendRadar 學術論文報告 - {now.strftime('%Y-%m-%d')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .timestamp {{
            margin-top: 10px;
            opacity: 0.9;
        }}
        .platform-section {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .platform-name {{
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .paper-item {{
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
            background: #f9f9f9;
            border-radius: 5px;
        }}
        .paper-title {{
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        .paper-link {{
            color: #667eea;
            text-decoration: none;
            margin-top: 8px;
            display: inline-block;
        }}
        .paper-link:hover {{
            text-decoration: underline;
        }}
        .failed-section {{
            background: #fff3cd;
            padding: 20px;
            margin-top: 20px;
            border-radius: 10px;
            border-left: 4px solid #ffc107;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 TrendRadar 學術論文報告</h1>
        <div class="timestamp">生成時間：{now.strftime('%Y年%m月%d日 %H:%M:%S')}</div>
    </div>
"""

    # 添加每個平台的論文
    for platform_id, papers_data in results.items():
        platform_name = id_to_name.get(platform_id, platform_id)
        html_content += f"""
    <div class="platform-section">
        <div class="platform-name">{platform_name} ({len(papers_data)} 篇論文)</div>
"""
        for idx, (title, info) in enumerate(papers_data.items(), 1):
            url = info.get("url", "")
            html_content += f"""
        <div class="paper-item">
            <div class="paper-title">{idx}. {title}</div>
"""
            if url:
                html_content += f"""
            <a href="{url}" class="paper-link" target="_blank">查看論文 →</a>
"""
            html_content += """
        </div>
"""
        html_content += """
    </div>
"""

    # 添加失敗的平台信息
    if failed_ids:
        html_content += """
    <div class="failed-section">
        <h3>⚠️ 以下平台請求失敗</h3>
        <ul>
"""
        for failed_id in failed_ids:
            html_content += f"            <li>{failed_id}</li>\n"
        html_content += """
        </ul>
    </div>
"""

    html_content += """
</body>
</html>
"""
    
    return html_content


# === 通知發送 ===
def send_notifications(results: Dict, id_to_name: Dict, failed_ids: List, html_content: str) -> Dict:
    """發送通知到配置的渠道"""
    notification_results = {}
    
    email_from = CONFIG.get("EMAIL_FROM", "")
    email_password = CONFIG.get("EMAIL_PASSWORD", "")
    email_to = CONFIG.get("EMAIL_TO", "")
    email_smtp_server = CONFIG.get("EMAIL_SMTP_SERVER", "")
    email_smtp_port = CONFIG.get("EMAIL_SMTP_PORT", "")
    
    line_channel_access_token = CONFIG.get("LINE_CHANNEL_ACCESS_TOKEN", "")
    line_user_id = CONFIG.get("LINE_USER_ID", "")
    
    proxy_url = CONFIG.get("DEFAULT_PROXY") if CONFIG.get("USE_PROXY") else None
    
    # 發送郵件
    if email_from and email_password and email_to:
        notification_results["email"] = send_to_email(
            email_from,
            email_password,
            email_to,
            "學術論文報告",
            html_content,
            email_smtp_server,
            email_smtp_port,
        )
    
    # 發送到 LINE
    if LINE_SUPPORT and line_channel_access_token and line_user_id:
        # 構建 LINE 需要的報告數據格式
        report_data = {
            "stats": [],
            "timestamp": get_beijing_time().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 將結果轉換為 stats 格式
        for platform_id, papers_data in results.items():
            platform_name = id_to_name.get(platform_id, platform_id)
            titles = []
            for title, info in papers_data.items():
                titles.append({
                    "title": title,
                    "source_name": platform_name,
                    "url": info.get("url", ""),
                })
            
            report_data["stats"].append({
                "word": platform_name,
                "count": len(papers_data),
                "titles": titles
            })
        
        notification_results["line"] = send_to_line(
            line_channel_access_token,
            line_user_id,
            report_data,
            "學術論文報告",
            proxy_url,
            use_flex=True,
        )
    
    if not notification_results:
        print("未配置任何通知渠道，跳過通知發送")
    
    return notification_results


# === 主分析器 ===
class AcademicMonitor:
    """學術論文監控器"""

    def __init__(self):
        self.request_interval = CONFIG["REQUEST_INTERVAL"]
        self.proxy_url = None
        self._setup_proxy()

    def _setup_proxy(self) -> None:
        """設置代理配置"""
        is_github_actions = os.environ.get("GITHUB_ACTIONS") == "true"
        if not is_github_actions and CONFIG["USE_PROXY"]:
            self.proxy_url = CONFIG["DEFAULT_PROXY"]
            print("本地環境，使用代理")
        elif not is_github_actions and not CONFIG["USE_PROXY"]:
            print("本地環境，未啟用代理")
        else:
            print("GitHub Actions環境，不使用代理")

    def _has_notification_configured(self) -> bool:
        """檢查是否配置了任何通知渠道"""
        return any(
            [
                (
                    CONFIG["EMAIL_FROM"]
                    and CONFIG["EMAIL_PASSWORD"]
                    and CONFIG["EMAIL_TO"]
                ),
                (CONFIG.get("LINE_CHANNEL_ACCESS_TOKEN") and CONFIG.get("LINE_USER_ID")),
            ]
        )

    def run(self) -> None:
        """執行監控流程"""
        try:
            now = get_beijing_time()
            print(f"當前北京時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")

            if not CONFIG["ENABLE_CRAWLER"]:
                print("爬蟲功能已禁用（ENABLE_CRAWLER=False），程序退出")
                return

            has_notification = self._has_notification_configured()
            if not CONFIG["ENABLE_NOTIFICATION"]:
                print("通知功能已禁用（ENABLE_NOTIFICATION=False），將只進行數據抓取")
            elif not has_notification:
                print("未配置任何通知渠道，將只進行數據抓取，不發送通知")
            else:
                print("通知功能已啟用，將發送通知")

            # 檢查是否有學術平台配置
            if not ACADEMIC_SUPPORT:
                print("❌ 未找到 academic_fetcher 模組，無法執行")
                return
            
            academic_platforms = [p for p in CONFIG["PLATFORMS"] if p.get('type') in ['arxiv', 'pubmed']]
            
            if not academic_platforms:
                print("❌ 未配置任何學術平台")
                return
            
            print(f"配置的學術平台: {[p.get('name', p['id']) for p in academic_platforms]}")
            print(f"開始爬取數據，請求間隔 {self.request_interval} 毫秒")
            ensure_directory_exists("output")

            # 爬取學術平台數據
            results, id_to_name, failed_ids = crawl_academic_platforms(
                academic_platforms,
                self.request_interval,
                self.proxy_url
            )

            if not results:
                print("未獲取到任何論文數據")
                return

            # 保存到文件
            title_file = save_papers_to_file(results, id_to_name, failed_ids)
            print(f"論文已保存到: {title_file}")

            # 生成 HTML 報告
            html_content = generate_simple_html_report(results, id_to_name, failed_ids)
            html_file = get_output_path("html", f"{format_time_filename()}.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"HTML 報告已生成: {html_file}")

            # 發送通知
            if CONFIG["ENABLE_NOTIFICATION"] and has_notification:
                send_notifications(results, id_to_name, failed_ids, html_content)

        except Exception as e:
            print(f"監控流程執行出錯: {e}")
            raise


def main():
    try:
        monitor = AcademicMonitor()
        monitor.run()
    except FileNotFoundError as e:
        print(f"❌ 配置文件錯誤: {e}")
        print("\n請確保以下文件存在:")
        print("  • config/config.yaml")
        print("\n參考項目文檔進行正確配置")
    except Exception as e:
        print(f"❌ 程序運行錯誤: {e}")
        raise


if __name__ == "__main__":
    main()
