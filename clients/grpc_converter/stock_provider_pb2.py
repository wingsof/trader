# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: stock_provider.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='stock_provider.proto',
  package='stock_api',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=b'\n\x14stock_provider.proto\x12\tstock_api\x1a\x1fgoogle/protobuf/timestamp.proto\"\x1e\n\x0eStockCodeQuery\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\"\x81\x01\n\nStockQuery\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\x12\x31\n\rfrom_datetime\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x32\n\x0euntil_datetime\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\xc4\x02\n\x0c\x43ybosDayData\x12\x0c\n\x04time\x18\x01 \x01(\r\x12\x13\n\x0bstart_price\x18\x02 \x01(\r\x12\x15\n\rhighest_price\x18\x03 \x01(\r\x12\x14\n\x0clowest_price\x18\x04 \x01(\r\x12\x13\n\x0b\x63lose_price\x18\x05 \x01(\r\x12\x0e\n\x06volume\x18\x06 \x01(\x04\x12\x0e\n\x06\x61mount\x18\x07 \x01(\x04\x12\x17\n\x0f\x63um_sell_volume\x18\x08 \x01(\x04\x12\x16\n\x0e\x63um_buy_volume\x18\t \x01(\x04\x12\x1d\n\x15\x66oreigner_hold_volume\x18\n \x01(\x03\x12\x1b\n\x13\x66oreigner_hold_rate\x18\x0b \x01(\x02\x12\x1e\n\x16institution_buy_volume\x18\x0c \x01(\x03\x12\"\n\x1ainstitution_cum_buy_volume\x18\r \x01(\x03\":\n\rCybosDayDatas\x12)\n\x08\x64\x61y_data\x18\x01 \x03(\x0b\x32\x17.stock_api.CybosDayData\"\xa6\x04\n\rCybosTickData\x12-\n\ttick_date\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x14\n\x0c\x63ompany_name\x18\x03 \x01(\t\x12\x16\n\x0eyesterday_diff\x18\x04 \x01(\x05\x12\x0c\n\x04time\x18\x05 \x01(\r\x12\x13\n\x0bstart_price\x18\x06 \x01(\r\x12\x15\n\rhighest_price\x18\x07 \x01(\r\x12\x14\n\x0clowest_price\x18\x08 \x01(\r\x12\x11\n\task_price\x18\t \x01(\r\x12\x11\n\tbid_price\x18\n \x01(\r\x12\x12\n\ncum_volume\x18\x0b \x01(\x04\x12\x12\n\ncum_amount\x18\x0c \x01(\x04\x12\x15\n\rcurrent_price\x18\r \x01(\r\x12\x13\n\x0b\x62uy_or_sell\x18\x0e \x01(\x08\x12 \n\x18\x63um_sell_volume_by_price\x18\x0f \x01(\x04\x12\x1f\n\x17\x63um_buy_volume_by_price\x18\x10 \x01(\x04\x12\x0e\n\x06volume\x18\x11 \x01(\x04\x12\x15\n\rtime_with_sec\x18\x12 \x01(\r\x12\x17\n\x0fmarket_type_exp\x18\x13 \x01(\r\x12\x13\n\x0bmarket_type\x18\x14 \x01(\r\x12\x17\n\x0fout_time_volume\x18\x15 \x01(\x04\x12\x17\n\x0f\x63um_sell_volume\x18\x16 \x01(\x04\x12\x16\n\x0e\x63um_buy_volume\x18\x17 \x01(\x04\"\xf0\x05\n\x13\x43ybosBidAskTickData\x12-\n\ttick_date\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x0c\n\x04time\x18\x03 \x01(\r\x12\x0e\n\x06volume\x18\x04 \x01(\x04\x12\x17\n\x0f\x66irst_ask_price\x18\x05 \x01(\r\x12\x17\n\x0f\x66irst_bid_price\x18\x06 \x01(\r\x12\x18\n\x10\x66irst_ask_remain\x18\x07 \x01(\r\x12\x18\n\x10\x66irst_bid_remain\x18\x08 \x01(\r\x12\x18\n\x10second_ask_price\x18\t \x01(\r\x12\x18\n\x10second_bid_price\x18\n \x01(\r\x12\x19\n\x11second_ask_remain\x18\x0b \x01(\r\x12\x19\n\x11second_bid_remain\x18\x0c \x01(\r\x12\x17\n\x0fthird_ask_price\x18\r \x01(\r\x12\x17\n\x0fthird_bid_price\x18\x0e \x01(\r\x12\x18\n\x10third_ask_remain\x18\x0f \x01(\r\x12\x18\n\x10third_bid_remain\x18\x10 \x01(\r\x12\x18\n\x10\x66ourth_ask_price\x18\x11 \x01(\r\x12\x18\n\x10\x66ourth_bid_price\x18\x12 \x01(\r\x12\x19\n\x11\x66ourth_ask_remain\x18\x13 \x01(\r\x12\x19\n\x11\x66ourth_bid_remain\x18\x14 \x01(\r\x12\x17\n\x0f\x66ifth_ask_price\x18\x15 \x01(\r\x12\x17\n\x0f\x66ifth_bid_price\x18\x16 \x01(\r\x12\x18\n\x10\x66ifth_ask_remain\x18\x17 \x01(\r\x12\x18\n\x10\x66ifth_bid_remain\x18\x18 \x01(\r\x12\x18\n\x10total_ask_remain\x18\x19 \x01(\x04\x12\x18\n\x10total_bid_remain\x18\x1a \x01(\x04\x12!\n\x19out_time_total_ask_remain\x18\x1b \x01(\x03\x12!\n\x19out_time_total_bid_remain\x18\x1c \x01(\x03\x32\xe5\x01\n\x05Stock\x12?\n\nGetDayData\x12\x15.stock_api.StockQuery\x1a\x18.stock_api.CybosDayDatas\"\x00\x12I\n\x0eSubscribeStock\x12\x19.stock_api.StockCodeQuery\x1a\x18.stock_api.CybosTickData\"\x00\x30\x01\x12P\n\x0fSubscribeBidAsk\x12\x19.stock_api.StockCodeQuery\x1a\x1e.stock_api.CybosBidAskTickData\"\x00\x30\x01\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])




