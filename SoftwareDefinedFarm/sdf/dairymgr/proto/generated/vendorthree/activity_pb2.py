# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: activity.proto

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
  name='activity.proto',
  package='dairymgr',
  syntax='proto3',
  serialized_pb=_b('\n\x0e\x61\x63tivity.proto\x12\x08\x64\x61irymgr\"\x98\x01\n\x10\x44\x61ilyCowActivity\x12<\n\x0f\x61\x63tivityEntries\x18\x01 \x03(\x0b\x32#.dairymgr.DailyCowActivity.Activity\x1a\x46\n\x08\x41\x63tivity\x12\x0f\n\x07localId\x18\x01 \x01(\x05\x12\x17\n\x0fobservationTime\x18\x02 \x01(\t\x12\x10\n\x08\x61\x63tivity\x18\x03 \x01(\x05\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_DAILYCOWACTIVITY_ACTIVITY = _descriptor.Descriptor(
  name='Activity',
  full_name='dairymgr.DailyCowActivity.Activity',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='localId', full_name='dairymgr.DailyCowActivity.Activity.localId', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='observationTime', full_name='dairymgr.DailyCowActivity.Activity.observationTime', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='activity', full_name='dairymgr.DailyCowActivity.Activity.activity', index=2,
      number=3, type=5, cpp_type=1, label=1,
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
  serialized_start=111,
  serialized_end=181,
)

_DAILYCOWACTIVITY = _descriptor.Descriptor(
  name='DailyCowActivity',
  full_name='dairymgr.DailyCowActivity',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='activityEntries', full_name='dairymgr.DailyCowActivity.activityEntries', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_DAILYCOWACTIVITY_ACTIVITY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=29,
  serialized_end=181,
)

_DAILYCOWACTIVITY_ACTIVITY.containing_type = _DAILYCOWACTIVITY
_DAILYCOWACTIVITY.fields_by_name['activityEntries'].message_type = _DAILYCOWACTIVITY_ACTIVITY
DESCRIPTOR.message_types_by_name['DailyCowActivity'] = _DAILYCOWACTIVITY

DailyCowActivity = _reflection.GeneratedProtocolMessageType('DailyCowActivity', (_message.Message,), dict(

  Activity = _reflection.GeneratedProtocolMessageType('Activity', (_message.Message,), dict(
    DESCRIPTOR = _DAILYCOWACTIVITY_ACTIVITY,
    __module__ = 'activity_pb2'
    # @@protoc_insertion_point(class_scope:dairymgr.DailyCowActivity.Activity)
    ))
  ,
  DESCRIPTOR = _DAILYCOWACTIVITY,
  __module__ = 'activity_pb2'
  # @@protoc_insertion_point(class_scope:dairymgr.DailyCowActivity)
  ))
_sym_db.RegisterMessage(DailyCowActivity)
_sym_db.RegisterMessage(DailyCowActivity.Activity)


# @@protoc_insertion_point(module_scope)
