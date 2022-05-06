from rest_framework import serializers
from django_grpc_framework import proto_serializers
from .models import Article
from .parser_pb2 import ArticleList


class ArticleProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Article
        proto_class = ArticleList
        fields = [
            'id',
            'source_url',
            'title',
            'date_time',
            'image',
            'description'
        ]


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'source_url',
            'title',
            'date_time',
            'image',
            'description'
        ]
