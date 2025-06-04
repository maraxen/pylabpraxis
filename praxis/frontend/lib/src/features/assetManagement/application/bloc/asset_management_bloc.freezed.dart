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
  const AddDeviceStarted(this.machine);


 final  ManagedDeviceOrm machine;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddDeviceStartedCopyWith<AddDeviceStarted> get copyWith => _$AddDeviceStartedCopyWithImpl<AddDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddDeviceStarted&&(identical(other.machine, machine) || other.machine == machine));
}


@override
int get hashCode => Object.hash(runtimeType,machine);

@override
String toString() {
  return 'AssetManagementEvent.addDeviceStarted(machine: $machine)';
}


}

/// @nodoc
abstract mixin class $AddDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddDeviceStartedCopyWith(AddDeviceStarted value, $Res Function(AddDeviceStarted) _then) = _$AddDeviceStartedCopyWithImpl;
@useResult
$Res call({
 ManagedDeviceOrm machine
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
@pragma('vm:prefer-inline') $Res call({Object? machine = null,}) {
  return _then(AddDeviceStarted(
null == machine ? _self.machine : machine // ignore: cast_nullable_to_non_nullable
as ManagedDeviceOrm,
  ));
}


}

/// @nodoc


class UpdateDeviceStarted implements AssetManagementEvent {
  const UpdateDeviceStarted(this.machineId, this.machine);


 final  String machineId;
 final  ManagedDeviceOrm machine;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateDeviceStartedCopyWith<UpdateDeviceStarted> get copyWith => _$UpdateDeviceStartedCopyWithImpl<UpdateDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateDeviceStarted&&(identical(other.machineId, machineId) || other.machineId == machineId)&&(identical(other.machine, machine) || other.machine == machine));
}


@override
int get hashCode => Object.hash(runtimeType,machineId,machine);

@override
String toString() {
  return 'AssetManagementEvent.updateDeviceStarted(machineId: $machineId, machine: $machine)';
}


}

/// @nodoc
abstract mixin class $UpdateDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateDeviceStartedCopyWith(UpdateDeviceStarted value, $Res Function(UpdateDeviceStarted) _then) = _$UpdateDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String machineId, ManagedDeviceOrm machine
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
@pragma('vm:prefer-inline') $Res call({Object? machineId = null,Object? machine = null,}) {
  return _then(UpdateDeviceStarted(
null == machineId ? _self.machineId : machineId // ignore: cast_nullable_to_non_nullable
as String,null == machine ? _self.machine : machine // ignore: cast_nullable_to_non_nullable
as ManagedDeviceOrm,
  ));
}


}

/// @nodoc


class DeleteDeviceStarted implements AssetManagementEvent {
  const DeleteDeviceStarted(this.machineId);


 final  String machineId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteDeviceStartedCopyWith<DeleteDeviceStarted> get copyWith => _$DeleteDeviceStartedCopyWithImpl<DeleteDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteDeviceStarted&&(identical(other.machineId, machineId) || other.machineId == machineId));
}


@override
int get hashCode => Object.hash(runtimeType,machineId);

@override
String toString() {
  return 'AssetManagementEvent.deleteDeviceStarted(machineId: $machineId)';
}


}

