// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'asset_management_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$AssetManagementEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementEvent()';
}


}

/// @nodoc
class $AssetManagementEventCopyWith<$Res>  {
$AssetManagementEventCopyWith(AssetManagementEvent _, $Res Function(AssetManagementEvent) __);
}


/// @nodoc


class AssetManagementLoadStarted implements AssetManagementEvent {
  const AssetManagementLoadStarted();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementLoadStarted);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementEvent.loadStarted()';
}


}




/// @nodoc


class AddDeviceStarted implements AssetManagementEvent {
  const AddDeviceStarted(this.device);
  

 final  ManagedDeviceOrm device;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddDeviceStartedCopyWith<AddDeviceStarted> get copyWith => _$AddDeviceStartedCopyWithImpl<AddDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddDeviceStarted&&(identical(other.device, device) || other.device == device));
}


@override
int get hashCode => Object.hash(runtimeType,device);

@override
String toString() {
  return 'AssetManagementEvent.addDeviceStarted(device: $device)';
}


}

/// @nodoc
abstract mixin class $AddDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddDeviceStartedCopyWith(AddDeviceStarted value, $Res Function(AddDeviceStarted) _then) = _$AddDeviceStartedCopyWithImpl;
@useResult
$Res call({
 ManagedDeviceOrm device
});




}
/// @nodoc
class _$AddDeviceStartedCopyWithImpl<$Res>
    implements $AddDeviceStartedCopyWith<$Res> {
  _$AddDeviceStartedCopyWithImpl(this._self, this._then);

  final AddDeviceStarted _self;
  final $Res Function(AddDeviceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? device = null,}) {
  return _then(AddDeviceStarted(
null == device ? _self.device : device // ignore: cast_nullable_to_non_nullable
as ManagedDeviceOrm,
  ));
}


}

/// @nodoc


class UpdateDeviceStarted implements AssetManagementEvent {
  const UpdateDeviceStarted(this.deviceId, this.device);
  

 final  String deviceId;
 final  ManagedDeviceOrm device;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateDeviceStartedCopyWith<UpdateDeviceStarted> get copyWith => _$UpdateDeviceStartedCopyWithImpl<UpdateDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateDeviceStarted&&(identical(other.deviceId, deviceId) || other.deviceId == deviceId)&&(identical(other.device, device) || other.device == device));
}


@override
int get hashCode => Object.hash(runtimeType,deviceId,device);

@override
String toString() {
  return 'AssetManagementEvent.updateDeviceStarted(deviceId: $deviceId, device: $device)';
}


}

/// @nodoc
abstract mixin class $UpdateDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateDeviceStartedCopyWith(UpdateDeviceStarted value, $Res Function(UpdateDeviceStarted) _then) = _$UpdateDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String deviceId, ManagedDeviceOrm device
});




}
/// @nodoc
class _$UpdateDeviceStartedCopyWithImpl<$Res>
    implements $UpdateDeviceStartedCopyWith<$Res> {
  _$UpdateDeviceStartedCopyWithImpl(this._self, this._then);

  final UpdateDeviceStarted _self;
  final $Res Function(UpdateDeviceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deviceId = null,Object? device = null,}) {
  return _then(UpdateDeviceStarted(
null == deviceId ? _self.deviceId : deviceId // ignore: cast_nullable_to_non_nullable
as String,null == device ? _self.device : device // ignore: cast_nullable_to_non_nullable
as ManagedDeviceOrm,
  ));
}


}

/// @nodoc


class DeleteDeviceStarted implements AssetManagementEvent {
  const DeleteDeviceStarted(this.deviceId);
  

 final  String deviceId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteDeviceStartedCopyWith<DeleteDeviceStarted> get copyWith => _$DeleteDeviceStartedCopyWithImpl<DeleteDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteDeviceStarted&&(identical(other.deviceId, deviceId) || other.deviceId == deviceId));
}


@override
int get hashCode => Object.hash(runtimeType,deviceId);

@override
String toString() {
  return 'AssetManagementEvent.deleteDeviceStarted(deviceId: $deviceId)';
}


}

