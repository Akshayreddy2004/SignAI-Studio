from django.db import models
from django.contrib.auth.models import User

class TranslationHistory(models.Model):
    TRANSLATION_TYPES = [
        ('AUDIO_TO_SIGN', 'Audio to Sign Language'),
        ('SIGN_TO_AUDIO', 'Sign Language to Audio'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='translations')
    translation_type = models.CharField(max_length=20, choices=TRANSLATION_TYPES)
    input_text = models.TextField(help_text="Spoken phrase or detected gesture")
    output_result = models.TextField(help_text="Matched ISL animation or spoken audio text")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_translation_type_display()} by {self.user or 'Guest'} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