/// @nodoc
abstract mixin class $DeleteDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteDeviceStartedCopyWith(DeleteDeviceStarted value, $Res Function(DeleteDeviceStarted) _then) = _$DeleteDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String machineId
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
@pragma('vm:prefer-inline') $Res call({Object? machineId = null,}) {
  return _then(DeleteDeviceStarted(
null == machineId ? _self.machineId : machineId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class ConnectDeviceStarted implements AssetManagementEvent {
  const ConnectDeviceStarted(this.machineId);


 final  String machineId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ConnectDeviceStartedCopyWith<ConnectDeviceStarted> get copyWith => _$ConnectDeviceStartedCopyWithImpl<ConnectDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ConnectDeviceStarted&&(identical(other.machineId, machineId) || other.machineId == machineId));
}


@override
int get hashCode => Object.hash(runtimeType,machineId);

@override
String toString() {
  return 'AssetManagementEvent.connectDeviceStarted(machineId: $machineId)';
}


}

/// @nodoc
abstract mixin class $ConnectDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $ConnectDeviceStartedCopyWith(ConnectDeviceStarted value, $Res Function(ConnectDeviceStarted) _then) = _$ConnectDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String machineId
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
@pragma('vm:prefer-inline') $Res call({Object? machineId = null,}) {
  return _then(ConnectDeviceStarted(
null == machineId ? _self.machineId : machineId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class InitializeDeviceStarted implements AssetManagementEvent {
  const InitializeDeviceStarted(this.machineId);


 final  String machineId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InitializeDeviceStartedCopyWith<InitializeDeviceStarted> get copyWith => _$InitializeDeviceStartedCopyWithImpl<InitializeDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InitializeDeviceStarted&&(identical(other.machineId, machineId) || other.machineId == machineId));
}


@override
int get hashCode => Object.hash(runtimeType,machineId);

@override
String toString() {
  return 'AssetManagementEvent.initializeDeviceStarted(machineId: $machineId)';
}


}

/// @nodoc
abstract mixin class $InitializeDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $InitializeDeviceStartedCopyWith(InitializeDeviceStarted value, $Res Function(InitializeDeviceStarted) _then) = _$InitializeDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String machineId
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
@pragma('vm:prefer-inline') $Res call({Object? machineId = null,}) {
  return _then(InitializeDeviceStarted(
null == machineId ? _self.machineId : machineId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class DisconnectDeviceStarted implements AssetManagementEvent {
  const DisconnectDeviceStarted(this.machineId);


 final  String machineId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DisconnectDeviceStartedCopyWith<DisconnectDeviceStarted> get copyWith => _$DisconnectDeviceStartedCopyWithImpl<DisconnectDeviceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DisconnectDeviceStarted&&(identical(other.machineId, machineId) || other.machineId == machineId));
}


@override
int get hashCode => Object.hash(runtimeType,machineId);

@override
String toString() {
  return 'AssetManagementEvent.disconnectDeviceStarted(machineId: $machineId)';
}


}

/// @nodoc
abstract mixin class $DisconnectDeviceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DisconnectDeviceStartedCopyWith(DisconnectDeviceStarted value, $Res Function(DisconnectDeviceStarted) _then) = _$DisconnectDeviceStartedCopyWithImpl;
@useResult
$Res call({
 String machineId
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
@pragma('vm:prefer-inline') $Res call({Object? machineId = null,}) {
  return _then(DisconnectDeviceStarted(
null == machineId ? _self.machineId : machineId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddResourceDefinitionStarted implements AssetManagementEvent {
  const AddResourceDefinitionStarted(this.resourceDefinition);


 final  ResourceDefinitionCatalogOrm resourceDefinition;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddResourceDefinitionStartedCopyWith<AddResourceDefinitionStarted> get copyWith => _$AddResourceDefinitionStartedCopyWithImpl<AddResourceDefinitionStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddResourceDefinitionStarted&&(identical(other.resourceDefinition, resourceDefinition) || other.resourceDefinition == resourceDefinition));
}


@override
int get hashCode => Object.hash(runtimeType,resourceDefinition);

@override
String toString() {
  return 'AssetManagementEvent.addResourceDefinitionStarted(resourceDefinition: $resourceDefinition)';
}


}

/// @nodoc
abstract mixin class $AddResourceDefinitionStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddResourceDefinitionStartedCopyWith(AddResourceDefinitionStarted value, $Res Function(AddResourceDefinitionStarted) _then) = _$AddResourceDefinitionStartedCopyWithImpl;
@useResult
$Res call({
 ResourceDefinitionCatalogOrm resourceDefinition
});




}
/// @nodoc
class _$AddResourceDefinitionStartedCopyWithImpl<$Res>
    implements $AddResourceDefinitionStartedCopyWith<$Res> {
  _$AddResourceDefinitionStartedCopyWithImpl(this._self, this._then);

  final AddResourceDefinitionStarted _self;
  final $Res Function(AddResourceDefinitionStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? resourceDefinition = null,}) {
  return _then(AddResourceDefinitionStarted(
null == resourceDefinition ? _self.resourceDefinition : resourceDefinition // ignore: cast_nullable_to_non_nullable
as ResourceDefinitionCatalogOrm,
  ));
}


}

/// @nodoc


class UpdateResourceDefinitionStarted implements AssetManagementEvent {
  const UpdateResourceDefinitionStarted(this.resourceDefinitionId, this.resourceDefinition);


 final  String resourceDefinitionId;
 final  ResourceDefinitionCatalogOrm resourceDefinition;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateResourceDefinitionStartedCopyWith<UpdateResourceDefinitionStarted> get copyWith => _$UpdateResourceDefinitionStartedCopyWithImpl<UpdateResourceDefinitionStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateResourceDefinitionStarted&&(identical(other.resourceDefinitionId, resourceDefinitionId) || other.resourceDefinitionId == resourceDefinitionId)&&(identical(other.resourceDefinition, resourceDefinition) || other.resourceDefinition == resourceDefinition));
}


@override
int get hashCode => Object.hash(runtimeType,resourceDefinitionId,resourceDefinition);

@override
String toString() {
  return 'AssetManagementEvent.updateResourceDefinitionStarted(resourceDefinitionId: $resourceDefinitionId, resourceDefinition: $resourceDefinition)';
}


}

/// @nodoc
abstract mixin class $UpdateResourceDefinitionStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateResourceDefinitionStartedCopyWith(UpdateResourceDefinitionStarted value, $Res Function(UpdateResourceDefinitionStarted) _then) = _$UpdateResourceDefinitionStartedCopyWithImpl;
@useResult
$Res call({
 String resourceDefinitionId, ResourceDefinitionCatalogOrm resourceDefinition
});




}
/// @nodoc
class _$UpdateResourceDefinitionStartedCopyWithImpl<$Res>
    implements $UpdateResourceDefinitionStartedCopyWith<$Res> {
  _$UpdateResourceDefinitionStartedCopyWithImpl(this._self, this._then);

  final UpdateResourceDefinitionStarted _self;
  final $Res Function(UpdateResourceDefinitionStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? resourceDefinitionId = null,Object? resourceDefinition = null,}) {
  return _then(UpdateResourceDefinitionStarted(
null == resourceDefinitionId ? _self.resourceDefinitionId : resourceDefinitionId // ignore: cast_nullable_to_non_nullable
as String,null == resourceDefinition ? _self.resourceDefinition : resourceDefinition // ignore: cast_nullable_to_non_nullable
as ResourceDefinitionCatalogOrm,
  ));
}


}

