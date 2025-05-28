// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_prepare_response.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolPrepareResponse {

 String get status;// "ready" or "invalid"
 Map<String, dynamic> get config; List<String>? get errors; Map<String, dynamic>? get assetSuggestions;
/// Create a copy of ProtocolPrepareResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPrepareResponseCopyWith<ProtocolPrepareResponse> get copyWith => _$ProtocolPrepareResponseCopyWithImpl<ProtocolPrepareResponse>(this as ProtocolPrepareResponse, _$identity);

  /// Serializes this ProtocolPrepareResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPrepareResponse&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other.config, config)&&const DeepCollectionEquality().equals(other.errors, errors)&&const DeepCollectionEquality().equals(other.assetSuggestions, assetSuggestions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,status,const DeepCollectionEquality().hash(config),const DeepCollectionEquality().hash(errors),const DeepCollectionEquality().hash(assetSuggestions));

@override
String toString() {
  return 'ProtocolPrepareResponse(status: $status, config: $config, errors: $errors, assetSuggestions: $assetSuggestions)';
}


}

/// @nodoc
abstract mixin class $ProtocolPrepareResponseCopyWith<$Res>  {
  factory $ProtocolPrepareResponseCopyWith(ProtocolPrepareResponse value, $Res Function(ProtocolPrepareResponse) _then) = _$ProtocolPrepareResponseCopyWithImpl;
@useResult
$Res call({
 String status, Map<String, dynamic> config, List<String>? errors, Map<String, dynamic>? assetSuggestions
});




}
/// @nodoc
class _$ProtocolPrepareResponseCopyWithImpl<$Res>
    implements $ProtocolPrepareResponseCopyWith<$Res> {
  _$ProtocolPrepareResponseCopyWithImpl(this._self, this._then);

  final ProtocolPrepareResponse _self;
  final $Res Function(ProtocolPrepareResponse) _then;

/// Create a copy of ProtocolPrepareResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? status = null,Object? config = null,Object? errors = freezed,Object? assetSuggestions = freezed,}) {
  return _then(_self.copyWith(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,config: null == config ? _self.config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,errors: freezed == errors ? _self.errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>?,assetSuggestions: freezed == assetSuggestions ? _self.assetSuggestions : assetSuggestions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolPrepareResponse implements ProtocolPrepareResponse {
  const _ProtocolPrepareResponse({required this.status, required final  Map<String, dynamic> config, final  List<String>? errors, final  Map<String, dynamic>? assetSuggestions}): _config = config,_errors = errors,_assetSuggestions = assetSuggestions;
  factory _ProtocolPrepareResponse.fromJson(Map<String, dynamic> json) => _$ProtocolPrepareResponseFromJson(json);

@override final  String status;
// "ready" or "invalid"
 final  Map<String, dynamic> _config;
// "ready" or "invalid"
@override Map<String, dynamic> get config {
  if (_config is EqualUnmodifiableMapView) return _config;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_config);
}

 final  List<String>? _errors;
@override List<String>? get errors {
  final value = _errors;
  if (value == null) return null;
  if (_errors is EqualUnmodifiableListView) return _errors;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  Map<String, dynamic>? _assetSuggestions;
@override Map<String, dynamic>? get assetSuggestions {
  final value = _assetSuggestions;
  if (value == null) return null;
  if (_assetSuggestions is EqualUnmodifiableMapView) return _assetSuggestions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ProtocolPrepareResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolPrepareResponseCopyWith<_ProtocolPrepareResponse> get copyWith => __$ProtocolPrepareResponseCopyWithImpl<_ProtocolPrepareResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolPrepareResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolPrepareResponse&&(identical(other.status, status) || other.status == status)&&const DeepCollectionEquality().equals(other._config, _config)&&const DeepCollectionEquality().equals(other._errors, _errors)&&const DeepCollectionEquality().equals(other._assetSuggestions, _assetSuggestions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,status,const DeepCollectionEquality().hash(_config),const DeepCollectionEquality().hash(_errors),const DeepCollectionEquality().hash(_assetSuggestions));

@override
String toString() {
  return 'ProtocolPrepareResponse(status: $status, config: $config, errors: $errors, assetSuggestions: $assetSuggestions)';
}


}

/// @nodoc
abstract mixin class _$ProtocolPrepareResponseCopyWith<$Res> implements $ProtocolPrepareResponseCopyWith<$Res> {
  factory _$ProtocolPrepareResponseCopyWith(_ProtocolPrepareResponse value, $Res Function(_ProtocolPrepareResponse) _then) = __$ProtocolPrepareResponseCopyWithImpl;
@override @useResult
$Res call({
 String status, Map<String, dynamic> config, List<String>? errors, Map<String, dynamic>? assetSuggestions
});




}
/// @nodoc
class __$ProtocolPrepareResponseCopyWithImpl<$Res>
    implements _$ProtocolPrepareResponseCopyWith<$Res> {
  __$ProtocolPrepareResponseCopyWithImpl(this._self, this._then);

  final _ProtocolPrepareResponse _self;
  final $Res Function(_ProtocolPrepareResponse) _then;

/// Create a copy of ProtocolPrepareResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? status = null,Object? config = null,Object? errors = freezed,Object? assetSuggestions = freezed,}) {
  return _then(_ProtocolPrepareResponse(
status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,config: null == config ? _self._config : config // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,errors: freezed == errors ? _self._errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>?,assetSuggestions: freezed == assetSuggestions ? _self._assetSuggestions : assetSuggestions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}


}

// dart format on
