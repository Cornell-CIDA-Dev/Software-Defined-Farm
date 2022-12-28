# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: storage.proto

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
  name='storage.proto',
  package='sdf',
  syntax='proto3',
  serialized_pb=_b('\n\rstorage.proto\x12\x03sdf\x1a\x0cshared.proto\"\x1a\n\nFileSystem\x12\x0c\n\x04path\x18\x01 \x01(\t\"\x1e\n\nChangeFeed\x12\x10\n\x08iterator\x18\x01 \x01(\t\";\n\x06PubSub\x12!\n\nsubscriber\x18\x01 \x01(\x0b\x32\r.sdf.Observer\x12\x0e\n\x06topics\x18\x02 \x03(\t\"\x88\x01\n\nMediumType\x12!\n\x06sdf_fs\x18\x01 \x01(\x0b\x32\x0f.sdf.FileSystemH\x00\x12#\n\x08sdf_feed\x18\x02 \x01(\x0b\x32\x0f.sdf.ChangeFeedH\x00\x12\"\n\x0bsdf_pub_sub\x18\x03 \x01(\x0b\x32\x0b.sdf.PubSubH\x00\x42\x0e\n\x0cmedium_types\"G\n\nStorageRPC\x12%\n\tprocedure\x18\x01 \x01(\x0b\x32\x12.sdf.ProcedureType\x12\x12\n\nstore_args\x18\x02 \x01(\x0c\x62\x06proto3')
  ,
  dependencies=[shared__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_FILESYSTEM = _descriptor.Descriptor(
  name='FileSystem',
  full_name='sdf.FileSystem',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='sdf.FileSystem.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=36,
  serialized_end=62,
)


_CHANGEFEED = _descriptor.Descriptor(
  name='ChangeFeed',
  full_name='sdf.ChangeFeed',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='iterator', full_name='sdf.ChangeFeed.iterator', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=64,
  serialized_end=94,
)


_PUBSUB = _descriptor.Descriptor(
  name='PubSub',
  full_name='sdf.PubSub',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='subscriber', full_name='sdf.PubSub.subscriber', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='topics', full_name='sdf.PubSub.topics', index=1,
      number=2, type=9, cpp_type=9, label=3,
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
  serialized_start=96,
  serialized_end=155,
)


_MEDIUMTYPE = _descriptor.Descriptor(
  name='MediumType',
  full_name='sdf.MediumType',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sdf_fs', full_name='sdf.MediumType.sdf_fs', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sdf_feed', full_name='sdf.MediumType.sdf_feed', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sdf_pub_sub', full_name='sdf.MediumType.sdf_pub_sub', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
      name='medium_types', full_name='sdf.MediumType.medium_types',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=158,
  serialized_end=294,
)


_STORAGERPC = _descriptor.Descriptor(
  name='StorageRPC',
  full_name='sdf.StorageRPC',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='procedure', full_name='sdf.StorageRPC.procedure', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='store_args', full_name='sdf.StorageRPC.store_args', index=1,
      number=2, type=12, cpp_type=9, label=1,
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
  serialized_start=296,
  serialized_end=367,
)

_PUBSUB.fields_by_name['subscriber'].message_type = shared__pb2._OBSERVER
_MEDIUMTYPE.fields_by_name['sdf_fs'].message_type = _FILESYSTEM
_MEDIUMTYPE.fields_by_name['sdf_feed'].message_type = _CHANGEFEED
_MEDIUMTYPE.fields_by_name['sdf_pub_sub'].message_type = _PUBSUB
_MEDIUMTYPE.oneofs_by_name['medium_types'].fields.append(
  _MEDIUMTYPE.fields_by_name['sdf_fs'])
_MEDIUMTYPE.fields_by_name['sdf_fs'].containing_oneof = _MEDIUMTYPE.oneofs_by_name['medium_types']
_MEDIUMTYPE.oneofs_by_name['medium_types'].fields.append(
  _MEDIUMTYPE.fields_by_name['sdf_feed'])
_MEDIUMTYPE.fields_by_name['sdf_feed'].containing_oneof = _MEDIUMTYPE.oneofs_by_name['medium_types']
_MEDIUMTYPE.oneofs_by_name['medium_types'].fields.append(
  _MEDIUMTYPE.fields_by_name['sdf_pub_sub'])
_MEDIUMTYPE.fields_by_name['sdf_pub_sub'].containing_oneof = _MEDIUMTYPE.oneofs_by_name['medium_types']
_STORAGERPC.fields_by_name['procedure'].message_type = shared__pb2._PROCEDURETYPE
DESCRIPTOR.message_types_by_name['FileSystem'] = _FILESYSTEM
DESCRIPTOR.message_types_by_name['ChangeFeed'] = _CHANGEFEED
DESCRIPTOR.message_types_by_name['PubSub'] = _PUBSUB
DESCRIPTOR.message_types_by_name['MediumType'] = _MEDIUMTYPE
DESCRIPTOR.message_types_by_name['StorageRPC'] = _STORAGERPC

FileSystem = _reflection.GeneratedProtocolMessageType('FileSystem', (_message.Message,), dict(
  DESCRIPTOR = _FILESYSTEM,
  __module__ = 'storage_pb2'
  # @@protoc_insertion_point(class_scope:sdf.FileSystem)
  ))
_sym_db.RegisterMessage(FileSystem)

ChangeFeed = _reflection.GeneratedProtocolMessageType('ChangeFeed', (_message.Message,), dict(
  DESCRIPTOR = _CHANGEFEED,
  __module__ = 'storage_pb2'
  # @@protoc_insertion_point(class_scope:sdf.ChangeFeed)
  ))
_sym_db.RegisterMessage(ChangeFeed)

PubSub = _reflection.GeneratedProtocolMessageType('PubSub', (_message.Message,), dict(
  DESCRIPTOR = _PUBSUB,
  __module__ = 'storage_pb2'
  # @@protoc_insertion_point(class_scope:sdf.PubSub)
  ))
_sym_db.RegisterMessage(PubSub)

MediumType = _reflection.GeneratedProtocolMessageType('MediumType', (_message.Message,), dict(
  DESCRIPTOR = _MEDIUMTYPE,
  __module__ = 'storage_pb2'
  # @@protoc_insertion_point(class_scope:sdf.MediumType)
  ))
_sym_db.RegisterMessage(MediumType)

StorageRPC = _reflection.GeneratedProtocolMessageType('StorageRPC', (_message.Message,), dict(
  DESCRIPTOR = _STORAGERPC,
  __module__ = 'storage_pb2'
  # @@protoc_insertion_point(class_scope:sdf.StorageRPC)
  ))
_sym_db.RegisterMessage(StorageRPC)


# @@protoc_insertion_point(module_scope)