/// @nodoc


class DeleteResourceDefinitionStarted implements AssetManagementEvent {
  const DeleteResourceDefinitionStarted(this.resourceDefinitionId);


 final  String resourceDefinitionId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteResourceDefinitionStartedCopyWith<DeleteResourceDefinitionStarted> get copyWith => _$DeleteResourceDefinitionStartedCopyWithImpl<DeleteResourceDefinitionStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteResourceDefinitionStarted&&(identical(other.resourceDefinitionId, resourceDefinitionId) || other.resourceDefinitionId == resourceDefinitionId));
}


@override
int get hashCode => Object.hash(runtimeType,resourceDefinitionId);

@override
String toString() {
  return 'AssetManagementEvent.deleteResourceDefinitionStarted(resourceDefinitionId: $resourceDefinitionId)';
}


}

/// @nodoc
abstract mixin class $DeleteResourceDefinitionStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteResourceDefinitionStartedCopyWith(DeleteResourceDefinitionStarted value, $Res Function(DeleteResourceDefinitionStarted) _then) = _$DeleteResourceDefinitionStartedCopyWithImpl;
@useResult
$Res call({
 String resourceDefinitionId
});




}
/// @nodoc
class _$DeleteResourceDefinitionStartedCopyWithImpl<$Res>
    implements $DeleteResourceDefinitionStartedCopyWith<$Res> {
  _$DeleteResourceDefinitionStartedCopyWithImpl(this._self, this._then);

  final DeleteResourceDefinitionStarted _self;
  final $Res Function(DeleteResourceDefinitionStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? resourceDefinitionId = null,}) {
  return _then(DeleteResourceDefinitionStarted(
null == resourceDefinitionId ? _self.resourceDefinitionId : resourceDefinitionId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddResourceInstanceStarted implements AssetManagementEvent {
  const AddResourceInstanceStarted(this.resourceInstance);


 final  ResourceInstanceOrm resourceInstance;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddResourceInstanceStartedCopyWith<AddResourceInstanceStarted> get copyWith => _$AddResourceInstanceStartedCopyWithImpl<AddResourceInstanceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddResourceInstanceStarted&&(identical(other.resourceInstance, resourceInstance) || other.resourceInstance == resourceInstance));
}


@override
int get hashCode => Object.hash(runtimeType,resourceInstance);

@override
String toString() {
  return 'AssetManagementEvent.addResourceInstanceStarted(resourceInstance: $resourceInstance)';
}


}

/// @nodoc
abstract mixin class $AddResourceInstanceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $AddResourceInstanceStartedCopyWith(AddResourceInstanceStarted value, $Res Function(AddResourceInstanceStarted) _then) = _$AddResourceInstanceStartedCopyWithImpl;
@useResult
$Res call({
 ResourceInstanceOrm resourceInstance
});




}
/// @nodoc
class _$AddResourceInstanceStartedCopyWithImpl<$Res>
    implements $AddResourceInstanceStartedCopyWith<$Res> {
  _$AddResourceInstanceStartedCopyWithImpl(this._self, this._then);

  final AddResourceInstanceStarted _self;
  final $Res Function(AddResourceInstanceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? resourceInstance = null,}) {
  return _then(AddResourceInstanceStarted(
null == resourceInstance ? _self.resourceInstance : resourceInstance // ignore: cast_nullable_to_non_nullable
as ResourceInstanceOrm,
  ));
}


}

