from src.modules.urls.user.models import LinkUrl


# Helper function to return the list of the payload
def get_user_url_payload(link_url: LinkUrl):
    return {
        "link_url_id": str(link_url.link_url_id),
        "long_url": link_url.long_url,
        "short_url": f"https://tj.url.shortner/{link_url.short_code}",
        "expires_at": link_url.expires_at.isoformat(),
    }
