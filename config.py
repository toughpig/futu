import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenD Connection Settings
OPEND_HOST = os.getenv('FUTU_OPEND_HOST', '127.0.0.1')
OPEND_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

# Password Hashing Settings
USE_MD5_HASH = os.getenv('USE_MD5_HASH', 'True').lower() in ('true', '1', 't', 'yes')
IS_PASSWORD_HASHED = os.getenv('IS_PASSWORD_HASHED', 'False').lower() in ('true', '1', 't', 'yes')

# Trading Environment Settings
# 设置交易环境: 'REAL' 为真实交易, 'SIMULATE' 为模拟交易
TRADING_ENV = os.getenv('TRADING_ENV', 'SIMULATE').upper()
if TRADING_ENV not in ['REAL', 'SIMULATE']:
    print(f"Warning: Invalid TRADING_ENV value: {TRADING_ENV}. Defaulting to SIMULATE.")
    TRADING_ENV = 'SIMULATE'

# Account Credentials
ACCOUNT_ID = os.getenv('FUTU_ACCOUNT_ID', '')
ACCOUNT_PWD = os.getenv('FUTU_ACCOUNT_PWD', '')
TRADE_PWD = os.getenv('FUTU_TRADE_PWD', '')
UNLOCK_TRADE_PWD = os.getenv('FUTU_UNLOCK_TRADE_PWD', '')

# Verify if passwords are in MD5 format when IS_PASSWORD_HASHED is True
def is_md5_hash(s):
    """Check if a string matches MD5 hash format (32 hex characters)"""
    return bool(re.match(r'^[a-f0-9]{32}$', s.lower()))

if IS_PASSWORD_HASHED:
    # Verify that passwords follow MD5 format when claimed to be hashed
    if ACCOUNT_PWD and not is_md5_hash(ACCOUNT_PWD):
        print("Warning: FUTU_ACCOUNT_PWD does not appear to be an MD5 hash")
    if TRADE_PWD and not is_md5_hash(TRADE_PWD):
        print("Warning: FUTU_TRADE_PWD does not appear to be an MD5 hash")
    if UNLOCK_TRADE_PWD and not is_md5_hash(UNLOCK_TRADE_PWD):
        print("Warning: FUTU_UNLOCK_TRADE_PWD does not appear to be an MD5 hash")

# Security checks
if not all([ACCOUNT_ID, ACCOUNT_PWD]):
    print("Warning: Account credentials not fully configured in .env file")

# Market Data Settings
DEFAULT_MARKET = os.getenv('DEFAULT_MARKET', 'HK')
QUOTE_PUSH_INTERVAL_S = int(os.getenv('QUOTE_PUSH_INTERVAL_S', '3'))

# Market codes mapping
MARKET_MAP = {
    'HK': 'HK',      # Hong Kong
    'US': 'US',      # United States
    'CN': 'SH',      # China (Shanghai)
    'CN_SZ': 'SZ',   # China (Shenzhen)
    'SG': 'SG'       # Singapore
} 