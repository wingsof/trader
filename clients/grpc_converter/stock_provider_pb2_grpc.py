# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
import stock_provider_pb2 as stock__provider__pb2


class StockStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetDayData = channel.unary_unary(
        '/stock_api.Stock/GetDayData',
        request_serializer=stock__provider__pb2.StockQuery.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosDayDatas.FromString,
        )
    self.GetMinuteData = channel.unary_unary(
        '/stock_api.Stock/GetMinuteData',
        request_serializer=stock__provider__pb2.StockQuery.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosDayDatas.FromString,
        )
    self.RequestCybosTickData = channel.unary_unary(
        '/stock_api.Stock/RequestCybosTickData',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.RequestCybosBidAsk = channel.unary_unary(
        '/stock_api.Stock/RequestCybosBidAsk',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.RequestCybosSubject = channel.unary_unary(
        '/stock_api.Stock/RequestCybosSubject',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.GetYesterdayTopAmountCodes = channel.unary_unary(
        '/stock_api.Stock/GetYesterdayTopAmountCodes',
        request_serializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.SerializeToString,
        response_deserializer=stock__provider__pb2.CodeList.FromString,
        )
    self.ListenCybosTickData = channel.unary_stream(
        '/stock_api.Stock/ListenCybosTickData',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosTickData.FromString,
        )
    self.ListenCybosBidAsk = channel.unary_stream(
        '/stock_api.Stock/ListenCybosBidAsk',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosBidAskTickData.FromString,
        )
    self.ListenCurrentTime = channel.unary_stream(
        '/stock_api.Stock/ListenCurrentTime',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.FromString,
        )
    self.ListenCybosSubject = channel.unary_stream(
        '/stock_api.Stock/ListenCybosSubject',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosSubjectTickData.FromString,
        )
    self.StartSimulation = channel.unary_unary(
        '/stock_api.Stock/StartSimulation',
        request_serializer=stock__provider__pb2.SimulationArgument.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.StopSimulation = channel.unary_unary(
        '/stock_api.Stock/StopSimulation',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )


class StockServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetDayData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetMinuteData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RequestCybosTickData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RequestCybosBidAsk(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RequestCybosSubject(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetYesterdayTopAmountCodes(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenCybosTickData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenCybosBidAsk(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenCurrentTime(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenCybosSubject(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StartSimulation(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def StopSimulation(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_StockServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetDayData': grpc.unary_unary_rpc_method_handler(
          servicer.GetDayData,
          request_deserializer=stock__provider__pb2.StockQuery.FromString,
          response_serializer=stock__provider__pb2.CybosDayDatas.SerializeToString,
      ),
      'GetMinuteData': grpc.unary_unary_rpc_method_handler(
          servicer.GetMinuteData,
          request_deserializer=stock__provider__pb2.StockQuery.FromString,
          response_serializer=stock__provider__pb2.CybosDayDatas.SerializeToString,
      ),
      'RequestCybosTickData': grpc.unary_unary_rpc_method_handler(
          servicer.RequestCybosTickData,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'RequestCybosBidAsk': grpc.unary_unary_rpc_method_handler(
          servicer.RequestCybosBidAsk,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'RequestCybosSubject': grpc.unary_unary_rpc_method_handler(
          servicer.RequestCybosSubject,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'GetYesterdayTopAmountCodes': grpc.unary_unary_rpc_method_handler(
          servicer.GetYesterdayTopAmountCodes,
          request_deserializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.FromString,
          response_serializer=stock__provider__pb2.CodeList.SerializeToString,
      ),
      'ListenCybosTickData': grpc.unary_stream_rpc_method_handler(
          servicer.ListenCybosTickData,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.CybosTickData.SerializeToString,
      ),
      'ListenCybosBidAsk': grpc.unary_stream_rpc_method_handler(
          servicer.ListenCybosBidAsk,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.CybosBidAskTickData.SerializeToString,
      ),
      'ListenCurrentTime': grpc.unary_stream_rpc_method_handler(
          servicer.ListenCurrentTime,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.SerializeToString,
      ),
      'ListenCybosSubject': grpc.unary_stream_rpc_method_handler(
          servicer.ListenCybosSubject,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.CybosSubjectTickData.SerializeToString,
      ),
      'StartSimulation': grpc.unary_unary_rpc_method_handler(
          servicer.StartSimulation,
          request_deserializer=stock__provider__pb2.SimulationArgument.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'StopSimulation': grpc.unary_unary_rpc_method_handler(
          servicer.StopSimulation,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'stock_api.Stock', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
