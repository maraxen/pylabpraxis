// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'visualizer_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$VisualizerEvent implements DiagnosticableTreeMixin {




@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerEvent'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerEvent()';
}


}

/// @nodoc
class $VisualizerEventCopyWith<$Res>  {
$VisualizerEventCopyWith(VisualizerEvent _, $Res Function(VisualizerEvent) __);
}


/// @nodoc


class VisualizerLoadDeckStateRequested with DiagnosticableTreeMixin implements VisualizerEvent {
  const VisualizerLoadDeckStateRequested(this.workcellId);
  

 final  String workcellId;

/// Create a copy of VisualizerEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VisualizerLoadDeckStateRequestedCopyWith<VisualizerLoadDeckStateRequested> get copyWith => _$VisualizerLoadDeckStateRequestedCopyWithImpl<VisualizerLoadDeckStateRequested>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerEvent.loadDeckStateRequested'))
    ..add(DiagnosticsProperty('workcellId', workcellId));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerLoadDeckStateRequested&&(identical(other.workcellId, workcellId) || other.workcellId == workcellId));
}


@override
int get hashCode => Object.hash(runtimeType,workcellId);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerEvent.loadDeckStateRequested(workcellId: $workcellId)';
}


}

/// @nodoc
abstract mixin class $VisualizerLoadDeckStateRequestedCopyWith<$Res> implements $VisualizerEventCopyWith<$Res> {
  factory $VisualizerLoadDeckStateRequestedCopyWith(VisualizerLoadDeckStateRequested value, $Res Function(VisualizerLoadDeckStateRequested) _then) = _$VisualizerLoadDeckStateRequestedCopyWithImpl;
@useResult
$Res call({
 String workcellId
});




}
/// @nodoc
class _$VisualizerLoadDeckStateRequestedCopyWithImpl<$Res>
    implements $VisualizerLoadDeckStateRequestedCopyWith<$Res> {
  _$VisualizerLoadDeckStateRequestedCopyWithImpl(this._self, this._then);

  final VisualizerLoadDeckStateRequested _self;
  final $Res Function(VisualizerLoadDeckStateRequested) _then;

/// Create a copy of VisualizerEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? workcellId = null,}) {
  return _then(VisualizerLoadDeckStateRequested(
null == workcellId ? _self.workcellId : workcellId // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class VisualizerWebSocketMessageReceived with DiagnosticableTreeMixin implements VisualizerEvent {
  const VisualizerWebSocketMessageReceived(this.message);
  

 final  dynamic message;

/// Create a copy of VisualizerEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VisualizerWebSocketMessageReceivedCopyWith<VisualizerWebSocketMessageReceived> get copyWith => _$VisualizerWebSocketMessageReceivedCopyWithImpl<VisualizerWebSocketMessageReceived>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerEvent.webSocketMessageReceived'))
    ..add(DiagnosticsProperty('message', message));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerWebSocketMessageReceived&&const DeepCollectionEquality().equals(other.message, message));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(message));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerEvent.webSocketMessageReceived(message: $message)';
}


}

/// @nodoc
abstract mixin class $VisualizerWebSocketMessageReceivedCopyWith<$Res> implements $VisualizerEventCopyWith<$Res> {
  factory $VisualizerWebSocketMessageReceivedCopyWith(VisualizerWebSocketMessageReceived value, $Res Function(VisualizerWebSocketMessageReceived) _then) = _$VisualizerWebSocketMessageReceivedCopyWithImpl;
@useResult
$Res call({
 dynamic message
});




}
/// @nodoc
class _$VisualizerWebSocketMessageReceivedCopyWithImpl<$Res>
    implements $VisualizerWebSocketMessageReceivedCopyWith<$Res> {
  _$VisualizerWebSocketMessageReceivedCopyWithImpl(this._self, this._then);

  final VisualizerWebSocketMessageReceived _self;
  final $Res Function(VisualizerWebSocketMessageReceived) _then;

/// Create a copy of VisualizerEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = freezed,}) {
  return _then(VisualizerWebSocketMessageReceived(
freezed == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

/// @nodoc


class VisualizerWebSocketConnectionClosed with DiagnosticableTreeMixin implements VisualizerEvent {
  const VisualizerWebSocketConnectionClosed();
  





@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerEvent.webSocketConnectionClosed'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerWebSocketConnectionClosed);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerEvent.webSocketConnectionClosed()';
}


}




/// @nodoc


class VisualizerDisposeRequested with DiagnosticableTreeMixin implements VisualizerEvent {
  const VisualizerDisposeRequested();
  





@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerEvent.disposeRequested'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerDisposeRequested);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerEvent.disposeRequested()';
}


}




/// @nodoc
mixin _$VisualizerState implements DiagnosticableTreeMixin {




@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState()';
}


}

/// @nodoc
class $VisualizerStateCopyWith<$Res>  {
$VisualizerStateCopyWith(VisualizerState _, $Res Function(VisualizerState) __);
}


/// @nodoc


class VisualizerInitial with DiagnosticableTreeMixin implements VisualizerState {
  const VisualizerInitial();
  





@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState.initial'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState.initial()';
}


}




/// @nodoc


class VisualizerLoadInProgress with DiagnosticableTreeMixin implements VisualizerState {
  const VisualizerLoadInProgress();
  





@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState.loadInProgress'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerLoadInProgress);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState.loadInProgress()';
}


}




/// @nodoc


