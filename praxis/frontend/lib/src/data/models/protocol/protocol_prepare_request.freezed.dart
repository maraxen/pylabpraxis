// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_prepare_request.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolPrepareRequest {

/// The ID of the protocol to prepare.
@JsonKey(name: 'protocol_id') String get protocolId;/// Parameters for the protocol run.
/// The key in the backend JSON is expected to be 'params'.
@JsonKey(name: 'params') Map<String, dynamic>? get params;/// Asset assignments for the protocol run.
 Map<String, String>? get assets;/// Name of the deck layout to use (if selecting an existing one).
@JsonKey(name: 'deck_layout_name') String? get deckLayoutName;/// Content of the deck layout (if uploading a new or modified one).
/// This is expected to be a JSON string or a Map representing the JSON structure.
@JsonKey(name: 'deck_layout_content') Map<String, dynamic>? get deckLayoutContent;
/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPrepareRequestCopyWith<ProtocolPrepareRequest> get copyWith => _$ProtocolPrepareRequestCopyWithImpl<ProtocolPrepareRequest>(this as ProtocolPrepareRequest, _$identity);

  /// Serializes this ProtocolPrepareRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPrepareRequest&&(identical(other.protocolId, protocolId) || other.protocolId == protocolId)&&const DeepCollectionEquality().equals(other.params, params)&&const DeepCollectionEquality().equals(other.assets, assets)&&(identical(other.deckLayoutName, deckLayoutName) || other.deckLayoutName == deckLayoutName)&&const DeepCollectionEquality().equals(other.deckLayoutContent, deckLayoutContent));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,protocolId,const DeepCollectionEquality().hash(params),const DeepCollectionEquality().hash(assets),deckLayoutName,const DeepCollectionEquality().hash(deckLayoutContent));

@override
String toString() {
  return 'ProtocolPrepareRequest(protocolId: $protocolId, params: $params, assets: $assets, deckLayoutName: $deckLayoutName, deckLayoutContent: $deckLayoutContent)';
}


}

