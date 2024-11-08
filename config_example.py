class Config:
    GOOGLE_CALENDAR_CONFIG = {
        'SERVICE_ACCOUNT_FILE': './service_account.json',
        'SCOPES': ['https://www.googleapis.com/auth/calendar'],
        'CALENDAR_ID': ''
    }
    
    EMAIL_CONFIG = {
        'EMAIL_ADDRESS': ',
        'EMAIL_PASSWORD': '',
        'SMTP_SERVER': '',
        'SMTP_PORT': 587,
        'REPLY_TO': ''
    }

    INVENTORY = {
        'Camera': 5,
        'Lens': 10,
        'Tripod': 4,
    }
