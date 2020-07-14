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
    self.GetTodayMinuteData = channel.unary_unary(
        '/stock_api.Stock/GetTodayMinuteData',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosDayDatas.FromString,
        )
    self.GetPastMinuteData = channel.unary_unary(
        '/stock_api.Stock/GetPastMinuteData',
        request_serializer=stock__provider__pb2.PastMinuteQuery.SerializeToString,
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
    self.RequestOrder = channel.unary_unary(
        '/stock_api.Stock/RequestOrder',
        request_serializer=stock__provider__pb2.TradeMsg.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.SetCurrentStock = channel.unary_unary(
        '/stock_api.Stock/SetCurrentStock',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.SetCurrentDateTime = channel.unary_unary(
        '/stock_api.Stock/SetCurrentDateTime',
        request_serializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.GetCompanyName = channel.unary_unary(
        '/stock_api.Stock/GetCompanyName',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=stock__provider__pb2.CompanyName.FromString,
        )
    self.SetSimulationStatus = channel.unary_unary(
        '/stock_api.Stock/SetSimulationStatus',
        request_serializer=stock__provider__pb2.SimulationStatus.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.GetSimulationStatus = channel.unary_unary(
        '/stock_api.Stock/GetSimulationStatus',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.SimulationStatus.FromString,
        )
    self.GetFavoriteList = channel.unary_unary(
        '/stock_api.Stock/GetFavoriteList',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.CodeList.FromString,
        )
    self.AddFavorite = channel.unary_unary(
        '/stock_api.Stock/AddFavorite',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.RemoveFavorite = channel.unary_unary(
        '/stock_api.Stock/RemoveFavorite',
        request_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.GetYesterdayTopAmountList = channel.unary_unary(
        '/stock_api.Stock/GetYesterdayTopAmountList',
        request_serializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.SerializeToString,
        response_deserializer=stock__provider__pb2.TopList.FromString,
        )
    self.GetTodayTopAmountList = channel.unary_unary(
        '/stock_api.Stock/GetTodayTopAmountList',
        request_serializer=stock__provider__pb2.Option.SerializeToString,
        response_deserializer=stock__provider__pb2.CodeList.FromString,
        )
    self.GetRecentSearch = channel.unary_unary(
        '/stock_api.Stock/GetRecentSearch',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.CodeList.FromString,
        )
    self.GetViList = channel.unary_unary(
        '/stock_api.Stock/GetViList',
        request_serializer=stock__provider__pb2.Option.SerializeToString,
        response_deserializer=stock__provider__pb2.CodeList.FromString,
        )
    self.ListenCurrentStock = channel.unary_stream(
        '/stock_api.Stock/ListenCurrentStock',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
        )
    self.ListenListChanged = channel.unary_stream(
        '/stock_api.Stock/ListenListChanged',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.ListType.FromString,
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
    self.ListenCybosAlarm = channel.unary_stream(
        '/stock_api.Stock/ListenCybosAlarm',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.CybosStockAlarm.FromString,
        )
    self.ListenTraderMsg = channel.unary_stream(
        '/stock_api.Stock/ListenTraderMsg',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.TradeMsg.FromString,
        )
    self.ListenSimulationStatusChanged = channel.unary_stream(
        '/stock_api.Stock/ListenSimulationStatusChanged',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
        response_deserializer=stock__provider__pb2.SimulationStatus.FromString,
        )
    self.StartSimulation = channel.unary_stream(
        '/stock_api.Stock/StartSimulation',
        request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
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

  def GetTodayMinuteData(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetPastMinuteData(self, request, context):
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

  def RequestOrder(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SetCurrentStock(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SetCurrentDateTime(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetCompanyName(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SetSimulationStatus(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetSimulationStatus(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetFavoriteList(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def AddFavorite(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def RemoveFavorite(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetYesterdayTopAmountList(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetTodayTopAmountList(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetRecentSearch(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetViList(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenCurrentStock(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenListChanged(self, request, context):
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

  def ListenCybosAlarm(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenTraderMsg(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListenSimulationStatusChanged(self, request, context):
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
      'GetTodayMinuteData': grpc.unary_unary_rpc_method_handler(
          servicer.GetTodayMinuteData,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=stock__provider__pb2.CybosDayDatas.SerializeToString,
      ),
      'GetPastMinuteData': grpc.unary_unary_rpc_method_handler(
          servicer.GetPastMinuteData,
          request_deserializer=stock__provider__pb2.PastMinuteQuery.FromString,
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
      'RequestOrder': grpc.unary_unary_rpc_method_handler(
          servicer.RequestOrder,
          request_deserializer=stock__provider__pb2.TradeMsg.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'SetCurrentStock': grpc.unary_unary_rpc_method_handler(
          servicer.SetCurrentStock,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'SetCurrentDateTime': grpc.unary_unary_rpc_method_handler(
          servicer.SetCurrentDateTime,
          request_deserializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'GetCompanyName': grpc.unary_unary_rpc_method_handler(
          servicer.GetCompanyName,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=stock__provider__pb2.CompanyName.SerializeToString,
      ),
      'SetSimulationStatus': grpc.unary_unary_rpc_method_handler(
          servicer.SetSimulationStatus,
          request_deserializer=stock__provider__pb2.SimulationStatus.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'GetSimulationStatus': grpc.unary_unary_rpc_method_handler(
          servicer.GetSimulationStatus,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.SimulationStatus.SerializeToString,
      ),
      'GetFavoriteList': grpc.unary_unary_rpc_method_handler(
          servicer.GetFavoriteList,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.CodeList.SerializeToString,
      ),
      'AddFavorite': grpc.unary_unary_rpc_method_handler(
          servicer.AddFavorite,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'RemoveFavorite': grpc.unary_unary_rpc_method_handler(
          servicer.RemoveFavorite,
          request_deserializer=stock__provider__pb2.StockCodeQuery.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'GetYesterdayTopAmountList': grpc.unary_unary_rpc_method_handler(
          servicer.GetYesterdayTopAmountList,
          request_deserializer=google_dot_protobuf_dot_timestamp__pb2.Timestamp.FromString,
          response_serializer=stock__provider__pb2.TopList.SerializeToString,
      ),
      'GetTodayTopAmountList': grpc.unary_unary_rpc_method_handler(
          servicer.GetTodayTopAmountList,
          request_deserializer=stock__provider__pb2.Option.FromString,
          response_serializer=stock__provider__pb2.CodeList.SerializeToString,
      ),
      'GetRecentSearch': grpc.unary_unary_rpc_method_handler(
          servicer.GetRecentSearch,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.CodeList.SerializeToString,
      ),
      'GetViList': grpc.unary_unary_rpc_method_handler(
          servicer.GetViList,
          request_deserializer=stock__provider__pb2.Option.FromString,
          response_serializer=stock__provider__pb2.CodeList.SerializeToString,
      ),
      'ListenCurrentStock': grpc.unary_stream_rpc_method_handler(
          servicer.ListenCurrentStock,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.StockCodeQuery.SerializeToString,
      ),
      'ListenListChanged': grpc.unary_stream_rpc_method_handler(
          servicer.ListenListChanged,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.ListType.SerializeToString,
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
      'ListenCybosAlarm': grpc.unary_stream_rpc_method_handler(
          servicer.ListenCybosAlarm,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.CybosStockAlarm.SerializeToString,
      ),
      'ListenTraderMsg': grpc.unary_stream_rpc_method_handler(
          servicer.ListenTraderMsg,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.TradeMsg.SerializeToString,
      ),
      'ListenSimulationStatusChanged': grpc.unary_stream_rpc_method_handler(
          servicer.ListenSimulationStatusChanged,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
          response_serializer=stock__provider__pb2.SimulationStatus.SerializeToString,
      ),
      'StartSimulation': grpc.unary_stream_rpc_method_handler(
          servicer.StartSimulation,
          request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
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