/// @nodoc
abstract mixin class $ProtocolPrepareRequestCopyWith<$Res>  {
  factory $ProtocolPrepareRequestCopyWith(ProtocolPrepareRequest value, $Res Function(ProtocolPrepareRequest) _then) = _$ProtocolPrepareRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'protocol_id') String protocolId,@JsonKey(name: 'params') Map<String, dynamic>? params, Map<String, String>? assets,@JsonKey(name: 'deck_layout_name') String? deckLayoutName,@JsonKey(name: 'deck_layout_content') Map<String, dynamic>? deckLayoutContent
});




}
/// @nodoc
class _$ProtocolPrepareRequestCopyWithImpl<$Res>
    implements $ProtocolPrepareRequestCopyWith<$Res> {
  _$ProtocolPrepareRequestCopyWithImpl(this._self, this._then);

  final ProtocolPrepareRequest _self;
  final $Res Function(ProtocolPrepareRequest) _then;

/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? protocolId = null,Object? params = freezed,Object? assets = freezed,Object? deckLayoutName = freezed,Object? deckLayoutContent = freezed,}) {
  return _then(_self.copyWith(
protocolId: null == protocolId ? _self.protocolId : protocolId // ignore: cast_nullable_to_non_nullable
as String,params: freezed == params ? _self.params : params // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,assets: freezed == assets ? _self.assets : assets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutName: freezed == deckLayoutName ? _self.deckLayoutName : deckLayoutName // ignore: cast_nullable_to_non_nullable
as String?,deckLayoutContent: freezed == deckLayoutContent ? _self.deckLayoutContent : deckLayoutContent // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolPrepareRequest implements ProtocolPrepareRequest {
  const _ProtocolPrepareRequest({@JsonKey(name: 'protocol_id') required this.protocolId, @JsonKey(name: 'params') final  Map<String, dynamic>? params, final  Map<String, String>? assets, @JsonKey(name: 'deck_layout_name') this.deckLayoutName, @JsonKey(name: 'deck_layout_content') final  Map<String, dynamic>? deckLayoutContent}): _params = params,_assets = assets,_deckLayoutContent = deckLayoutContent;
  factory _ProtocolPrepareRequest.fromJson(Map<String, dynamic> json) => _$ProtocolPrepareRequestFromJson(json);

/// The ID of the protocol to prepare.
@override@JsonKey(name: 'protocol_id') final  String protocolId;
/// Parameters for the protocol run.
/// The key in the backend JSON is expected to be 'params'.
 final  Map<String, dynamic>? _params;
/// Parameters for the protocol run.
/// The key in the backend JSON is expected to be 'params'.
@override@JsonKey(name: 'params') Map<String, dynamic>? get params {
  final value = _params;
  if (value == null) return null;
  if (_params is EqualUnmodifiableMapView) return _params;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

/// Asset assignments for the protocol run.
 final  Map<String, String>? _assets;
/// Asset assignments for the protocol run.
@override Map<String, String>? get assets {
  final value = _assets;
  if (value == null) return null;
  if (_assets is EqualUnmodifiableMapView) return _assets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

/// Name of the deck layout to use (if selecting an existing one).
@override@JsonKey(name: 'deck_layout_name') final  String? deckLayoutName;
/// Content of the deck layout (if uploading a new or modified one).
/// This is expected to be a JSON string or a Map representing the JSON structure.
 final  Map<String, dynamic>? _deckLayoutContent;
/// Content of the deck layout (if uploading a new or modified one).
/// This is expected to be a JSON string or a Map representing the JSON structure.
@override@JsonKey(name: 'deck_layout_content') Map<String, dynamic>? get deckLayoutContent {
  final value = _deckLayoutContent;
  if (value == null) return null;
  if (_deckLayoutContent is EqualUnmodifiableMapView) return _deckLayoutContent;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolPrepareRequestCopyWith<_ProtocolPrepareRequest> get copyWith => __$ProtocolPrepareRequestCopyWithImpl<_ProtocolPrepareRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolPrepareRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolPrepareRequest&&(identical(other.protocolId, protocolId) || other.protocolId == protocolId)&&const DeepCollectionEquality().equals(other._params, _params)&&const DeepCollectionEquality().equals(other._assets, _assets)&&(identical(other.deckLayoutName, deckLayoutName) || other.deckLayoutName == deckLayoutName)&&const DeepCollectionEquality().equals(other._deckLayoutContent, _deckLayoutContent));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,protocolId,const DeepCollectionEquality().hash(_params),const DeepCollectionEquality().hash(_assets),deckLayoutName,const DeepCollectionEquality().hash(_deckLayoutContent));

@override
String toString() {
  return 'ProtocolPrepareRequest(protocolId: $protocolId, params: $params, assets: $assets, deckLayoutName: $deckLayoutName, deckLayoutContent: $deckLayoutContent)';
}


}

/// @nodoc
abstract mixin class _$ProtocolPrepareRequestCopyWith<$Res> implements $ProtocolPrepareRequestCopyWith<$Res> {
  factory _$ProtocolPrepareRequestCopyWith(_ProtocolPrepareRequest value, $Res Function(_ProtocolPrepareRequest) _then) = __$ProtocolPrepareRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'protocol_id') String protocolId,@JsonKey(name: 'params') Map<String, dynamic>? params, Map<String, String>? assets,@JsonKey(name: 'deck_layout_name') String? deckLayoutName,@JsonKey(name: 'deck_layout_content') Map<String, dynamic>? deckLayoutContent
});




}
/// @nodoc
class __$ProtocolPrepareRequestCopyWithImpl<$Res>
    implements _$ProtocolPrepareRequestCopyWith<$Res> {
  __$ProtocolPrepareRequestCopyWithImpl(this._self, this._then);

  final _ProtocolPrepareRequest _self;
  final $Res Function(_ProtocolPrepareRequest) _then;

/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? protocolId = null,Object? params = freezed,Object? assets = freezed,Object? deckLayoutName = freezed,Object? deckLayoutContent = freezed,}) {
  return _then(_ProtocolPrepareRequest(
protocolId: null == protocolId ? _self.protocolId : protocolId // ignore: cast_nullable_to_non_nullable
as String,params: freezed == params ? _self._params : params // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,assets: freezed == assets ? _self._assets : assets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutName: freezed == deckLayoutName ? _self.deckLayoutName : deckLayoutName // ignore: cast_nullable_to_non_nullable
as String?,deckLayoutContent: freezed == deckLayoutContent ? _self._deckLayoutContent : deckLayoutContent // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}


}

// dart format on
