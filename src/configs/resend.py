# src/configs/resend.py
import resend
from src.configs.settings import settings

resend.api_key = settings.RESEND_API_KEY