/// @nodoc
abstract mixin class $DeleteDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteDeviceStartedCopyWith(DeleteDeviceStarted value, $Res Function(DeleteDeviceStarted) _then) = _$DeleteDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String deviceId
});




}
/// @nodoc
class _$DeleteDeviceStartedCopyWithImpl<$Res>
    implements $DeleteDeviceStartedCopyWith<$Res> {
  _$DeleteDeviceStartedCopyWithImpl(this._self, this._then);

  final DeleteDeviceStarted _self;
  final $Res Function(DeleteDeviceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deviceId = null,}) {
  return _then(DeleteDeviceStarted(
null == deviceId ? _self.deviceId : deviceId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class ConnectDeviceStarted implements AssetManagementEvent {
  const ConnectDeviceStarted(this.deviceId);
  

 final  String deviceId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ConnectDeviceStartedCopyWith<ConnectDeviceStarted> get copyWith => _$ConnectDeviceStartedCopyWithImpl<ConnectDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ConnectDeviceStarted&&(identical(other.deviceId, deviceId) || other.deviceId == deviceId));
}


@override
int get hashCode => Object.hash(runtimeType,deviceId);

@override
String toString() {
  return 'AssetManagementEvent.connectDeviceStarted(deviceId: $deviceId)';
}


}

/// @nodoc
abstract mixin class $ConnectDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $ConnectDeviceStartedCopyWith(ConnectDeviceStarted value, $Res Function(ConnectDeviceStarted) _then) = _$ConnectDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String deviceId
});




}
/// @nodoc
class _$ConnectDeviceStartedCopyWithImpl<$Res>
    implements $ConnectDeviceStartedCopyWith<$Res> {
  _$ConnectDeviceStartedCopyWithImpl(this._self, this._then);

  final ConnectDeviceStarted _self;
  final $Res Function(ConnectDeviceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deviceId = null,}) {
  return _then(ConnectDeviceStarted(
null == deviceId ? _self.deviceId : deviceId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class InitializeDeviceStarted implements AssetManagementEvent {
  const InitializeDeviceStarted(this.deviceId);
  

 final  String deviceId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InitializeDeviceStartedCopyWith<InitializeDeviceStarted> get copyWith => _$InitializeDeviceStartedCopyWithImpl<InitializeDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InitializeDeviceStarted&&(identical(other.deviceId, deviceId) || other.deviceId == deviceId));
}


@override
int get hashCode => Object.hash(runtimeType,deviceId);

@override
String toString() {
  return 'AssetManagementEvent.initializeDeviceStarted(deviceId: $deviceId)';
}


}

/// @nodoc
abstract mixin class $InitializeDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $InitializeDeviceStartedCopyWith(InitializeDeviceStarted value, $Res Function(InitializeDeviceStarted) _then) = _$InitializeDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String deviceId
});




}
/// @nodoc
class _$InitializeDeviceStartedCopyWithImpl<$Res>
    implements $InitializeDeviceStartedCopyWith<$Res> {
  _$InitializeDeviceStartedCopyWithImpl(this._self, this._then);

  final InitializeDeviceStarted _self;
  final $Res Function(InitializeDeviceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deviceId = null,}) {
  return _then(InitializeDeviceStarted(
null == deviceId ? _self.deviceId : deviceId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class DisconnectDeviceStarted implements AssetManagementEvent {
  const DisconnectDeviceStarted(this.deviceId);
  

 final  String deviceId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DisconnectDeviceStartedCopyWith<DisconnectDeviceStarted> get copyWith => _$DisconnectDeviceStartedCopyWithImpl<DisconnectDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DisconnectDeviceStarted&&(identical(other.deviceId, deviceId) || other.deviceId == deviceId));
}


@override
int get hashCode => Object.hash(runtimeType,deviceId);

@override
String toString() {
  return 'AssetManagementEvent.disconnectDeviceStarted(deviceId: $deviceId)';
}


}

/// @nodoc
abstract mixin class $DisconnectDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DisconnectDeviceStartedCopyWith(DisconnectDeviceStarted value, $Res Function(DisconnectDeviceStarted) _then) = _$DisconnectDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String deviceId
});




}
/// @nodoc
class _$DisconnectDeviceStartedCopyWithImpl<$Res>
    implements $DisconnectDeviceStartedCopyWith<$Res> {
  _$DisconnectDeviceStartedCopyWithImpl(this._self, this._then);

  final DisconnectDeviceStarted _self;
  final $Res Function(DisconnectDeviceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deviceId = null,}) {
  return _then(DisconnectDeviceStarted(
null == deviceId ? _self.deviceId : deviceId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddLabwareDefinitionStarted implements AssetManagementEvent {
  const AddLabwareDefinitionStarted(this.labwareDefinition);
  

 final  LabwareDefinitionCatalogOrm labwareDefinition;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddLabwareDefinitionStartedCopyWith<AddLabwareDefinitionStarted> get copyWith => _$AddLabwareDefinitionStartedCopyWithImpl<AddLabwareDefinitionStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddLabwareDefinitionStarted&&(identical(other.labwareDefinition, labwareDefinition) || other.labwareDefinition == labwareDefinition));
}


@override
int get hashCode => Object.hash(runtimeType,labwareDefinition);

@override
String toString() {
  return 'AssetManagementEvent.addLabwareDefinitionStarted(labwareDefinition: $labwareDefinition)';
}


}

/// @nodoc
abstract mixin class $AddLabwareDefinitionStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddLabwareDefinitionStartedCopyWith(AddLabwareDefinitionStarted value, $Res Function(AddLabwareDefinitionStarted) _then) = _$AddLabwareDefinitionStartedCopyWithImpl;
@useResult
$Res call({
 LabwareDefinitionCatalogOrm labwareDefinition
});




}
/// @nodoc
class _$AddLabwareDefinitionStartedCopyWithImpl<$Res>
    implements $AddLabwareDefinitionStartedCopyWith<$Res> {
  _$AddLabwareDefinitionStartedCopyWithImpl(this._self, this._then);

  final AddLabwareDefinitionStarted _self;
  final $Res Function(AddLabwareDefinitionStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? labwareDefinition = null,}) {
  return _then(AddLabwareDefinitionStarted(
null == labwareDefinition ? _self.labwareDefinition : labwareDefinition // ignore: cast_nullable_to_non_nullable
as LabwareDefinitionCatalogOrm,
  ));
}


}