class VisualizerLoadSuccess with DiagnosticableTreeMixin implements VisualizerState {
  const VisualizerLoadSuccess(this.deckLayout);
  

 final  DeckLayout deckLayout;

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VisualizerLoadSuccessCopyWith<VisualizerLoadSuccess> get copyWith => _$VisualizerLoadSuccessCopyWithImpl<VisualizerLoadSuccess>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState.loadSuccess'))
    ..add(DiagnosticsProperty('deckLayout', deckLayout));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerLoadSuccess&&(identical(other.deckLayout, deckLayout) || other.deckLayout == deckLayout));
}


@override
int get hashCode => Object.hash(runtimeType,deckLayout);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState.loadSuccess(deckLayout: $deckLayout)';
}


}

/// @nodoc
abstract mixin class $VisualizerLoadSuccessCopyWith<$Res> implements $VisualizerStateCopyWith<$Res> {
  factory $VisualizerLoadSuccessCopyWith(VisualizerLoadSuccess value, $Res Function(VisualizerLoadSuccess) _then) = _$VisualizerLoadSuccessCopyWithImpl;
@useResult
$Res call({
 DeckLayout deckLayout
});


$DeckLayoutCopyWith<$Res> get deckLayout;

}
/// @nodoc
class _$VisualizerLoadSuccessCopyWithImpl<$Res>
    implements $VisualizerLoadSuccessCopyWith<$Res> {
  _$VisualizerLoadSuccessCopyWithImpl(this._self, this._then);

  final VisualizerLoadSuccess _self;
  final $Res Function(VisualizerLoadSuccess) _then;

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? deckLayout = null,}) {
  return _then(VisualizerLoadSuccess(
null == deckLayout ? _self.deckLayout : deckLayout // ignore: cast_nullable_to_non_nullable
as DeckLayout,
  ));
}

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DeckLayoutCopyWith<$Res> get deckLayout {
  
  return $DeckLayoutCopyWith<$Res>(_self.deckLayout, (value) {
    return _then(_self.copyWith(deckLayout: value));
  });
}
}

/// @nodoc


class VisualizerLoadFailure with DiagnosticableTreeMixin implements VisualizerState {
  const VisualizerLoadFailure(this.error);
  

 final  String error;

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VisualizerLoadFailureCopyWith<VisualizerLoadFailure> get copyWith => _$VisualizerLoadFailureCopyWithImpl<VisualizerLoadFailure>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState.loadFailure'))
    ..add(DiagnosticsProperty('error', error));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerLoadFailure&&(identical(other.error, error) || other.error == error));
}


@override
int get hashCode => Object.hash(runtimeType,error);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState.loadFailure(error: $error)';
}


}

/// @nodoc
abstract mixin class $VisualizerLoadFailureCopyWith<$Res> implements $VisualizerStateCopyWith<$Res> {
  factory $VisualizerLoadFailureCopyWith(VisualizerLoadFailure value, $Res Function(VisualizerLoadFailure) _then) = _$VisualizerLoadFailureCopyWithImpl;
@useResult
$Res call({
 String error
});




}
/// @nodoc
class _$VisualizerLoadFailureCopyWithImpl<$Res>
    implements $VisualizerLoadFailureCopyWith<$Res> {
  _$VisualizerLoadFailureCopyWithImpl(this._self, this._then);

  final VisualizerLoadFailure _self;
  final $Res Function(VisualizerLoadFailure) _then;

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,}) {
  return _then(VisualizerLoadFailure(
null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class VisualizerRealtimeUpdate with DiagnosticableTreeMixin implements VisualizerState {
  const VisualizerRealtimeUpdate(this.updatedData);
  

 final  dynamic updatedData;

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$VisualizerRealtimeUpdateCopyWith<VisualizerRealtimeUpdate> get copyWith => _$VisualizerRealtimeUpdateCopyWithImpl<VisualizerRealtimeUpdate>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState.realtimeUpdate'))
    ..add(DiagnosticsProperty('updatedData', updatedData));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerRealtimeUpdate&&const DeepCollectionEquality().equals(other.updatedData, updatedData));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(updatedData));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState.realtimeUpdate(updatedData: $updatedData)';
}


}

/// @nodoc
abstract mixin class $VisualizerRealtimeUpdateCopyWith<$Res> implements $VisualizerStateCopyWith<$Res> {
  factory $VisualizerRealtimeUpdateCopyWith(VisualizerRealtimeUpdate value, $Res Function(VisualizerRealtimeUpdate) _then) = _$VisualizerRealtimeUpdateCopyWithImpl;
@useResult
$Res call({
 dynamic updatedData
});




}
/// @nodoc
class _$VisualizerRealtimeUpdateCopyWithImpl<$Res>
    implements $VisualizerRealtimeUpdateCopyWith<$Res> {
  _$VisualizerRealtimeUpdateCopyWithImpl(this._self, this._then);

  final VisualizerRealtimeUpdate _self;
  final $Res Function(VisualizerRealtimeUpdate) _then;

/// Create a copy of VisualizerState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? updatedData = freezed,}) {
  return _then(VisualizerRealtimeUpdate(
freezed == updatedData ? _self.updatedData : updatedData // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

/// @nodoc


class VisualizerDisconnected with DiagnosticableTreeMixin implements VisualizerState {
  const VisualizerDisconnected();
  





@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'VisualizerState.disconnected'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is VisualizerDisconnected);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'VisualizerState.disconnected()';
}


}




// dart format on
