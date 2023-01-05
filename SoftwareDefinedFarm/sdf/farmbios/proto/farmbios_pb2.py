# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: farmbios.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import sensor_pb2 as sensor__pb2
from . import storage_pb2 as storage__pb2
from . import compute_pb2 as compute__pb2
from . import actuation_pb2 as actuation__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='farmbios.proto',
  package='sdf',
  syntax='proto3',
  serialized_pb=_b('\n\x0e\x66\x61rmbios.proto\x12\x03sdf\x1a\x0csensor.proto\x1a\rstorage.proto\x1a\rcompute.proto\x1a\x0f\x61\x63tuation.proto\"7\n\x08\x43\x61llback\x12\x12\n\nidentifier\x18\x01 \x01(\t\x12\x17\n\x0fisFinalResponse\x18\x02 \x01(\x08\"\xe8\x01\n\x0f\x46\x61rmBIOSMessage\x12 \n\x06sensor\x18\x01 \x01(\x0b\x32\x0e.sdf.SensorRPCH\x00\x12\"\n\x07storage\x18\x02 \x01(\x0b\x32\x0f.sdf.StorageRPCH\x00\x12\"\n\x07\x63ompute\x18\x03 \x01(\x0b\x32\x0f.sdf.ComputeRPCH\x00\x12&\n\tactuation\x18\x04 \x01(\x0b\x32\x11.sdf.ActuationRPCH\x00\x12\x0c\n\x04\x64\x61ta\x18\x05 \x01(\x0c\x12\x1f\n\x08\x63\x61llback\x18\x06 \x01(\x0b\x32\r.sdf.CallbackB\x14\n\x12\x66\x61rmbios_msg_typesb\x06proto3')
  ,
  dependencies=[sensor__pb2.DESCRIPTOR,storage__pb2.DESCRIPTOR,compute__pb2.DESCRIPTOR,actuation__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_CALLBACK = _descriptor.Descriptor(
  name='Callback',
  full_name='sdf.Callback',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='identifier', full_name='sdf.Callback.identifier', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isFinalResponse', full_name='sdf.Callback.isFinalResponse', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  serialized_start=84,
  serialized_end=139,
)


_FARMBIOSMESSAGE = _descriptor.Descriptor(
  name='FarmBIOSMessage',
  full_name='sdf.FarmBIOSMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sensor', full_name='sdf.FarmBIOSMessage.sensor', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='storage', full_name='sdf.FarmBIOSMessage.storage', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='compute', full_name='sdf.FarmBIOSMessage.compute', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='actuation', full_name='sdf.FarmBIOSMessage.actuation', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='sdf.FarmBIOSMessage.data', index=4,
      number=5, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='callback', full_name='sdf.FarmBIOSMessage.callback', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
    _descriptor.OneofDescriptor(
      name='farmbios_msg_types', full_name='sdf.FarmBIOSMessage.farmbios_msg_types',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=142,
  serialized_end=374,
)

_FARMBIOSMESSAGE.fields_by_name['sensor'].message_type = sensor__pb2._SENSORRPC
_FARMBIOSMESSAGE.fields_by_name['storage'].message_type = storage__pb2._STORAGERPC
_FARMBIOSMESSAGE.fields_by_name['compute'].message_type = compute__pb2._COMPUTERPC
_FARMBIOSMESSAGE.fields_by_name['actuation'].message_type = actuation__pb2._ACTUATIONRPC
_FARMBIOSMESSAGE.fields_by_name['callback'].message_type = _CALLBACK
_FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types'].fields.append(
  _FARMBIOSMESSAGE.fields_by_name['sensor'])
_FARMBIOSMESSAGE.fields_by_name['sensor'].containing_oneof = _FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types']
_FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types'].fields.append(
  _FARMBIOSMESSAGE.fields_by_name['storage'])
_FARMBIOSMESSAGE.fields_by_name['storage'].containing_oneof = _FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types']
_FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types'].fields.append(
  _FARMBIOSMESSAGE.fields_by_name['compute'])
_FARMBIOSMESSAGE.fields_by_name['compute'].containing_oneof = _FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types']
_FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types'].fields.append(
  _FARMBIOSMESSAGE.fields_by_name['actuation'])
_FARMBIOSMESSAGE.fields_by_name['actuation'].containing_oneof = _FARMBIOSMESSAGE.oneofs_by_name['farmbios_msg_types']
DESCRIPTOR.message_types_by_name['Callback'] = _CALLBACK
DESCRIPTOR.message_types_by_name['FarmBIOSMessage'] = _FARMBIOSMESSAGE

Callback = _reflection.GeneratedProtocolMessageType('Callback', (_message.Message,), dict(
  DESCRIPTOR = _CALLBACK,
  __module__ = 'farmbios_pb2'
  # @@protoc_insertion_point(class_scope:sdf.Callback)
  ))
_sym_db.RegisterMessage(Callback)

FarmBIOSMessage = _reflection.GeneratedProtocolMessageType('FarmBIOSMessage', (_message.Message,), dict(
  DESCRIPTOR = _FARMBIOSMESSAGE,
  __module__ = 'farmbios_pb2'
  # @@protoc_insertion_point(class_scope:sdf.FarmBIOSMessage)
  ))
_sym_db.RegisterMessage(FarmBIOSMessage)


# @@protoc_insertion_point(module_scope)
