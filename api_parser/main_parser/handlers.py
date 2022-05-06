from .services import ParserService
from .parser_pb2_grpc import add_ParserServiceServicer_to_server


def grpc_handlers(server):
    add_ParserServiceServicer_to_server(ParserService.as_servicer(), server)