/// @nodoc


class UpdateResourceInstanceStarted implements AssetManagementEvent {
  const UpdateResourceInstanceStarted(this.instanceId, this.resourceInstance);


 final  String instanceId;
 final  ResourceInstanceOrm resourceInstance;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateResourceInstanceStartedCopyWith<UpdateResourceInstanceStarted> get copyWith => _$UpdateResourceInstanceStartedCopyWithImpl<UpdateResourceInstanceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateResourceInstanceStarted&&(identical(other.instanceId, instanceId) || other.instanceId == instanceId)&&(identical(other.resourceInstance, resourceInstance) || other.resourceInstance == resourceInstance));
}


@override
int get hashCode => Object.hash(runtimeType,instanceId,resourceInstance);

@override
String toString() {
  return 'AssetManagementEvent.updateResourceInstanceStarted(instanceId: $instanceId, resourceInstance: $resourceInstance)';
}


}

/// @nodoc
abstract mixin class $UpdateResourceInstanceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $UpdateResourceInstanceStartedCopyWith(UpdateResourceInstanceStarted value, $Res Function(UpdateResourceInstanceStarted) _then) = _$UpdateResourceInstanceStartedCopyWithImpl;
@useResult
$Res call({
 String instanceId, ResourceInstanceOrm resourceInstance
});




}
/// @nodoc
class _$UpdateResourceInstanceStartedCopyWithImpl<$Res>
    implements $UpdateResourceInstanceStartedCopyWith<$Res> {
  _$UpdateResourceInstanceStartedCopyWithImpl(this._self, this._then);

  final UpdateResourceInstanceStarted _self;
  final $Res Function(UpdateResourceInstanceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? instanceId = null,Object? resourceInstance = null,}) {
  return _then(UpdateResourceInstanceStarted(
null == instanceId ? _self.instanceId : instanceId // ignore: cast_nullable_to_non_nullable
as String,null == resourceInstance ? _self.resourceInstance : resourceInstance // ignore: cast_nullable_to_non_nullable
as ResourceInstanceOrm,
  ));
}


}

/// @nodoc


class DeleteResourceInstanceStarted implements AssetManagementEvent {
  const DeleteResourceInstanceStarted(this.instanceId);


 final  String instanceId;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeleteResourceInstanceStartedCopyWith<DeleteResourceInstanceStarted> get copyWith => _$DeleteResourceInstanceStartedCopyWithImpl<DeleteResourceInstanceStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeleteResourceInstanceStarted&&(identical(other.instanceId, instanceId) || other.instanceId == instanceId));
}


@override
int get hashCode => Object.hash(runtimeType,instanceId);

@override
String toString() {
  return 'AssetManagementEvent.deleteResourceInstanceStarted(instanceId: $instanceId)';
}


}

