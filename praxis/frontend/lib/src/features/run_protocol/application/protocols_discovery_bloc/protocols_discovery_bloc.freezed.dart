// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocols_discovery_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolsDiscoveryEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolsDiscoveryEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolsDiscoveryEvent()';
}


}

/// @nodoc
class $ProtocolsDiscoveryEventCopyWith<$Res>  {
$ProtocolsDiscoveryEventCopyWith(ProtocolsDiscoveryEvent _, $Res Function(ProtocolsDiscoveryEvent) __);
}


/// @nodoc


class FetchDiscoveredProtocols implements ProtocolsDiscoveryEvent {
  const FetchDiscoveredProtocols();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FetchDiscoveredProtocols);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolsDiscoveryEvent.fetchDiscoveredProtocols()';
}


}




/// @nodoc
mixin _$ProtocolsDiscoveryState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolsDiscoveryState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolsDiscoveryState()';
}


}

/// @nodoc
class $ProtocolsDiscoveryStateCopyWith<$Res>  {
$ProtocolsDiscoveryStateCopyWith(ProtocolsDiscoveryState _, $Res Function(ProtocolsDiscoveryState) __);
}


/// @nodoc


class ProtocolsDiscoveryInitial implements ProtocolsDiscoveryState {
  const ProtocolsDiscoveryInitial();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolsDiscoveryInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolsDiscoveryState.initial()';
}


}




/// @nodoc


class ProtocolsDiscoveryLoading implements ProtocolsDiscoveryState {
  const ProtocolsDiscoveryLoading();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolsDiscoveryLoading);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolsDiscoveryState.loading()';
}


}




/// @nodoc


class ProtocolsDiscoveryLoaded implements ProtocolsDiscoveryState {
  const ProtocolsDiscoveryLoaded({required final  List<ProtocolInfo> protocols}): _protocols = protocols;
  

 final  List<ProtocolInfo> _protocols;
 List<ProtocolInfo> get protocols {
  if (_protocols is EqualUnmodifiableListView) return _protocols;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_protocols);
}


/// Create a copy of ProtocolsDiscoveryState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolsDiscoveryLoadedCopyWith<ProtocolsDiscoveryLoaded> get copyWith => _$ProtocolsDiscoveryLoadedCopyWithImpl<ProtocolsDiscoveryLoaded>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolsDiscoveryLoaded&&const DeepCollectionEquality().equals(other._protocols, _protocols));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_protocols));

@override
String toString() {
  return 'ProtocolsDiscoveryState.loaded(protocols: $protocols)';
}


}

/// @nodoc
abstract mixin class $ProtocolsDiscoveryLoadedCopyWith<$Res> implements $ProtocolsDiscoveryStateCopyWith<$Res> {
  factory $ProtocolsDiscoveryLoadedCopyWith(ProtocolsDiscoveryLoaded value, $Res Function(ProtocolsDiscoveryLoaded) _then) = _$ProtocolsDiscoveryLoadedCopyWithImpl;
@useResult
$Res call({
 List<ProtocolInfo> protocols
});




}
/// @nodoc
class _$ProtocolsDiscoveryLoadedCopyWithImpl<$Res>
    implements $ProtocolsDiscoveryLoadedCopyWith<$Res> {
  _$ProtocolsDiscoveryLoadedCopyWithImpl(this._self, this._then);

  final ProtocolsDiscoveryLoaded _self;
  final $Res Function(ProtocolsDiscoveryLoaded) _then;

/// Create a copy of ProtocolsDiscoveryState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? protocols = null,}) {
  return _then(ProtocolsDiscoveryLoaded(
protocols: null == protocols ? _self._protocols : protocols // ignore: cast_nullable_to_non_nullable
as List<ProtocolInfo>,
  ));
}


}

/// @nodoc


class ProtocolsDiscoveryError implements ProtocolsDiscoveryState {
  const ProtocolsDiscoveryError({required this.message});
  

 final  String message;

/// Create a copy of ProtocolsDiscoveryState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolsDiscoveryErrorCopyWith<ProtocolsDiscoveryError> get copyWith => _$ProtocolsDiscoveryErrorCopyWithImpl<ProtocolsDiscoveryError>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolsDiscoveryError&&(identical(other.message, message) || other.message == message));
}


@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'ProtocolsDiscoveryState.error(message: $message)';
}


}

/// @nodoc
abstract mixin class $ProtocolsDiscoveryErrorCopyWith<$Res> implements $ProtocolsDiscoveryStateCopyWith<$Res> {
  factory $ProtocolsDiscoveryErrorCopyWith(ProtocolsDiscoveryError value, $Res Function(ProtocolsDiscoveryError) _then) = _$ProtocolsDiscoveryErrorCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class _$ProtocolsDiscoveryErrorCopyWithImpl<$Res>
    implements $ProtocolsDiscoveryErrorCopyWith<$Res> {
  _$ProtocolsDiscoveryErrorCopyWithImpl(this._self, this._then);

  final ProtocolsDiscoveryError _self;
  final $Res Function(ProtocolsDiscoveryError) _then;

/// Create a copy of ProtocolsDiscoveryState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(ProtocolsDiscoveryError(
message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
