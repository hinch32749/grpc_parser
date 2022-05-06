import grpc
from main_parser import parser_pb2, parser_pb2_grpc


with grpc.insecure_channel('localhost:50051') as channel:
    stub = parser_pb2_grpc.ParserServiceStub(channel)
    print('--List--')
    articles = stub.ListArticle(parser_pb2.ListRequest())
    for article in articles:
        print(article.title)
        print('======================')