import uuid


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = uuid.uuid4().hex


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
