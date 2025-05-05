from django.apps import AppConfig


class IndiegoNewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'indiego_news'

    def ready(self):
        import indiego_news.signals
