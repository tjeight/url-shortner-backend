from src.modules.analytics.users.models import URLClick


# Function to handle the payload of the user clicks
def get_user_click_payload(click: URLClick) -> dict:
    return {
        "url_click_id": str(click.url_click_id),
        "link_url_id": str(click.link_url_id),
        "ip_address": click.ip_address or "",
        "user_agent": click.user_agent or "",
        "clicked_at": click.clicked_at.isoformat() or "",
    }
