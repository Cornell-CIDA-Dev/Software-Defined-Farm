# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sensor.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import shared_pb2 as shared__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='sensor.proto',
  package='sdf',
  syntax='proto3',
  serialized_pb=_b('\n\x0csensor.proto\x12\x03sdf\x1a\x0cshared.proto\"c\n\tSensorRPC\x12%\n\tprocedure\x18\x01 \x01(\x0b\x32\x12.sdf.ProcedureType\x12\x1f\n\x08observer\x18\x02 \x01(\x0b\x32\r.sdf.Observer\x12\x0e\n\x06update\x18\x03 \x01(\x0c\x62\x06proto3')
  ,
  dependencies=[shared__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_SENSORRPC = _descriptor.Descriptor(
  name='SensorRPC',
  full_name='sdf.SensorRPC',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='procedure', full_name='sdf.SensorRPC.procedure', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='observer', full_name='sdf.SensorRPC.observer', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='update', full_name='sdf.SensorRPC.update', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=134,
)

_SENSORRPC.fields_by_name['procedure'].message_type = shared__pb2._PROCEDURETYPE
_SENSORRPC.fields_by_name['observer'].message_type = shared__pb2._OBSERVER
DESCRIPTOR.message_types_by_name['SensorRPC'] = _SENSORRPC

SensorRPC = _reflection.GeneratedProtocolMessageType('SensorRPC', (_message.Message,), dict(
  DESCRIPTOR = _SENSORRPC,
  __module__ = 'sensor_pb2'
  # @@protoc_insertion_point(class_scope:sdf.SensorRPC)
  ))
_sym_db.RegisterMessage(SensorRPC)


# @@protoc_insertion_point(module_scope)
