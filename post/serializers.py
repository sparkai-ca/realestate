from django.db.models import fields
from .models import Post
from rest_framework import serializers



class PostSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Post
        exclude = []
    def validate(self, attrs):
        return super().validate(attrs)


