from django.db import models


class ReferralSource(models.TextChoices):
    TIKTOK = "tiktok", "TikTok"
    INSTAGRAM = "instagram", "Instagram"
    FACEBOOK = "facebook", "Facebook"
    TWITTER = "twitter", "Twitter (X)"
    FRIENDS_FAMILY = "friends_family", "Família ou Amigos"
    OTHER = "other", "Outro"


class UserReferral(models.Model):
    source = models.CharField(
        max_length=50,
        choices=ReferralSource.choices,
        verbose_name="Como conheceu a plataforma",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_source_display()
