from . import settings, connection

settings.warn_on_missing_local_settings()
conn = connection.Connection()