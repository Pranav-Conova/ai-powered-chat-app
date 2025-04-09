from django.apps import AppConfig


class ChatAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_app'

    def ready(self):
        from . import topic_manager
        topic_manager.start_topic_thread()