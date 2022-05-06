from django_grpc_framework.services import Service

from .models import Article
from .serializers import ArticleProtoSerializer


class ParserService(Service):

    def ListArticle(self, request, context):
        articles = Article.objects.all()
        serializer = ArticleProtoSerializer(articles, many=True)
        for article in serializer.message:
            yield article
