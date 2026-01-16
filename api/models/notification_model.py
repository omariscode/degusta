from django.db import models

class Notification(models.Model):
    title = models.CharField(max_length=40, null=False)
    content = models.TextField()

    customer = models.ForeignKey(
        "api.User", on_delete=models.CASCADE, related_name="notifications"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification #{self.id} - {self.title}"