_STOCKCODEQUERY = _descriptor.Descriptor(
  name='StockCodeQuery',
  full_name='stock_api.StockCodeQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='stock_api.StockCodeQuery.code', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=68,
  serialized_end=98,
)


_STOCKQUERY = _descriptor.Descriptor(
  name='StockQuery',
  full_name='stock_api.StockQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='stock_api.StockQuery.code', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='from_datetime', full_name='stock_api.StockQuery.from_datetime', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='until_datetime', full_name='stock_api.StockQuery.until_datetime', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=101,
  serialized_end=230,
)


_CYBOSDAYDATA = _descriptor.Descriptor(
  name='CybosDayData',
  full_name='stock_api.CybosDayData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='time', full_name='stock_api.CybosDayData.time', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='start_price', full_name='stock_api.CybosDayData.start_price', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='highest_price', full_name='stock_api.CybosDayData.highest_price', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lowest_price', full_name='stock_api.CybosDayData.lowest_price', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='close_price', full_name='stock_api.CybosDayData.close_price', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='volume', full_name='stock_api.CybosDayData.volume', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='amount', full_name='stock_api.CybosDayData.amount', index=6,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_sell_volume', full_name='stock_api.CybosDayData.cum_sell_volume', index=7,
      number=8, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_buy_volume', full_name='stock_api.CybosDayData.cum_buy_volume', index=8,
      number=9, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='foreigner_hold_volume', full_name='stock_api.CybosDayData.foreigner_hold_volume', index=9,
      number=10, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='foreigner_hold_rate', full_name='stock_api.CybosDayData.foreigner_hold_rate', index=10,
      number=11, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='institution_buy_volume', full_name='stock_api.CybosDayData.institution_buy_volume', index=11,
      number=12, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='institution_cum_buy_volume', full_name='stock_api.CybosDayData.institution_cum_buy_volume', index=12,
      number=13, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=233,
  serialized_end=557,
)


_CYBOSDAYDATAS = _descriptor.Descriptor(
  name='CybosDayDatas',
  full_name='stock_api.CybosDayDatas',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='day_data', full_name='stock_api.CybosDayDatas.day_data', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=559,
  serialized_end=617,
)