/// @nodoc


class UpdateLabwareDefinitionStarted implements AssetManagementEvent {
  const UpdateLabwareDefinitionStarted(this.labwareDefinitionId, this.labwareDefinition);
  

 final  String labwareDefinitionId;
 final  LabwareDefinitionCatalogOrm labwareDefinition;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateLabwareDefinitionStartedCopyWith<UpdateLabwareDefinitionStarted> get copyWith => _$UpdateLabwareDefinitionStartedCopyWithImpl<UpdateLabwareDefinitionStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateLabwareDefinitionStarted&&(identical(other.labwareDefinitionId, labwareDefinitionId) || other.labwareDefinitionId == labwareDefinitionId)&&(identical(other.labwareDefinition, labwareDefinition) || other.labwareDefinition == labwareDefinition));
}


@override
int get hashCode => Object.hash(runtimeType,labwareDefinitionId,labwareDefinition);

@override
String toString() {
  return 'AssetManagementEvent.updateLabwareDefinitionStarted(labwareDefinitionId: $labwareDefinitionId, labwareDefinition: $labwareDefinition)';
}


}

/// @nodoc
abstract mixin class $UpdateLabwareDefinitionStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateLabwareDefinitionStartedCopyWith(UpdateLabwareDefinitionStarted value, $Res Function(UpdateLabwareDefinitionStarted) _then) = _$UpdateLabwareDefinitionStartedCopyWithImpl;
@useResult
$Res call({
 String labwareDefinitionId, LabwareDefinitionCatalogOrm labwareDefinition
});




}
/// @nodoc
class _$UpdateLabwareDefinitionStartedCopyWithImpl<$Res>
    implements $UpdateLabwareDefinitionStartedCopyWith<$Res> {
  _$UpdateLabwareDefinitionStartedCopyWithImpl(this._self, this._then);

  final UpdateLabwareDefinitionStarted _self;
  final $Res Function(UpdateLabwareDefinitionStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? labwareDefinitionId = null,Object? labwareDefinition = null,}) {
  return _then(UpdateLabwareDefinitionStarted(
null == labwareDefinitionId ? _self.labwareDefinitionId : labwareDefinitionId // ignore: cast_nullable_to_non_nullable
as String,null == labwareDefinition ? _self.labwareDefinition : labwareDefinition // ignore: cast_nullable_to_non_nullable
as LabwareDefinitionCatalogOrm,
  ));
}


}

