from django.apps import AppConfig


class QrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qr'
    def ready(self):
        import qr.signals
