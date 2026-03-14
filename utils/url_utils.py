"""URL 工具模块 - 提供 URL 解析和域名判断的公共方法."""
from urllib.parse import urlparse


# YouTube 域名列表
YOUTUBE_DOMAINS = ['youtube.com', 'youtu.be', 'youtube-nocookie.com']
# B站域名列表
BILIBILI_DOMAINS = ['bilibili.com', 'b23.tv']


def get_domain(url: str) -> str:
    """从 URL 中提取域名

    Args:
        url: 视频URL

    Returns:
        域名（不含端口号）
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if ':' in domain:
            domain = domain.split(':')[0]
        return domain
    except Exception:
        return ""


def is_youtube_url(url: str) -> bool:
    """判断是否是 YouTube URL

    Args:
        url: 视频URL

    Returns:
        是否是 YouTube
    """
    try:
        domain = get_domain(url)
        for yt_domain in YOUTUBE_DOMAINS:
            if yt_domain in domain or domain.endswith(yt_domain):
                return True
        return False
    except Exception:
        return False


def is_bilibili_url(url: str) -> bool:
    """判断是否是B站URL

    Args:
        url: 视频URL

    Returns:
        是否是B站
    """
    try:
        domain = get_domain(url)
        for bili_domain in BILIBILI_DOMAINS:
            if bili_domain in domain or domain.endswith(bili_domain):
                return True
        return False
    except Exception:
        return False


def should_use_proxy(url: str, proxy_enabled: bool) -> bool:
    """判断 URL 是否需要使用代理

    Args:
        url: 视频URL
        proxy_enabled: 是否启用代理

    Returns:
        是否需要代理
    """
    if not proxy_enabled:
        return False

    return is_youtube_url(url)