/// @nodoc
abstract mixin class $DeleteResourceInstanceStartedCopyWith<$Res> implements $AssetManagementEventCopyWith<$Res> {
  factory $DeleteResourceInstanceStartedCopyWith(DeleteResourceInstanceStarted value, $Res Function(DeleteResourceInstanceStarted) _then) = _$DeleteResourceInstanceStartedCopyWithImpl;
@useResult
$Res call({
 String instanceId
});




}
/// @nodoc
class _$DeleteResourceInstanceStartedCopyWithImpl<$Res>
    implements $DeleteResourceInstanceStartedCopyWith<$Res> {
  _$DeleteResourceInstanceStartedCopyWithImpl(this._self, this._then);

  final DeleteResourceInstanceStarted _self;
  final $Res Function(DeleteResourceInstanceStarted) _then;

/// Create a copy of AssetManagementEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? instanceId = null,}) {
  return _then(DeleteResourceInstanceStarted(
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
  const AssetManagementLoadSuccess({required final  List<ManagedDeviceOrm> machines, required final  List<ResourceDefinitionCatalogOrm> resourceDefinitions, required final  List<ResourceInstanceOrm> resourceInstances, required final  List<DeckLayoutOrm> deckLayouts}): _machines = machines,_resourceDefinitions = resourceDefinitions,_resourceInstances = resourceInstances,_deckLayouts = deckLayouts;


 final  List<ManagedDeviceOrm> _machines;
 List<ManagedDeviceOrm> get machines {
  if (_machines is EqualUnmodifiableListView) return _machines;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_machines);
}

 final  List<ResourceDefinitionCatalogOrm> _resourceDefinitions;
 List<ResourceDefinitionCatalogOrm> get resourceDefinitions {
  if (_resourceDefinitions is EqualUnmodifiableListView) return _resourceDefinitions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_resourceDefinitions);
}

 final  List<ResourceInstanceOrm> _resourceInstances;
 List<ResourceInstanceOrm> get resourceInstances {
  if (_resourceInstances is EqualUnmodifiableListView) return _resourceInstances;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_resourceInstances);
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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetManagementLoadSuccess&&const DeepCollectionEquality().equals(other._machines, _machines)&&const DeepCollectionEquality().equals(other._resourceDefinitions, _resourceDefinitions)&&const DeepCollectionEquality().equals(other._resourceInstances, _resourceInstances)&&const DeepCollectionEquality().equals(other._deckLayouts, _deckLayouts));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_machines),const DeepCollectionEquality().hash(_resourceDefinitions),const DeepCollectionEquality().hash(_resourceInstances),const DeepCollectionEquality().hash(_deckLayouts));

@override
String toString() {
  return 'AssetManagementState.loadSuccess(machines: $machines, resourceDefinitions: $resourceDefinitions, resourceInstances: $resourceInstances, deckLayouts: $deckLayouts)';
}


}

/// @nodoc
abstract mixin class $AssetManagementLoadSuccessCopyWith<$Res> implements $AssetManagementStateCopyWith<$Res> {
  factory $AssetManagementLoadSuccessCopyWith(AssetManagementLoadSuccess value, $Res Function(AssetManagementLoadSuccess) _then) = _$AssetManagementLoadSuccessCopyWithImpl;
@useResult
$Res call({
 List<ManagedDeviceOrm> machines, List<ResourceDefinitionCatalogOrm> resourceDefinitions, List<ResourceInstanceOrm> resourceInstances, List<DeckLayoutOrm> deckLayouts
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
@pragma('vm:prefer-inline') $Res call({Object? machines = null,Object? resourceDefinitions = null,Object? resourceInstances = null,Object? deckLayouts = null,}) {
  return _then(AssetManagementLoadSuccess(
machines: null == machines ? _self._machines : machines // ignore: cast_nullable_to_non_nullable
as List<ManagedDeviceOrm>,resourceDefinitions: null == resourceDefinitions ? _self._resourceDefinitions : resourceDefinitions // ignore: cast_nullable_to_non_nullable
as List<ResourceDefinitionCatalogOrm>,resourceInstances: null == resourceInstances ? _self._resourceInstances : resourceInstances // ignore: cast_nullable_to_non_nullable
as List<ResourceInstanceOrm>,deckLayouts: null == deckLayouts ? _self._deckLayouts : deckLayouts // ignore: cast_nullable_to_non_nullable
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
