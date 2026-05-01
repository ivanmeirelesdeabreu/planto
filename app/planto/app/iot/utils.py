import hashlib
import secrets
from django.conf import settings


def gerar_token_plano(tamanho_bytes: int = 24) -> str:
    """Gera um token aleatório (texto) para o dispositivo."""
    return secrets.token_urlsafe(tamanho_bytes)


def hash_token(token_plano: str) -> str:
    """Gera hash SHA-256 do token (com pepper) para armazenamento no banco."""
    pepper = getattr(settings, 'DEVICE_TOKEN_PEPPER', settings.SECRET_KEY)
    base = (token_plano + '|' + str(pepper)).encode('utf-8')
    return hashlib.sha256(base).hexdigest()
