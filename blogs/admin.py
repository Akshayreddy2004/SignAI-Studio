from django.contrib import admin
from .models import TranslationHistory

@admin.register(TranslationHistory)
class TranslationHistoryAdmin(admin.ModelAdmin):
    list_display = ('translation_type', 'user', 'input_text', 'output_result', 'timestamp')
    list_filter = ('translation_type', 'timestamp')
    search_fields = ('input_text', 'output_result')
