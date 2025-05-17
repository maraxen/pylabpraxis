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

// The path or unique identifier of the protocol to be prepared.
 String get protocolPath;// The configured parameter values for the protocol run.
// The keys are parameter names (matching ParameterConfig.name),
// and values are the user-provided or default values.
 Map<String, dynamic> get parameters;// Using dynamic for values as per ProtocolParameterValue
// Asset assignments made by the user.
// The key is the asset name (matching ProtocolAsset.name),
// and the value is the assigned asset ID or resource identifier.
 Map<String, String>? get assets;// Information about the deck layout to be used.
// This could be the name/ID of a pre-existing layout or an uploaded layout file.
// If a new layout is uploaded, this might contain its temporary ID or content.
// For simplicity, using a map; this could be a more structured object.
@JsonKey(name: 'deck_layout_config') Map<String, dynamic>? get deckLayoutConfig;// Example deckLayoutConfig structures:
// For a named layout: { "name": "my_saved_layout_id" }
// For an uploaded file: { "file_id": "temp_uploaded_deck_file_id" } or potentially the file content itself if small
// Or, if the DeckLayout model is directly sent: DeckLayout? deckLayout,
// Optional: User ID or context for the preparation.
 String? get userId;// Optional: Any specific run options or overrides.
 Map<String, dynamic>? get runOptions;// Optional: A user-defined name or label for this specific run.
 String? get runLabel;
/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPrepareRequestCopyWith<ProtocolPrepareRequest> get copyWith => _$ProtocolPrepareRequestCopyWithImpl<ProtocolPrepareRequest>(this as ProtocolPrepareRequest, _$identity);

  /// Serializes this ProtocolPrepareRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPrepareRequest&&(identical(other.protocolPath, protocolPath) || other.protocolPath == protocolPath)&&const DeepCollectionEquality().equals(other.parameters, parameters)&&const DeepCollectionEquality().equals(other.assets, assets)&&const DeepCollectionEquality().equals(other.deckLayoutConfig, deckLayoutConfig)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other.runOptions, runOptions)&&(identical(other.runLabel, runLabel) || other.runLabel == runLabel));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,protocolPath,const DeepCollectionEquality().hash(parameters),const DeepCollectionEquality().hash(assets),const DeepCollectionEquality().hash(deckLayoutConfig),userId,const DeepCollectionEquality().hash(runOptions),runLabel);

@override
String toString() {
  return 'ProtocolPrepareRequest(protocolPath: $protocolPath, parameters: $parameters, assets: $assets, deckLayoutConfig: $deckLayoutConfig, userId: $userId, runOptions: $runOptions, runLabel: $runLabel)';
}


}

