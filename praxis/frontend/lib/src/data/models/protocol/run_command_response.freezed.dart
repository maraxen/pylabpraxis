// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'run_command_response.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$RunCommandResponse {

 String get message;
/// Create a copy of RunCommandResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RunCommandResponseCopyWith<RunCommandResponse> get copyWith => _$RunCommandResponseCopyWithImpl<RunCommandResponse>(this as RunCommandResponse, _$identity);

  /// Serializes this RunCommandResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RunCommandResponse&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'RunCommandResponse(message: $message)';
}


}

/// @nodoc
abstract mixin class $RunCommandResponseCopyWith<$Res>  {
  factory $RunCommandResponseCopyWith(RunCommandResponse value, $Res Function(RunCommandResponse) _then) = _$RunCommandResponseCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class _$RunCommandResponseCopyWithImpl<$Res>
    implements $RunCommandResponseCopyWith<$Res> {
  _$RunCommandResponseCopyWithImpl(this._self, this._then);

  final RunCommandResponse _self;
  final $Res Function(RunCommandResponse) _then;

/// Create a copy of RunCommandResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? message = null,}) {
  return _then(_self.copyWith(
message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _RunCommandResponse implements RunCommandResponse {
  const _RunCommandResponse({required this.message});
  factory _RunCommandResponse.fromJson(Map<String, dynamic> json) => _$RunCommandResponseFromJson(json);

@override final  String message;

/// Create a copy of RunCommandResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RunCommandResponseCopyWith<_RunCommandResponse> get copyWith => __$RunCommandResponseCopyWithImpl<_RunCommandResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RunCommandResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RunCommandResponse&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'RunCommandResponse(message: $message)';
}


}

/// @nodoc
abstract mixin class _$RunCommandResponseCopyWith<$Res> implements $RunCommandResponseCopyWith<$Res> {
  factory _$RunCommandResponseCopyWith(_RunCommandResponse value, $Res Function(_RunCommandResponse) _then) = __$RunCommandResponseCopyWithImpl;
@override @useResult
$Res call({
 String message
});




}
/// @nodoc
class __$RunCommandResponseCopyWithImpl<$Res>
    implements _$RunCommandResponseCopyWith<$Res> {
  __$RunCommandResponseCopyWithImpl(this._self, this._then);

  final _RunCommandResponse _self;
  final $Res Function(_RunCommandResponse) _then;

/// Create a copy of RunCommandResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(_RunCommandResponse(
message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