/// @nodoc


class DeleteLabwareDefinitionStarted implements AssetManagementEvent {
  const DeleteLabwareDefinitionStarted(this.labwareDefinitionId);
  

 final  String labwareDefinitionId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteLabwareDefinitionStartedCopyWith<DeleteLabwareDefinitionStarted> get copyWith => _$DeleteLabwareDefinitionStartedCopyWithImpl<DeleteLabwareDefinitionStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteLabwareDefinitionStarted&&(identical(other.labwareDefinitionId, labwareDefinitionId) || other.labwareDefinitionId == labwareDefinitionId));
}


@override
int get hashCode => Object.hash(runtimeType,labwareDefinitionId);

@override
String toString() {
  return 'AssetManagementEvent.deleteLabwareDefinitionStarted(labwareDefinitionId: $labwareDefinitionId)';
}


}

/// @nodoc
abstract mixin class $DeleteLabwareDefinitionStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteLabwareDefinitionStartedCopyWith(DeleteLabwareDefinitionStarted value, $Res Function(DeleteLabwareDefinitionStarted) _then) = _$DeleteLabwareDefinitionStartedCopyWithImpl;
@useResult
$Res call({
 String labwareDefinitionId
});




}
/// @nodoc
class _$DeleteLabwareDefinitionStartedCopyWithImpl<$Res>
    implements $DeleteLabwareDefinitionStartedCopyWith<$Res> {
  _$DeleteLabwareDefinitionStartedCopyWithImpl(this._self, this._then);

  final DeleteLabwareDefinitionStarted _self;
  final $Res Function(DeleteLabwareDefinitionStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? labwareDefinitionId = null,}) {
  return _then(DeleteLabwareDefinitionStarted(
null == labwareDefinitionId ? _self.labwareDefinitionId : labwareDefinitionId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddLabwareInstanceStarted implements AssetManagementEvent {
  const AddLabwareInstanceStarted(this.labwareInstance);
  

 final  LabwareInstanceOrm labwareInstance;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddLabwareInstanceStartedCopyWith<AddLabwareInstanceStarted> get copyWith => _$AddLabwareInstanceStartedCopyWithImpl<AddLabwareInstanceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddLabwareInstanceStarted&&(identical(other.labwareInstance, labwareInstance) || other.labwareInstance == labwareInstance));
}


@override
int get hashCode => Object.hash(runtimeType,labwareInstance);

@override
String toString() {
  return 'AssetManagementEvent.addLabwareInstanceStarted(labwareInstance: $labwareInstance)';
}


}

/// @nodoc
abstract mixin class $AddLabwareInstanceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddLabwareInstanceStartedCopyWith(AddLabwareInstanceStarted value, $Res Function(AddLabwareInstanceStarted) _then) = _$AddLabwareInstanceStartedCopyWithImpl;
@useResult
$Res call({
 LabwareInstanceOrm labwareInstance
});




}
/// @nodoc
class _$AddLabwareInstanceStartedCopyWithImpl<$Res>
    implements $AddLabwareInstanceStartedCopyWith<$Res> {
  _$AddLabwareInstanceStartedCopyWithImpl(this._self, this._then);

  final AddLabwareInstanceStarted _self;
  final $Res Function(AddLabwareInstanceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? labwareInstance = null,}) {
  return _then(AddLabwareInstanceStarted(
null == labwareInstance ? _self.labwareInstance : labwareInstance // ignore: cast_nullable_to_non_nullable
as LabwareInstanceOrm,
  ));
}


}

/// @nodoc


class UpdateLabwareInstanceStarted implements AssetManagementEvent {
  const UpdateLabwareInstanceStarted(this.instanceId, this.labwareInstance);
  

 final  String instanceId;
 final  LabwareInstanceOrm labwareInstance;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateLabwareInstanceStartedCopyWith<UpdateLabwareInstanceStarted> get copyWith => _$UpdateLabwareInstanceStartedCopyWithImpl<UpdateLabwareInstanceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateLabwareInstanceStarted&&(identical(other.instanceId, instanceId) || other.instanceId == instanceId)&&(identical(other.labwareInstance, labwareInstance) || other.labwareInstance == labwareInstance));
}