/// @nodoc
abstract mixin class $ProtocolPrepareRequestCopyWith<$Res>  {
  factory $ProtocolPrepareRequestCopyWith(ProtocolPrepareRequest value, $Res Function(ProtocolPrepareRequest) _then) = _$ProtocolPrepareRequestCopyWithImpl;
@useResult
$Res call({
 String protocolPath, Map<String, dynamic> parameters, Map<String, String>? assets,@JsonKey(name: 'deck_layout_config') Map<String, dynamic>? deckLayoutConfig, String? userId, Map<String, dynamic>? runOptions, String? runLabel
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
@pragma('vm:prefer-inline') @override $Res call({Object? protocolPath = null,Object? parameters = null,Object? assets = freezed,Object? deckLayoutConfig = freezed,Object? userId = freezed,Object? runOptions = freezed,Object? runLabel = freezed,}) {
  return _then(_self.copyWith(
protocolPath: null == protocolPath ? _self.protocolPath : protocolPath // ignore: cast_nullable_to_non_nullable
as String,parameters: null == parameters ? _self.parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,assets: freezed == assets ? _self.assets : assets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutConfig: freezed == deckLayoutConfig ? _self.deckLayoutConfig : deckLayoutConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,runOptions: freezed == runOptions ? _self.runOptions : runOptions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,runLabel: freezed == runLabel ? _self.runLabel : runLabel // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolPrepareRequest implements ProtocolPrepareRequest {
  const _ProtocolPrepareRequest({required this.protocolPath, required final  Map<String, dynamic> parameters, final  Map<String, String>? assets, @JsonKey(name: 'deck_layout_config') final  Map<String, dynamic>? deckLayoutConfig, this.userId, final  Map<String, dynamic>? runOptions, this.runLabel}): _parameters = parameters,_assets = assets,_deckLayoutConfig = deckLayoutConfig,_runOptions = runOptions;
  factory _ProtocolPrepareRequest.fromJson(Map<String, dynamic> json) => _$ProtocolPrepareRequestFromJson(json);

// The path or unique identifier of the protocol to be prepared.
@override final  String protocolPath;
// The configured parameter values for the protocol run.
// The keys are parameter names (matching ParameterConfig.name),
// and values are the user-provided or default values.
 final  Map<String, dynamic> _parameters;
// The configured parameter values for the protocol run.
// The keys are parameter names (matching ParameterConfig.name),
// and values are the user-provided or default values.
@override Map<String, dynamic> get parameters {
  if (_parameters is EqualUnmodifiableMapView) return _parameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_parameters);
}

// Using dynamic for values as per ProtocolParameterValue
// Asset assignments made by the user.
// The key is the asset name (matching ProtocolAsset.name),
// and the value is the assigned asset ID or resource identifier.
 final  Map<String, String>? _assets;
// Using dynamic for values as per ProtocolParameterValue
// Asset assignments made by the user.
// The key is the asset name (matching ProtocolAsset.name),
// and the value is the assigned asset ID or resource identifier.
@override Map<String, String>? get assets {
  final value = _assets;
  if (value == null) return null;
  if (_assets is EqualUnmodifiableMapView) return _assets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Information about the deck layout to be used.
// This could be the name/ID of a pre-existing layout or an uploaded layout file.
// If a new layout is uploaded, this might contain its temporary ID or content.
// For simplicity, using a map; this could be a more structured object.
 final  Map<String, dynamic>? _deckLayoutConfig;
// Information about the deck layout to be used.
// This could be the name/ID of a pre-existing layout or an uploaded layout file.
// If a new layout is uploaded, this might contain its temporary ID or content.
// For simplicity, using a map; this could be a more structured object.
@override@JsonKey(name: 'deck_layout_config') Map<String, dynamic>? get deckLayoutConfig {
  final value = _deckLayoutConfig;
  if (value == null) return null;
  if (_deckLayoutConfig is EqualUnmodifiableMapView) return _deckLayoutConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Example deckLayoutConfig structures:
// For a named layout: { "name": "my_saved_layout_id" }
// For an uploaded file: { "file_id": "temp_uploaded_deck_file_id" } or potentially the file content itself if small
// Or, if the DeckLayout model is directly sent: DeckLayout? deckLayout,
// Optional: User ID or context for the preparation.
@override final  String? userId;
// Optional: Any specific run options or overrides.
 final  Map<String, dynamic>? _runOptions;
// Optional: Any specific run options or overrides.
@override Map<String, dynamic>? get runOptions {
  final value = _runOptions;
  if (value == null) return null;
  if (_runOptions is EqualUnmodifiableMapView) return _runOptions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Optional: A user-defined name or label for this specific run.
@override final  String? runLabel;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolPrepareRequest&&(identical(other.protocolPath, protocolPath) || other.protocolPath == protocolPath)&&const DeepCollectionEquality().equals(other._parameters, _parameters)&&const DeepCollectionEquality().equals(other._assets, _assets)&&const DeepCollectionEquality().equals(other._deckLayoutConfig, _deckLayoutConfig)&&(identical(other.userId, userId) || other.userId == userId)&&const DeepCollectionEquality().equals(other._runOptions, _runOptions)&&(identical(other.runLabel, runLabel) || other.runLabel == runLabel));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,protocolPath,const DeepCollectionEquality().hash(_parameters),const DeepCollectionEquality().hash(_assets),const DeepCollectionEquality().hash(_deckLayoutConfig),userId,const DeepCollectionEquality().hash(_runOptions),runLabel);

@override
String toString() {
  return 'ProtocolPrepareRequest(protocolPath: $protocolPath, parameters: $parameters, assets: $assets, deckLayoutConfig: $deckLayoutConfig, userId: $userId, runOptions: $runOptions, runLabel: $runLabel)';
}


}

/// @nodoc
abstract mixin class _$ProtocolPrepareRequestCopyWith<$Res> implements $ProtocolPrepareRequestCopyWith<$Res> {
  factory _$ProtocolPrepareRequestCopyWith(_ProtocolPrepareRequest value, $Res Function(_ProtocolPrepareRequest) _then) = __$ProtocolPrepareRequestCopyWithImpl;
@override @useResult
$Res call({
 String protocolPath, Map<String, dynamic> parameters, Map<String, String>? assets,@JsonKey(name: 'deck_layout_config') Map<String, dynamic>? deckLayoutConfig, String? userId, Map<String, dynamic>? runOptions, String? runLabel
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
@override @pragma('vm:prefer-inline') $Res call({Object? protocolPath = null,Object? parameters = null,Object? assets = freezed,Object? deckLayoutConfig = freezed,Object? userId = freezed,Object? runOptions = freezed,Object? runLabel = freezed,}) {
  return _then(_ProtocolPrepareRequest(
protocolPath: null == protocolPath ? _self.protocolPath : protocolPath // ignore: cast_nullable_to_non_nullable
as String,parameters: null == parameters ? _self._parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,assets: freezed == assets ? _self._assets : assets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutConfig: freezed == deckLayoutConfig ? _self._deckLayoutConfig : deckLayoutConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,runOptions: freezed == runOptions ? _self._runOptions : runOptions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,runLabel: freezed == runLabel ? _self.runLabel : runLabel // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