_CYBOSTICKDATA = _descriptor.Descriptor(
  name='CybosTickData',
  full_name='stock_api.CybosTickData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tick_date', full_name='stock_api.CybosTickData.tick_date', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='code', full_name='stock_api.CybosTickData.code', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='company_name', full_name='stock_api.CybosTickData.company_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='yesterday_diff', full_name='stock_api.CybosTickData.yesterday_diff', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='time', full_name='stock_api.CybosTickData.time', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='start_price', full_name='stock_api.CybosTickData.start_price', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='highest_price', full_name='stock_api.CybosTickData.highest_price', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lowest_price', full_name='stock_api.CybosTickData.lowest_price', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ask_price', full_name='stock_api.CybosTickData.ask_price', index=8,
      number=9, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='bid_price', full_name='stock_api.CybosTickData.bid_price', index=9,
      number=10, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_volume', full_name='stock_api.CybosTickData.cum_volume', index=10,
      number=11, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_amount', full_name='stock_api.CybosTickData.cum_amount', index=11,
      number=12, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='current_price', full_name='stock_api.CybosTickData.current_price', index=12,
      number=13, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='buy_or_sell', full_name='stock_api.CybosTickData.buy_or_sell', index=13,
      number=14, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_sell_volume_by_price', full_name='stock_api.CybosTickData.cum_sell_volume_by_price', index=14,
      number=15, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_buy_volume_by_price', full_name='stock_api.CybosTickData.cum_buy_volume_by_price', index=15,
      number=16, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='volume', full_name='stock_api.CybosTickData.volume', index=16,
      number=17, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='time_with_sec', full_name='stock_api.CybosTickData.time_with_sec', index=17,
      number=18, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='market_type_exp', full_name='stock_api.CybosTickData.market_type_exp', index=18,
      number=19, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='market_type', full_name='stock_api.CybosTickData.market_type', index=19,
      number=20, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='out_time_volume', full_name='stock_api.CybosTickData.out_time_volume', index=20,
      number=21, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_sell_volume', full_name='stock_api.CybosTickData.cum_sell_volume', index=21,
      number=22, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cum_buy_volume', full_name='stock_api.CybosTickData.cum_buy_volume', index=22,
      number=23, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=620,
  serialized_end=1170,
)


_CYBOSBIDASKTICKDATA = _descriptor.Descriptor(
  name='CybosBidAskTickData',
  full_name='stock_api.CybosBidAskTickData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tick_date', full_name='stock_api.CybosBidAskTickData.tick_date', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='code', full_name='stock_api.CybosBidAskTickData.code', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='time', full_name='stock_api.CybosBidAskTickData.time', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='volume', full_name='stock_api.CybosBidAskTickData.volume', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='first_ask_price', full_name='stock_api.CybosBidAskTickData.first_ask_price', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='first_bid_price', full_name='stock_api.CybosBidAskTickData.first_bid_price', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='first_ask_remain', full_name='stock_api.CybosBidAskTickData.first_ask_remain', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='first_bid_remain', full_name='stock_api.CybosBidAskTickData.first_bid_remain', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='second_ask_price', full_name='stock_api.CybosBidAskTickData.second_ask_price', index=8,
      number=9, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='second_bid_price', full_name='stock_api.CybosBidAskTickData.second_bid_price', index=9,
      number=10, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='second_ask_remain', full_name='stock_api.CybosBidAskTickData.second_ask_remain', index=10,
      number=11, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='second_bid_remain', full_name='stock_api.CybosBidAskTickData.second_bid_remain', index=11,
      number=12, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='third_ask_price', full_name='stock_api.CybosBidAskTickData.third_ask_price', index=12,
      number=13, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='third_bid_price', full_name='stock_api.CybosBidAskTickData.third_bid_price', index=13,
      number=14, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='third_ask_remain', full_name='stock_api.CybosBidAskTickData.third_ask_remain', index=14,
      number=15, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='third_bid_remain', full_name='stock_api.CybosBidAskTickData.third_bid_remain', index=15,
      number=16, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fourth_ask_price', full_name='stock_api.CybosBidAskTickData.fourth_ask_price', index=16,
      number=17, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fourth_bid_price', full_name='stock_api.CybosBidAskTickData.fourth_bid_price', index=17,
      number=18, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fourth_ask_remain', full_name='stock_api.CybosBidAskTickData.fourth_ask_remain', index=18,
      number=19, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fourth_bid_remain', full_name='stock_api.CybosBidAskTickData.fourth_bid_remain', index=19,
      number=20, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fifth_ask_price', full_name='stock_api.CybosBidAskTickData.fifth_ask_price', index=20,
      number=21, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fifth_bid_price', full_name='stock_api.CybosBidAskTickData.fifth_bid_price', index=21,
      number=22, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fifth_ask_remain', full_name='stock_api.CybosBidAskTickData.fifth_ask_remain', index=22,
      number=23, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fifth_bid_remain', full_name='stock_api.CybosBidAskTickData.fifth_bid_remain', index=23,
      number=24, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_ask_remain', full_name='stock_api.CybosBidAskTickData.total_ask_remain', index=24,
      number=25, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_bid_remain', full_name='stock_api.CybosBidAskTickData.total_bid_remain', index=25,
      number=26, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='out_time_total_ask_remain', full_name='stock_api.CybosBidAskTickData.out_time_total_ask_remain', index=26,
      number=27, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='out_time_total_bid_remain', full_name='stock_api.CybosBidAskTickData.out_time_total_bid_remain', index=27,
      number=28, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1173,
  serialized_end=1925,
)

