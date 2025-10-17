# jobs/models.py
from django.conf import settings
from django.db import models


class LanguageReviewStatus(models.TextChoices):
    PENDING = 'pending', 'Pendiente'
    REVIEWED = 'reviewed', 'Revisado'


class LanguageReview(models.Model):
    job = models.ForeignKey(
        'companies.Job',
        on_delete=models.CASCADE,
        related_name='language_reviews'
    )
    status = models.CharField(
        max_length=20,
        choices=LanguageReviewStatus.choices,
        default=LanguageReviewStatus.PENDING
    )
    issues_found = models.JSONField(default=dict)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']