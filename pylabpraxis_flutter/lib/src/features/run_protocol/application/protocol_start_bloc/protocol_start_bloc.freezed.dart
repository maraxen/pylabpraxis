// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_start_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolStartEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolStartEvent()';
}


}

/// @nodoc
class $ProtocolStartEventCopyWith<$Res>  {
$ProtocolStartEventCopyWith(ProtocolStartEvent _, $Res Function(ProtocolStartEvent) __);
}


/// @nodoc


class InitializeStartScreen implements ProtocolStartEvent {
  const InitializeStartScreen({required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InitializeStartScreenCopyWith<InitializeStartScreen> get copyWith => _$InitializeStartScreenCopyWithImpl<InitializeStartScreen>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InitializeStartScreen&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartEvent.initializeStartScreen(preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $InitializeStartScreenCopyWith<$Res> implements $ProtocolStartEventCopyWith<$Res> {
  factory $InitializeStartScreenCopyWith(InitializeStartScreen value, $Res Function(InitializeStartScreen) _then) = _$InitializeStartScreenCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$InitializeStartScreenCopyWithImpl<$Res>
    implements $InitializeStartScreenCopyWith<$Res> {
  _$InitializeStartScreenCopyWithImpl(this._self, this._then);

  final InitializeStartScreen _self;
  final $Res Function(InitializeStartScreen) _then;

/// Create a copy of ProtocolStartEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? preparedConfig = null,}) {
  return _then(InitializeStartScreen(
preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc


class ExecuteStartProtocol implements ProtocolStartEvent {
  const ExecuteStartProtocol();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExecuteStartProtocol);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolStartEvent.executeStartProtocol()';
}


}




/// @nodoc


class ResetStart implements ProtocolStartEvent {
  const ResetStart();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ResetStart);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolStartEvent.resetStart()';
}


}




/// @nodoc


class LoadConfiguration implements ProtocolStartEvent {
  const LoadConfiguration({required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LoadConfigurationCopyWith<LoadConfiguration> get copyWith => _$LoadConfigurationCopyWithImpl<LoadConfiguration>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LoadConfiguration&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartEvent.loadConfiguration(preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $LoadConfigurationCopyWith<$Res> implements $ProtocolStartEventCopyWith<$Res> {
  factory $LoadConfigurationCopyWith(LoadConfiguration value, $Res Function(LoadConfiguration) _then) = _$LoadConfigurationCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$LoadConfigurationCopyWithImpl<$Res>
    implements $LoadConfigurationCopyWith<$Res> {
  _$LoadConfigurationCopyWithImpl(this._self, this._then);

  final LoadConfiguration _self;
  final $Res Function(LoadConfiguration) _then;

/// Create a copy of ProtocolStartEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? preparedConfig = null,}) {
  return _then(LoadConfiguration(
preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc


class ReportError implements ProtocolStartEvent {
  const ReportError({required this.error, required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  String error;
 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportErrorCopyWith<ReportError> get copyWith => _$ReportErrorCopyWithImpl<ReportError>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReportError&&(identical(other.error, error) || other.error == error)&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,error,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartEvent.reportError(error: $error, preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $ReportErrorCopyWith<$Res> implements $ProtocolStartEventCopyWith<$Res> {
  factory $ReportErrorCopyWith(ReportError value, $Res Function(ReportError) _then) = _$ReportErrorCopyWithImpl;
@useResult
$Res call({
 String error, Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$ReportErrorCopyWithImpl<$Res>
    implements $ReportErrorCopyWith<$Res> {
  _$ReportErrorCopyWithImpl(this._self, this._then);

  final ReportError _self;
  final $Res Function(ReportError) _then;

/// Create a copy of ProtocolStartEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,Object? preparedConfig = null,}) {
  return _then(ReportError(
error: null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc
mixin _$ProtocolStartState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolStartState()';
}


}

/// @nodoc
class $ProtocolStartStateCopyWith<$Res>  {
$ProtocolStartStateCopyWith(ProtocolStartState _, $Res Function(ProtocolStartState) __);
}


/// @nodoc


class ProtocolStartInitial implements ProtocolStartState {
  const ProtocolStartInitial();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolStartState.initial()';
}


}




/// @nodoc


class ProtocolStartReady implements ProtocolStartState {
  const ProtocolStartReady({required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolStartReadyCopyWith<ProtocolStartReady> get copyWith => _$ProtocolStartReadyCopyWithImpl<ProtocolStartReady>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartReady&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartState.ready(preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $ProtocolStartReadyCopyWith<$Res> implements $ProtocolStartStateCopyWith<$Res> {
  factory $ProtocolStartReadyCopyWith(ProtocolStartReady value, $Res Function(ProtocolStartReady) _then) = _$ProtocolStartReadyCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$ProtocolStartReadyCopyWithImpl<$Res>
    implements $ProtocolStartReadyCopyWith<$Res> {
  _$ProtocolStartReadyCopyWithImpl(this._self, this._then);

  final ProtocolStartReady _self;
  final $Res Function(ProtocolStartReady) _then;

/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? preparedConfig = null,}) {
  return _then(ProtocolStartReady(
preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc


class ProtocolStartingExecution implements ProtocolStartState {
  const ProtocolStartingExecution({required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolStartingExecutionCopyWith<ProtocolStartingExecution> get copyWith => _$ProtocolStartingExecutionCopyWithImpl<ProtocolStartingExecution>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartingExecution&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartState.startingExecution(preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $ProtocolStartingExecutionCopyWith<$Res> implements $ProtocolStartStateCopyWith<$Res> {
  factory $ProtocolStartingExecutionCopyWith(ProtocolStartingExecution value, $Res Function(ProtocolStartingExecution) _then) = _$ProtocolStartingExecutionCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$ProtocolStartingExecutionCopyWithImpl<$Res>
    implements $ProtocolStartingExecutionCopyWith<$Res> {
  _$ProtocolStartingExecutionCopyWithImpl(this._self, this._then);

  final ProtocolStartingExecution _self;
  final $Res Function(ProtocolStartingExecution) _then;

/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? preparedConfig = null,}) {
  return _then(ProtocolStartingExecution(
preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc


class ProtocolStartSuccess implements ProtocolStartState {
  const ProtocolStartSuccess({required this.response, required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  ProtocolStatusResponse response;
 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolStartSuccessCopyWith<ProtocolStartSuccess> get copyWith => _$ProtocolStartSuccessCopyWithImpl<ProtocolStartSuccess>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartSuccess&&(identical(other.response, response) || other.response == response)&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,response,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartState.success(response: $response, preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $ProtocolStartSuccessCopyWith<$Res> implements $ProtocolStartStateCopyWith<$Res> {
  factory $ProtocolStartSuccessCopyWith(ProtocolStartSuccess value, $Res Function(ProtocolStartSuccess) _then) = _$ProtocolStartSuccessCopyWithImpl;
@useResult
$Res call({
 ProtocolStatusResponse response, Map<String, dynamic> preparedConfig
});


$ProtocolStatusResponseCopyWith<$Res> get response;

}
/// @nodoc
class _$ProtocolStartSuccessCopyWithImpl<$Res>
    implements $ProtocolStartSuccessCopyWith<$Res> {
  _$ProtocolStartSuccessCopyWithImpl(this._self, this._then);

  final ProtocolStartSuccess _self;
  final $Res Function(ProtocolStartSuccess) _then;

/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? response = null,Object? preparedConfig = null,}) {
  return _then(ProtocolStartSuccess(
response: null == response ? _self.response : response // ignore: cast_nullable_to_non_nullable
as ProtocolStatusResponse,preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolStatusResponseCopyWith<$Res> get response {
  
  return $ProtocolStatusResponseCopyWith<$Res>(_self.response, (value) {
    return _then(_self.copyWith(response: value));
  });
}
}

/// @nodoc


class ProtocolStartFailure implements ProtocolStartState {
  const ProtocolStartFailure({required this.error, required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  String error;
 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolStartFailureCopyWith<ProtocolStartFailure> get copyWith => _$ProtocolStartFailureCopyWithImpl<ProtocolStartFailure>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStartFailure&&(identical(other.error, error) || other.error == error)&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,error,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolStartState.failure(error: $error, preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $ProtocolStartFailureCopyWith<$Res> implements $ProtocolStartStateCopyWith<$Res> {
  factory $ProtocolStartFailureCopyWith(ProtocolStartFailure value, $Res Function(ProtocolStartFailure) _then) = _$ProtocolStartFailureCopyWithImpl;
@useResult
$Res call({
 String error, Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$ProtocolStartFailureCopyWithImpl<$Res>
    implements $ProtocolStartFailureCopyWith<$Res> {
  _$ProtocolStartFailureCopyWithImpl(this._self, this._then);

  final ProtocolStartFailure _self;
  final $Res Function(ProtocolStartFailure) _then;

/// Create a copy of ProtocolStartState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,Object? preparedConfig = null,}) {
  return _then(ProtocolStartFailure(
error: null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