@override
int get hashCode => Object.hash(runtimeType,instanceId,labwareInstance);

@override
String toString() {
  return 'AssetManagementEvent.updateLabwareInstanceStarted(instanceId: $instanceId, labwareInstance: $labwareInstance)';
}


}

/// @nodoc
abstract mixin class $UpdateLabwareInstanceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateLabwareInstanceStartedCopyWith(UpdateLabwareInstanceStarted value, $Res Function(UpdateLabwareInstanceStarted) _then) = _$UpdateLabwareInstanceStartedCopyWithImpl;
@useResult
$Res call({
 String instanceId, LabwareInstanceOrm labwareInstance
});




}
/// @nodoc
class _$UpdateLabwareInstanceStartedCopyWithImpl<$Res>
    implements $UpdateLabwareInstanceStartedCopyWith<$Res> {
  _$UpdateLabwareInstanceStartedCopyWithImpl(this._self, this._then);

  final UpdateLabwareInstanceStarted _self;
  final $Res Function(UpdateLabwareInstanceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? instanceId = null,Object? labwareInstance = null,}) {
  return _then(UpdateLabwareInstanceStarted(
null == instanceId ? _self.instanceId : instanceId // ignore: cast_nullable_to_non_nullable
as String,null == labwareInstance ? _self.labwareInstance : labwareInstance // ignore: cast_nullable_to_non_nullable
as LabwareInstanceOrm,
  ));
}


}

/// @nodoc


class DeleteLabwareInstanceStarted implements AssetManagementEvent {
  const DeleteLabwareInstanceStarted(this.instanceId);
  

 final  String instanceId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteLabwareInstanceStartedCopyWith<DeleteLabwareInstanceStarted> get copyWith => _$DeleteLabwareInstanceStartedCopyWithImpl<DeleteLabwareInstanceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteLabwareInstanceStarted&&(identical(other.instanceId, instanceId) || other.instanceId == instanceId));
}


@override
int get hashCode => Object.hash(runtimeType,instanceId);

@override
String toString() {
  return 'AssetManagementEvent.deleteLabwareInstanceStarted(instanceId: $instanceId)';
}


}

/// @nodoc
abstract mixin class $DeleteLabwareInstanceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteLabwareInstanceStartedCopyWith(DeleteLabwareInstanceStarted value, $Res Function(DeleteLabwareInstanceStarted) _then) = _$DeleteLabwareInstanceStartedCopyWithImpl;
@useResult
$Res call({
 String instanceId
});




}
/// @nodoc
class _$DeleteLabwareInstanceStartedCopyWithImpl<$Res>
    implements $DeleteLabwareInstanceStartedCopyWith<$Res> {
  _$DeleteLabwareInstanceStartedCopyWithImpl(this._self, this._then);

  final DeleteLabwareInstanceStarted _self;
  final $Res Function(DeleteLabwareInstanceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? instanceId = null,}) {
  return _then(DeleteLabwareInstanceStarted(
null == instanceId ? _self.instanceId : instanceId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddDeckLayoutStarted implements AssetManagementEvent {
  const AddDeckLayoutStarted(this.deckLayout);
  

 final  DeckLayoutOrm deckLayout;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddDeckLayoutStartedCopyWith<AddDeckLayoutStarted> get copyWith => _$AddDeckLayoutStartedCopyWithImpl<AddDeckLayoutStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddDeckLayoutStarted&&(identical(other.deckLayout, deckLayout) || other.deckLayout == deckLayout));
}


@override
int get hashCode => Object.hash(runtimeType,deckLayout);

@override
String toString() {
  return 'AssetManagementEvent.addDeckLayoutStarted(deckLayout: $deckLayout)';
}


}

/// @nodoc
abstract mixin class $AddDeckLayoutStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddDeckLayoutStartedCopyWith(AddDeckLayoutStarted value, $Res Function(AddDeckLayoutStarted) _then) = _$AddDeckLayoutStartedCopyWithImpl;
@useResult
$Res call({
 DeckLayoutOrm deckLayout
});




}
/// @nodoc
class _$AddDeckLayoutStartedCopyWithImpl<$Res>
    implements $AddDeckLayoutStartedCopyWith<$Res> {
  _$AddDeckLayoutStartedCopyWithImpl(this._self, this._then);

  final AddDeckLayoutStarted _self;
  final $Res Function(AddDeckLayoutStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deckLayout = null,}) {
  return _then(AddDeckLayoutStarted(
null == deckLayout ? _self.deckLayout : deckLayout // ignore: cast_nullable_to_non_nullable
as DeckLayoutOrm,
  ));
}


}

