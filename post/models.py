from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.fields import CharField
import uuid
from enum import Enum


User = get_user_model()


class Post(models.Model):
    class StatusType(Enum):
        DELIVERED = 1
        BLOCKED = 0

    POSTSTATUSES = (
        (StatusType.DELIVERED.value, 'DELIVERED'),
        (StatusType.BLOCKED.value, 'BLOCKED'),
    )

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False, )
    postuserid = models.ForeignKey(User, on_delete=models.CASCADE)
    postusername = CharField(max_length=100, default="admin")
    postmessage = CharField(null=False, blank=False, max_length=5000)
    poststatus = models.IntegerField(choices=POSTSTATUSES, default=POSTSTATUSES[0][0])
    is_allowed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