_STOCKQUERY.fields_by_name['from_datetime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_STOCKQUERY.fields_by_name['until_datetime'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_CYBOSDAYDATAS.fields_by_name['day_data'].message_type = _CYBOSDAYDATA
_CYBOSTICKDATA.fields_by_name['tick_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_CYBOSBIDASKTICKDATA.fields_by_name['tick_date'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['StockCodeQuery'] = _STOCKCODEQUERY
DESCRIPTOR.message_types_by_name['StockQuery'] = _STOCKQUERY
DESCRIPTOR.message_types_by_name['CybosDayData'] = _CYBOSDAYDATA
DESCRIPTOR.message_types_by_name['CybosDayDatas'] = _CYBOSDAYDATAS
DESCRIPTOR.message_types_by_name['CybosTickData'] = _CYBOSTICKDATA
DESCRIPTOR.message_types_by_name['CybosBidAskTickData'] = _CYBOSBIDASKTICKDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

StockCodeQuery = _reflection.GeneratedProtocolMessageType('StockCodeQuery', (_message.Message,), {
  'DESCRIPTOR' : _STOCKCODEQUERY,
  '__module__' : 'stock_provider_pb2'
  # @@protoc_insertion_point(class_scope:stock_api.StockCodeQuery)
  })
_sym_db.RegisterMessage(StockCodeQuery)

StockQuery = _reflection.GeneratedProtocolMessageType('StockQuery', (_message.Message,), {
  'DESCRIPTOR' : _STOCKQUERY,
  '__module__' : 'stock_provider_pb2'
  # @@protoc_insertion_point(class_scope:stock_api.StockQuery)
  })
_sym_db.RegisterMessage(StockQuery)

CybosDayData = _reflection.GeneratedProtocolMessageType('CybosDayData', (_message.Message,), {
  'DESCRIPTOR' : _CYBOSDAYDATA,
  '__module__' : 'stock_provider_pb2'
  # @@protoc_insertion_point(class_scope:stock_api.CybosDayData)
  })
_sym_db.RegisterMessage(CybosDayData)

CybosDayDatas = _reflection.GeneratedProtocolMessageType('CybosDayDatas', (_message.Message,), {
  'DESCRIPTOR' : _CYBOSDAYDATAS,
  '__module__' : 'stock_provider_pb2'
  # @@protoc_insertion_point(class_scope:stock_api.CybosDayDatas)
  })
_sym_db.RegisterMessage(CybosDayDatas)

CybosTickData = _reflection.GeneratedProtocolMessageType('CybosTickData', (_message.Message,), {
  'DESCRIPTOR' : _CYBOSTICKDATA,
  '__module__' : 'stock_provider_pb2'
  # @@protoc_insertion_point(class_scope:stock_api.CybosTickData)
  })
_sym_db.RegisterMessage(CybosTickData)

CybosBidAskTickData = _reflection.GeneratedProtocolMessageType('CybosBidAskTickData', (_message.Message,), {
  'DESCRIPTOR' : _CYBOSBIDASKTICKDATA,
  '__module__' : 'stock_provider_pb2'
  # @@protoc_insertion_point(class_scope:stock_api.CybosBidAskTickData)
  })
_sym_db.RegisterMessage(CybosBidAskTickData)



_STOCK = _descriptor.ServiceDescriptor(
  name='Stock',
  full_name='stock_api.Stock',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=1928,
  serialized_end=2157,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetDayData',
    full_name='stock_api.Stock.GetDayData',
    index=0,
    containing_service=None,
    input_type=_STOCKQUERY,
    output_type=_CYBOSDAYDATAS,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeStock',
    full_name='stock_api.Stock.SubscribeStock',
    index=1,
    containing_service=None,
    input_type=_STOCKCODEQUERY,
    output_type=_CYBOSTICKDATA,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='SubscribeBidAsk',
    full_name='stock_api.Stock.SubscribeBidAsk',
    index=2,
    containing_service=None,
    input_type=_STOCKCODEQUERY,
    output_type=_CYBOSBIDASKTICKDATA,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_STOCK)

DESCRIPTOR.services_by_name['Stock'] = _STOCK

# @@protoc_insertion_point(module_scope)