/// @nodoc


class UpdateDeckLayoutStarted implements AssetManagementEvent {
  const UpdateDeckLayoutStarted(this.deckLayoutId, this.deckLayout);
  

 final  String deckLayoutId;
 final  DeckLayoutOrm deckLayout;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateDeckLayoutStartedCopyWith<UpdateDeckLayoutStarted> get copyWith => _$UpdateDeckLayoutStartedCopyWithImpl<UpdateDeckLayoutStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateDeckLayoutStarted&&(identical(other.deckLayoutId, deckLayoutId) || other.deckLayoutId == deckLayoutId)&&(identical(other.deckLayout, deckLayout) || other.deckLayout == deckLayout));
}


@override
int get hashCode => Object.hash(runtimeType,deckLayoutId,deckLayout);

@override
String toString() {
  return 'AssetManagementEvent.updateDeckLayoutStarted(deckLayoutId: $deckLayoutId, deckLayout: $deckLayout)';
}


}

/// @nodoc
abstract mixin class $UpdateDeckLayoutStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateDeckLayoutStartedCopyWith(UpdateDeckLayoutStarted value, $Res Function(UpdateDeckLayoutStarted) _then) = _$UpdateDeckLayoutStartedCopyWithImpl;
@useResult
$Res call({
 String deckLayoutId, DeckLayoutOrm deckLayout
});




}
/// @nodoc
class _$UpdateDeckLayoutStartedCopyWithImpl<$Res>
    implements $UpdateDeckLayoutStartedCopyWith<$Res> {
  _$UpdateDeckLayoutStartedCopyWithImpl(this._self, this._then);

  final UpdateDeckLayoutStarted _self;
  final $Res Function(UpdateDeckLayoutStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deckLayoutId = null,Object? deckLayout = null,}) {
  return _then(UpdateDeckLayoutStarted(
null == deckLayoutId ? _self.deckLayoutId : deckLayoutId // ignore: cast_nullable_to_non_nullable
as String,null == deckLayout ? _self.deckLayout : deckLayout // ignore: cast_nullable_to_non_nullable
as DeckLayoutOrm,
  ));
}


}

/// @nodoc


class DeleteDeckLayoutStarted implements AssetManagementEvent {
  const DeleteDeckLayoutStarted(this.deckLayoutId);
  

 final  String deckLayoutId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteDeckLayoutStartedCopyWith<DeleteDeckLayoutStarted> get copyWith => _$DeleteDeckLayoutStartedCopyWithImpl<DeleteDeckLayoutStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteDeckLayoutStarted&&(identical(other.deckLayoutId, deckLayoutId) || other.deckLayoutId == deckLayoutId));
}


@override
int get hashCode => Object.hash(runtimeType,deckLayoutId);

@override
String toString() {
  return 'AssetManagementEvent.deleteDeckLayoutStarted(deckLayoutId: $deckLayoutId)';
}


}

/// @nodoc
abstract mixin class $DeleteDeckLayoutStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteDeckLayoutStartedCopyWith(DeleteDeckLayoutStarted value, $Res Function(DeleteDeckLayoutStarted) _then) = _$DeleteDeckLayoutStartedCopyWithImpl;
@useResult
$Res call({
 String deckLayoutId
});




}
/// @nodoc
class _$DeleteDeckLayoutStartedCopyWithImpl<$Res>
    implements $DeleteDeckLayoutStartedCopyWith<$Res> {
  _$DeleteDeckLayoutStartedCopyWithImpl(this._self, this._then);

  final DeleteDeckLayoutStarted _self;
  final $Res Function(DeleteDeckLayoutStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deckLayoutId = null,}) {
  return _then(DeleteDeckLayoutStarted(
null == deckLayoutId ? _self.deckLayoutId : deckLayoutId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc
mixin _$AssetManagementState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementState()';
}


}

/// @nodoc
class $AssetManagementStateCopyWith<$Res>  {
$AssetManagementStateCopyWith(AssetManagementState _, $Res Function(AssetManagementState) __);
}


/// @nodoc


class AssetManagementInitial implements AssetManagementState {
  const AssetManagementInitial();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementState.initial()';
}


}




