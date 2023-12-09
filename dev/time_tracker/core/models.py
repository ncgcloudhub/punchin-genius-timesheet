from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
# Create your models here.




class PunchinUser(AbstractUser):
    # Add any additional fields here
    pass

class TimeEntry(models.Model):
    #user = models.ForeignKey(PunchinUser, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    project = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.clock_in}"


