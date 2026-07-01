from django.apps import AppConfig

class QuestionsConfig(AppConfig):
    name = 'questions'

    def ready(self):
        from . import signals
