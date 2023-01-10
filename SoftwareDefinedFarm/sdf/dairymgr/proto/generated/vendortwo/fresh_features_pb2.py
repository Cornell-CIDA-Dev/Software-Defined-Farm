# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fresh_features.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import shared_messages_pb2 as shared__messages__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='fresh_features.proto',
  package='dairymgr',
  syntax='proto3',
  serialized_pb=_b('\n\x14\x66resh_features.proto\x12\x08\x64\x61irymgr\x1a\x15shared_messages.proto\"\x84\x03\n\x16PerCowFreshFeatureData\x12\'\n\x03key\x18\x01 \x01(\x0b\x32\x1a.dairymgr.RecordIdentifier\x12\x0c\n\x04shon\x18\x02 \x01(\t\x12\r\n\x05shoff\x18\x03 \x01(\t\x12\r\n\x05\x62olus\x18\x04 \x01(\t\x12\x0b\n\x03\x64im\x18\x05 \x01(\x05\x12\x0c\n\x04\x66\x64\x61t\x18\x06 \x01(\t\x12\x0c\n\x04\x62\x64\x61t\x18\x07 \x01(\t\x12\r\n\x05\x61geda\x18\x08 \x01(\x05\x12\r\n\x05\x61\x66\x63\x64\x61\x18\t \x01(\x05\x12\r\n\x05mosfh\x18\n \x01(\t\x12&\n\x07\x63\x61lving\x18\x0b \x01(\x0b\x32\x15.dairymgr.CalvingData\x12@\n\x08lactData\x18\x0c \x01(\x0b\x32..dairymgr.PerCowFreshFeatureData.LactationData\x12*\n\tgestation\x18\r \x01(\x0b\x32\x17.dairymgr.GestationData\x1a)\n\rLactationData\x12\n\n\x02pl\x18\x01 \x01(\x05\x12\x0c\n\x04pdmi\x18\x02 \x01(\x05\"T\n\x17PerFileFreshFeatureData\x12\x39\n\x0f\x61llFreshEntries\x18\x01 \x03(\x0b\x32 .dairymgr.PerCowFreshFeatureDatab\x06proto3')
  ,
  dependencies=[shared__messages__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_PERCOWFRESHFEATUREDATA_LACTATIONDATA = _descriptor.Descriptor(
  name='LactationData',
  full_name='dairymgr.PerCowFreshFeatureData.LactationData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pl', full_name='dairymgr.PerCowFreshFeatureData.LactationData.pl', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pdmi', full_name='dairymgr.PerCowFreshFeatureData.LactationData.pdmi', index=1,
      number=2, type=5, cpp_type=1, label=1,
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
  serialized_start=405,
  serialized_end=446,
)

_PERCOWFRESHFEATUREDATA = _descriptor.Descriptor(
  name='PerCowFreshFeatureData',
  full_name='dairymgr.PerCowFreshFeatureData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='dairymgr.PerCowFreshFeatureData.key', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shon', full_name='dairymgr.PerCowFreshFeatureData.shon', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shoff', full_name='dairymgr.PerCowFreshFeatureData.shoff', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bolus', full_name='dairymgr.PerCowFreshFeatureData.bolus', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dim', full_name='dairymgr.PerCowFreshFeatureData.dim', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='fdat', full_name='dairymgr.PerCowFreshFeatureData.fdat', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bdat', full_name='dairymgr.PerCowFreshFeatureData.bdat', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ageda', full_name='dairymgr.PerCowFreshFeatureData.ageda', index=7,
      number=8, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='afcda', full_name='dairymgr.PerCowFreshFeatureData.afcda', index=8,
      number=9, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mosfh', full_name='dairymgr.PerCowFreshFeatureData.mosfh', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='calving', full_name='dairymgr.PerCowFreshFeatureData.calving', index=10,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lactData', full_name='dairymgr.PerCowFreshFeatureData.lactData', index=11,
      number=12, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gestation', full_name='dairymgr.PerCowFreshFeatureData.gestation', index=12,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_PERCOWFRESHFEATUREDATA_LACTATIONDATA, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=58,
  serialized_end=446,
)


_PERFILEFRESHFEATUREDATA = _descriptor.Descriptor(
  name='PerFileFreshFeatureData',
  full_name='dairymgr.PerFileFreshFeatureData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='allFreshEntries', full_name='dairymgr.PerFileFreshFeatureData.allFreshEntries', index=0,
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
  serialized_start=448,
  serialized_end=532,
)

_PERCOWFRESHFEATUREDATA_LACTATIONDATA.containing_type = _PERCOWFRESHFEATUREDATA
_PERCOWFRESHFEATUREDATA.fields_by_name['key'].message_type = shared__messages__pb2._RECORDIDENTIFIER
_PERCOWFRESHFEATUREDATA.fields_by_name['calving'].message_type = shared__messages__pb2._CALVINGDATA
_PERCOWFRESHFEATUREDATA.fields_by_name['lactData'].message_type = _PERCOWFRESHFEATUREDATA_LACTATIONDATA
_PERCOWFRESHFEATUREDATA.fields_by_name['gestation'].message_type = shared__messages__pb2._GESTATIONDATA
_PERFILEFRESHFEATUREDATA.fields_by_name['allFreshEntries'].message_type = _PERCOWFRESHFEATUREDATA
DESCRIPTOR.message_types_by_name['PerCowFreshFeatureData'] = _PERCOWFRESHFEATUREDATA
DESCRIPTOR.message_types_by_name['PerFileFreshFeatureData'] = _PERFILEFRESHFEATUREDATA

PerCowFreshFeatureData = _reflection.GeneratedProtocolMessageType('PerCowFreshFeatureData', (_message.Message,), dict(

  LactationData = _reflection.GeneratedProtocolMessageType('LactationData', (_message.Message,), dict(
    DESCRIPTOR = _PERCOWFRESHFEATUREDATA_LACTATIONDATA,
    __module__ = 'fresh_features_pb2'
    # @@protoc_insertion_point(class_scope:dairymgr.PerCowFreshFeatureData.LactationData)
    ))
  ,
  DESCRIPTOR = _PERCOWFRESHFEATUREDATA,
  __module__ = 'fresh_features_pb2'
  # @@protoc_insertion_point(class_scope:dairymgr.PerCowFreshFeatureData)
  ))
_sym_db.RegisterMessage(PerCowFreshFeatureData)
_sym_db.RegisterMessage(PerCowFreshFeatureData.LactationData)

PerFileFreshFeatureData = _reflection.GeneratedProtocolMessageType('PerFileFreshFeatureData', (_message.Message,), dict(
  DESCRIPTOR = _PERFILEFRESHFEATUREDATA,
  __module__ = 'fresh_features_pb2'
  # @@protoc_insertion_point(class_scope:dairymgr.PerFileFreshFeatureData)
  ))
_sym_db.RegisterMessage(PerFileFreshFeatureData)


# @@protoc_insertion_point(module_scope)