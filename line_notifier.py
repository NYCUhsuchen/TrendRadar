# coding=utf-8
"""
LINE Messaging API 通知模組
支持向 LINE 用戶或群組發送消息
"""

import requests
from typing import Optional, Dict


# 常量定義
LINE_TEXT_LIMIT = 5000  # LINE 文本消息長度限制
MAX_FLEX_CARDS = 10     # Flex Message 最大卡片數
MAX_AUTHORS_DISPLAY = 3 # 顯示的最大作者數
TITLE_DISPLAY_LENGTH = 80  # 標題顯示長度


class LineNotifier:
    """LINE Messaging API 通知器"""
    
    def __init__(self, channel_access_token: str, proxy_url: Optional[str] = None):
        """
        初始化 LINE 通知器
        
        Args:
            channel_access_token: LINE Channel Access Token
            proxy_url: 代理 URL（可選）
        """
        self.channel_access_token = channel_access_token
        self.api_url = "https://api.line.me/v2/bot/message/push"
        self.proxies = None
        if proxy_url:
            self.proxies = {"http": proxy_url, "https": proxy_url}
    
    def send_text_message(
        self,
        to: str,
        text: str
    ) -> bool:
        """
        發送文本消息
        
        Args:
            to: 接收者 ID（用戶 ID 或群組 ID）
            text: 消息文本
        
        Returns:
            是否發送成功
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_access_token}"
        }
        
        payload = {
            "to": to,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                proxies=self.proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"LINE 消息發送成功")
                return True
            else:
                print(f"LINE 消息發送失敗，狀態碼: {response.status_code}")
                print(f"響應: {response.text}")
                return False
                
        except Exception as e:
            print(f"LINE 消息發送出錯: {e}")
            return False
    
    def send_flex_message(
        self,
        to: str,
        alt_text: str,
        flex_content: Dict
    ) -> bool:
        """
        發送 Flex Message（支持更豐富的格式）
        
        Args:
            to: 接收者 ID
            alt_text: 替代文本（用於通知預覽）
            flex_content: Flex Message 內容
        
        Returns:
            是否發送成功
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_access_token}"
        }
        
        payload = {
            "to": to,
            "messages": [
                {
                    "type": "flex",
                    "altText": alt_text,
                    "contents": flex_content
                }
            ]
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                proxies=self.proxies,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"LINE Flex 消息發送成功")
                return True
            else:
                print(f"LINE Flex 消息發送失敗，狀態碼: {response.status_code}")
                print(f"響應: {response.text}")
                return False
                
        except Exception as e:
            print(f"LINE Flex 消息發送出錯: {e}")
            return False


def create_paper_flex_message(papers_data: Dict) -> Dict:
    """
    創建學術論文的 Flex Message 格式
    
    Args:
        papers_data: 論文數據
    
    Returns:
        Flex Message 內容
    """
    bubbles = []
    
    # 只顯示前 MAX_FLEX_CARDS 篇論文，避免消息過長
    stats = papers_data.get('stats', [])
    count = 0
    
    for stat in stats:
        if count >= MAX_FLEX_CARDS:
            break
            
        for title_data in stat.get('titles', []):
            if count >= MAX_FLEX_CARDS:
                break
            
            title = title_data.get('title', '')
            source_name = title_data.get('source_name', '')
            url = title_data.get('url', '')
            
            # 截斷過長的標題
            if len(title) > TITLE_DISPLAY_LENGTH:
                title = title[:TITLE_DISPLAY_LENGTH-3] + "..."
            
            bubble = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": source_name,
                            "weight": "bold",
                            "size": "sm",
                            "color": "#1DB446"
                        },
                        {
                            "type": "text",
                            "text": title,
                            "weight": "bold",
                            "size": "md",
                            "wrap": True,
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "link",
                            "height": "sm",
                            "action": {
                                "type": "uri",
                                "label": "查看論文",
                                "uri": url if url else "https://arxiv.org"
                            }
                        }
                    ],
                    "flex": 0
                }
            }
            
            bubbles.append(bubble)
            count += 1
    
    # 構建 Carousel
    flex_content = {
        "type": "carousel",
        "contents": bubbles if bubbles else [
            {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "暫無論文更新",
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }
    
    return flex_content


def send_to_line(
    channel_access_token: str,
    user_id: str,
    report_data: Dict,
    report_type: str,
    proxy_url: Optional[str] = None,
    use_flex: bool = True
) -> bool:
    """
    發送學術論文報告到 LINE
    
    Args:
        channel_access_token: LINE Channel Access Token
        user_id: LINE 用戶 ID 或群組 ID
        report_data: 報告數據
        report_type: 報告類型
        proxy_url: 代理 URL
        use_flex: 是否使用 Flex Message（推薦）
    
    Returns:
        是否發送成功
    """
    notifier = LineNotifier(channel_access_token, proxy_url)
    
    if use_flex:
        # 使用 Flex Message
        alt_text = f"TrendRadar 學術論文報告 - {report_type}"
        flex_content = create_paper_flex_message(report_data)
        
        return notifier.send_flex_message(user_id, alt_text, flex_content)
    else:
        # 使用純文本消息
        text = format_text_message(report_data, report_type)
        
        # LINE 文本消息限制
        if len(text) > LINE_TEXT_LIMIT:
            text = text[:LINE_TEXT_LIMIT-3] + "..."
            
        return notifier.send_text_message(user_id, text)


def format_text_message(report_data: Dict, report_type: str) -> str:
    """
    格式化文本消息
    
    Args:
        report_data: 報告數據
        report_type: 報告類型
    
    Returns:
        格式化後的文本
    """
    lines = []
    lines.append(f"📚 TrendRadar 學術論文報告")
    lines.append(f"類型: {report_type}")
    lines.append("")
    
    stats = report_data.get('stats', [])
    
    for stat in stats:
        word = stat.get('word', '')
        count = stat.get('count', 0)
        
        if count > 0:
            lines.append(f"🔍 {word}: {count} 篇")
            lines.append("")
            
            for idx, title_data in enumerate(stat.get('titles', [])[:5], 1):  # 只顯示前 5 篇
                title = title_data.get('title', '')
                source_name = title_data.get('source_name', '')
                url = title_data.get('url', '')
                
                # 截斷標題
                if len(title) > TITLE_DISPLAY_LENGTH:
                    title = title[:TITLE_DISPLAY_LENGTH-3] + "..."
                
                lines.append(f"{idx}. [{source_name}] {title}")
                if url:
                    lines.append(f"   {url}")
                lines.append("")
    
    lines.append(f"⏰ {report_data.get('timestamp', '')}")
    
    return "\n".join(lines)