/// @nodoc


class AssetManagementLoadInProgress implements AssetManagementState {
  const AssetManagementLoadInProgress();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementLoadInProgress);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementState.loadInProgress()';
}


}




/// @nodoc


class AssetManagementLoadSuccess implements AssetManagementState {
  const AssetManagementLoadSuccess({required final  List<ManagedDeviceOrm> devices, required final  List<LabwareDefinitionCatalogOrm> labwareDefinitions, required final  List<LabwareInstanceOrm> labwareInstances, required final  List<DeckLayoutOrm> deckLayouts}): _devices = devices,_labwareDefinitions = labwareDefinitions,_labwareInstances = labwareInstances,_deckLayouts = deckLayouts;
  

 final  List<ManagedDeviceOrm> _devices;
 List<ManagedDeviceOrm> get devices {
  if (_devices is EqualUnmodifiableListView) return _devices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_devices);
}

 final  List<LabwareDefinitionCatalogOrm> _labwareDefinitions;
 List<LabwareDefinitionCatalogOrm> get labwareDefinitions {
  if (_labwareDefinitions is EqualUnmodifiableListView) return _labwareDefinitions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_labwareDefinitions);
}

 final  List<LabwareInstanceOrm> _labwareInstances;
 List<LabwareInstanceOrm> get labwareInstances {
  if (_labwareInstances is EqualUnmodifiableListView) return _labwareInstances;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_labwareInstances);
}

 final  List<DeckLayoutOrm> _deckLayouts;
 List<DeckLayoutOrm> get deckLayouts {
  if (_deckLayouts is EqualUnmodifiableListView) return _deckLayouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_deckLayouts);
}


/// Create a copy of AssetManagementState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssetManagementLoadSuccessCopyWith<AssetManagementLoadSuccess> get copyWith => _$AssetManagementLoadSuccessCopyWithImpl<AssetManagementLoadSuccess>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementLoadSuccess&&const DeepCollectionEquality().equals(other._devices, _devices)&&const DeepCollectionEquality().equals(other._labwareDefinitions, _labwareDefinitions)&&const DeepCollectionEquality().equals(other._labwareInstances, _labwareInstances)&&const DeepCollectionEquality().equals(other._deckLayouts, _deckLayouts));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_devices),const DeepCollectionEquality().hash(_labwareDefinitions),const DeepCollectionEquality().hash(_labwareInstances),const DeepCollectionEquality().hash(_deckLayouts));

@override
String toString() {
  return 'AssetManagementState.loadSuccess(devices: $devices, labwareDefinitions: $labwareDefinitions, labwareInstances: $labwareInstances, deckLayouts: $deckLayouts)';
}


}

/// @nodoc
abstract mixin class $AssetManagementLoadSuccessCopyWith<$Res> implements $AssetManagementStateCopyWith<$Res> {
  factory $AssetManagementLoadSuccessCopyWith(AssetManagementLoadSuccess value, $Res Function(AssetManagementLoadSuccess) _then) = _$AssetManagementLoadSuccessCopyWithImpl;
@useResult
$Res call({
 List<ManagedDeviceOrm> devices, List<LabwareDefinitionCatalogOrm> labwareDefinitions, List<LabwareInstanceOrm> labwareInstances, List<DeckLayoutOrm> deckLayouts
});




}
/// @nodoc
class _$AssetManagementLoadSuccessCopyWithImpl<$Res>
    implements $AssetManagementLoadSuccessCopyWith<$Res> {
  _$AssetManagementLoadSuccessCopyWithImpl(this._self, this._then);

  final AssetManagementLoadSuccess _self;
  final $Res Function(AssetManagementLoadSuccess) _then;

/// Create a copy of AssetManagementState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? devices = null,Object? labwareDefinitions = null,Object? labwareInstances = null,Object? deckLayouts = null,}) {
  return _then(AssetManagementLoadSuccess(
devices: null == devices ? _self._devices : devices // ignore: cast_nullable_to_non_nullable
as List<ManagedDeviceOrm>,labwareDefinitions: null == labwareDefinitions ? _self._labwareDefinitions : labwareDefinitions // ignore: cast_nullable_to_non_nullable
as List<LabwareDefinitionCatalogOrm>,labwareInstances: null == labwareInstances ? _self._labwareInstances : labwareInstances // ignore: cast_nullable_to_non_nullable
as List<LabwareInstanceOrm>,deckLayouts: null == deckLayouts ? _self._deckLayouts : deckLayouts // ignore: cast_nullable_to_non_nullable
as List<DeckLayoutOrm>,
  ));
}


}

