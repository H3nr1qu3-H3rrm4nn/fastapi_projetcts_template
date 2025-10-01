"""
Utilitário para geração e validação de tokens seguros
====================================================

Este módulo fornece funcionalidades para gerar tokens seguros
para links públicos, evitando exposição de IDs diretos.
"""

import secrets
import string
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import pytz

# Timezone padrão do projeto
sp_tz = pytz.timezone("America/Sao_Paulo")

def get_current_datetime() -> datetime:
    """Obtém o datetime atual com timezone correto"""
    return datetime.now(sp_tz)


class SecurityTokens:
    """Classe para gerenciamento de tokens seguros"""
    
    @staticmethod
    def generate_public_token(booking_id: int, length: int = 32) -> str:
        """
        Gera um token seguro único para um booking
        
        Args:
            booking_id: ID do booking
            length: Tamanho do token (padrão: 32)
            
        Returns:
            Token seguro de 32 caracteres
        """
        # Gera uma string aleatória segura
        alphabet = string.ascii_letters + string.digits
        random_part = ''.join(secrets.choice(alphabet) for _ in range(length - 8))
        
        # Adiciona timestamp para garantir unicidade
        timestamp = str(int(datetime.now().timestamp()))[-8:]
        
        # Combina e gera hash final
        combined = f"{booking_id}_{random_part}_{timestamp}"
        token_hash = hashlib.sha256(combined.encode()).hexdigest()[:length]
        
        return token_hash
    
    @staticmethod
    def calculate_token_expiry(days: int = 7) -> datetime:
        """
        DEPRECATED: Tokens agora não expiram por tempo
        Mantido para compatibilidade, mas retorna None
        
        Returns:
            None (tokens não expiram mais por tempo)
        """
        return None
    
    @staticmethod
    def is_token_valid(token_expires_at: Optional[datetime]) -> bool:
        """
        Verifica se um token ainda é válido
        
        Args:
            token_expires_at: Data de expiração do token
            
        Returns:
            True se válido, False se expirado
        """
        if not token_expires_at:
            return False
        
        # Converter para datetime se for date
        if hasattr(token_expires_at, 'date') and not hasattr(token_expires_at, 'hour'):
            # É um objeto date, converter para datetime
            from datetime import time
            token_expires_at = datetime.combine(token_expires_at, time.max)
        elif isinstance(token_expires_at, str):
            # É uma string, tentar fazer parse
            try:
                token_expires_at = datetime.fromisoformat(token_expires_at.replace('Z', '+00:00'))
            except:
                return False
            
        return datetime.now() < token_expires_at
    
    @staticmethod
    def obfuscate_booking_id(booking_id: int) -> str:
        """
        Ofusca o ID do booking para logs
        
        Args:
            booking_id: ID do booking
            
        Returns:
            ID ofuscado para logs
        """
        return f"***{str(booking_id)[-3:]}"


# Funções de conveniência
def generate_secure_token(booking_id: int) -> tuple[str, None]:
    """
    Gera token seguro (sem expiração por tempo)
    
    Returns:
        Tupla com (token, None) - tokens não expiram mais por tempo
    """
    token = SecurityTokens.generate_public_token(booking_id)
    return token, None


def validate_token_expiry(expires_at: Optional[datetime]) -> bool:
    """
    DEPRECATED: Tokens não expiram mais por tempo
    Mantido para compatibilidade
    
    Returns:
        Sempre True (tokens não expiram por tempo)
    """
    return True
