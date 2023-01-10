# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pencap.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pencap.proto',
  package='dairymgr',
  syntax='proto3',
  serialized_pb=_b('\n\x0cpencap.proto\x12\x08\x64\x61irymgr\"Z\n\nPerPenData\x12\r\n\x05\x62yPen\x18\x01 \x01(\x05\x12\x0b\n\x03pct\x18\x02 \x01(\x05\x12\r\n\x05\x63ount\x18\x03 \x01(\x05\x12\x10\n\x08\x61vgstlct\x18\x04 \x01(\x05\x12\x0f\n\x07\x61vPencp\x18\x05 \x01(\x05\"@\n\x16PerFilePenCapacityData\x12&\n\x08\x61ll_pens\x18\x01 \x03(\x0b\x32\x14.dairymgr.PerPenDatab\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PERPENDATA = _descriptor.Descriptor(
  name='PerPenData',
  full_name='dairymgr.PerPenData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='byPen', full_name='dairymgr.PerPenData.byPen', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pct', full_name='dairymgr.PerPenData.pct', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='count', full_name='dairymgr.PerPenData.count', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avgstlct', full_name='dairymgr.PerPenData.avgstlct', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='avPencp', full_name='dairymgr.PerPenData.avPencp', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=26,
  serialized_end=116,
)


_PERFILEPENCAPACITYDATA = _descriptor.Descriptor(
  name='PerFilePenCapacityData',
  full_name='dairymgr.PerFilePenCapacityData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='all_pens', full_name='dairymgr.PerFilePenCapacityData.all_pens', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=118,
  serialized_end=182,
)

_PERFILEPENCAPACITYDATA.fields_by_name['all_pens'].message_type = _PERPENDATA
DESCRIPTOR.message_types_by_name['PerPenData'] = _PERPENDATA
DESCRIPTOR.message_types_by_name['PerFilePenCapacityData'] = _PERFILEPENCAPACITYDATA

PerPenData = _reflection.GeneratedProtocolMessageType('PerPenData', (_message.Message,), dict(
  DESCRIPTOR = _PERPENDATA,
  __module__ = 'pencap_pb2'
  # @@protoc_insertion_point(class_scope:dairymgr.PerPenData)
  ))
_sym_db.RegisterMessage(PerPenData)

PerFilePenCapacityData = _reflection.GeneratedProtocolMessageType('PerFilePenCapacityData', (_message.Message,), dict(
  DESCRIPTOR = _PERFILEPENCAPACITYDATA,
  __module__ = 'pencap_pb2'
  # @@protoc_insertion_point(class_scope:dairymgr.PerFilePenCapacityData)
  ))
_sym_db.RegisterMessage(PerFilePenCapacityData)


# @@protoc_insertion_point(module_scope)