/// @nodoc


class AssetManagementLoadFailure implements AssetManagementState {
  const AssetManagementLoadFailure(this.error);
  

 final  String error;

/// Create a copy of AssetManagementState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssetManagementLoadFailureCopyWith<AssetManagementLoadFailure> get copyWith => _$AssetManagementLoadFailureCopyWithImpl<AssetManagementLoadFailure>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementLoadFailure&&(identical(other.error, error) || other.error == error));
}


@override
int get hashCode => Object.hash(runtimeType,error);

@override
String toString() {
  return 'AssetManagementState.loadFailure(error: $error)';
}


}

/// @nodoc
abstract mixin class $AssetManagementLoadFailureCopyWith<$Res> implements $AssetManagementStateCopyWith<$Res> {
  factory $AssetManagementLoadFailureCopyWith(AssetManagementLoadFailure value, $Res Function(AssetManagementLoadFailure) _then) = _$AssetManagementLoadFailureCopyWithImpl;
@useResult
$Res call({
 String error
});




}
/// @nodoc
class _$AssetManagementLoadFailureCopyWithImpl<$Res>
    implements $AssetManagementLoadFailureCopyWith<$Res> {
  _$AssetManagementLoadFailureCopyWithImpl(this._self, this._then);

  final AssetManagementLoadFailure _self;
  final $Res Function(AssetManagementLoadFailure) _then;

/// Create a copy of AssetManagementState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,}) {
  return _then(AssetManagementLoadFailure(
null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AssetManagementUpdateInProgress implements AssetManagementState {
  const AssetManagementUpdateInProgress();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementUpdateInProgress);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementState.updateInProgress()';
}


}




/// @nodoc


class AssetManagementUpdateSuccess implements AssetManagementState {
  const AssetManagementUpdateSuccess();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementUpdateSuccess);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'AssetManagementState.updateSuccess()';
}


}




/// @nodoc


class AssetManagementUpdateFailure implements AssetManagementState {
  const AssetManagementUpdateFailure(this.error);
  

 final  String error;

/// Create a copy of AssetManagementState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssetManagementUpdateFailureCopyWith<AssetManagementUpdateFailure> get copyWith => _$AssetManagementUpdateFailureCopyWithImpl<AssetManagementUpdateFailure>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementUpdateFailure&&(identical(other.error, error) || other.error == error));
}


@override
int get hashCode => Object.hash(runtimeType,error);

@override
String toString() {
  return 'AssetManagementState.updateFailure(error: $error)';
}


}

/// @nodoc
abstract mixin class $AssetManagementUpdateFailureCopyWith<$Res> implements $AssetManagementStateCopyWith<$Res> {
  factory $AssetManagementUpdateFailureCopyWith(AssetManagementUpdateFailure value, $Res Function(AssetManagementUpdateFailure) _then) = _$AssetManagementUpdateFailureCopyWithImpl;
@useResult
$Res call({
 String error
});




}
/// @nodoc
class _$AssetManagementUpdateFailureCopyWithImpl<$Res>
    implements $AssetManagementUpdateFailureCopyWith<$Res> {
  _$AssetManagementUpdateFailureCopyWithImpl(this._self, this._then);

  final AssetManagementUpdateFailure _self;
  final $Res Function(AssetManagementUpdateFailure) _then;

/// Create a copy of AssetManagementState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,}) {
  return _then(AssetManagementUpdateFailure(
null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
