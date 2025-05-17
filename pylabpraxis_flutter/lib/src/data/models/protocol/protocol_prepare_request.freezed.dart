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

@JsonKey(name: 'protocol_path') String get protocolPath; Map<String, dynamic> get parameters;@JsonKey(name: 'assigned_assets') Map<String, String>? get assignedAssets;@JsonKey(name: 'deck_layout_path') String? get deckLayoutPath;@JsonKey(name: 'deck_layout_content') DeckLayout? get deckLayoutContent;
/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPrepareRequestCopyWith<ProtocolPrepareRequest> get copyWith => _$ProtocolPrepareRequestCopyWithImpl<ProtocolPrepareRequest>(this as ProtocolPrepareRequest, _$identity);

  /// Serializes this ProtocolPrepareRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPrepareRequest&&(identical(other.protocolPath, protocolPath) || other.protocolPath == protocolPath)&&const DeepCollectionEquality().equals(other.parameters, parameters)&&const DeepCollectionEquality().equals(other.assignedAssets, assignedAssets)&&(identical(other.deckLayoutPath, deckLayoutPath) || other.deckLayoutPath == deckLayoutPath)&&(identical(other.deckLayoutContent, deckLayoutContent) || other.deckLayoutContent == deckLayoutContent));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,protocolPath,const DeepCollectionEquality().hash(parameters),const DeepCollectionEquality().hash(assignedAssets),deckLayoutPath,deckLayoutContent);

@override
String toString() {
  return 'ProtocolPrepareRequest(protocolPath: $protocolPath, parameters: $parameters, assignedAssets: $assignedAssets, deckLayoutPath: $deckLayoutPath, deckLayoutContent: $deckLayoutContent)';
}


}

/// @nodoc
abstract mixin class $ProtocolPrepareRequestCopyWith<$Res>  {
  factory $ProtocolPrepareRequestCopyWith(ProtocolPrepareRequest value, $Res Function(ProtocolPrepareRequest) _then) = _$ProtocolPrepareRequestCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'protocol_path') String protocolPath, Map<String, dynamic> parameters,@JsonKey(name: 'assigned_assets') Map<String, String>? assignedAssets,@JsonKey(name: 'deck_layout_path') String? deckLayoutPath,@JsonKey(name: 'deck_layout_content') DeckLayout? deckLayoutContent
});


$DeckLayoutCopyWith<$Res>? get deckLayoutContent;

}
/// @nodoc
class _$ProtocolPrepareRequestCopyWithImpl<$Res>
    implements $ProtocolPrepareRequestCopyWith<$Res> {
  _$ProtocolPrepareRequestCopyWithImpl(this._self, this._then);

  final ProtocolPrepareRequest _self;
  final $Res Function(ProtocolPrepareRequest) _then;

/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? protocolPath = null,Object? parameters = null,Object? assignedAssets = freezed,Object? deckLayoutPath = freezed,Object? deckLayoutContent = freezed,}) {
  return _then(_self.copyWith(
protocolPath: null == protocolPath ? _self.protocolPath : protocolPath // ignore: cast_nullable_to_non_nullable
as String,parameters: null == parameters ? _self.parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,assignedAssets: freezed == assignedAssets ? _self.assignedAssets : assignedAssets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutPath: freezed == deckLayoutPath ? _self.deckLayoutPath : deckLayoutPath // ignore: cast_nullable_to_non_nullable
as String?,deckLayoutContent: freezed == deckLayoutContent ? _self.deckLayoutContent : deckLayoutContent // ignore: cast_nullable_to_non_nullable
as DeckLayout?,
  ));
}
/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DeckLayoutCopyWith<$Res>? get deckLayoutContent {
    if (_self.deckLayoutContent == null) {
    return null;
  }

  return $DeckLayoutCopyWith<$Res>(_self.deckLayoutContent!, (value) {
    return _then(_self.copyWith(deckLayoutContent: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ProtocolPrepareRequest implements ProtocolPrepareRequest {
  const _ProtocolPrepareRequest({@JsonKey(name: 'protocol_path') required this.protocolPath, required final  Map<String, dynamic> parameters, @JsonKey(name: 'assigned_assets') final  Map<String, String>? assignedAssets, @JsonKey(name: 'deck_layout_path') this.deckLayoutPath, @JsonKey(name: 'deck_layout_content') this.deckLayoutContent}): _parameters = parameters,_assignedAssets = assignedAssets;
  factory _ProtocolPrepareRequest.fromJson(Map<String, dynamic> json) => _$ProtocolPrepareRequestFromJson(json);

@override@JsonKey(name: 'protocol_path') final  String protocolPath;
 final  Map<String, dynamic> _parameters;
@override Map<String, dynamic> get parameters {
  if (_parameters is EqualUnmodifiableMapView) return _parameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_parameters);
}

 final  Map<String, String>? _assignedAssets;
@override@JsonKey(name: 'assigned_assets') Map<String, String>? get assignedAssets {
  final value = _assignedAssets;
  if (value == null) return null;
  if (_assignedAssets is EqualUnmodifiableMapView) return _assignedAssets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'deck_layout_path') final  String? deckLayoutPath;
@override@JsonKey(name: 'deck_layout_content') final  DeckLayout? deckLayoutContent;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolPrepareRequest&&(identical(other.protocolPath, protocolPath) || other.protocolPath == protocolPath)&&const DeepCollectionEquality().equals(other._parameters, _parameters)&&const DeepCollectionEquality().equals(other._assignedAssets, _assignedAssets)&&(identical(other.deckLayoutPath, deckLayoutPath) || other.deckLayoutPath == deckLayoutPath)&&(identical(other.deckLayoutContent, deckLayoutContent) || other.deckLayoutContent == deckLayoutContent));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,protocolPath,const DeepCollectionEquality().hash(_parameters),const DeepCollectionEquality().hash(_assignedAssets),deckLayoutPath,deckLayoutContent);

@override
String toString() {
  return 'ProtocolPrepareRequest(protocolPath: $protocolPath, parameters: $parameters, assignedAssets: $assignedAssets, deckLayoutPath: $deckLayoutPath, deckLayoutContent: $deckLayoutContent)';
}


}

/// @nodoc
abstract mixin class _$ProtocolPrepareRequestCopyWith<$Res> implements $ProtocolPrepareRequestCopyWith<$Res> {
  factory _$ProtocolPrepareRequestCopyWith(_ProtocolPrepareRequest value, $Res Function(_ProtocolPrepareRequest) _then) = __$ProtocolPrepareRequestCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'protocol_path') String protocolPath, Map<String, dynamic> parameters,@JsonKey(name: 'assigned_assets') Map<String, String>? assignedAssets,@JsonKey(name: 'deck_layout_path') String? deckLayoutPath,@JsonKey(name: 'deck_layout_content') DeckLayout? deckLayoutContent
});


@override $DeckLayoutCopyWith<$Res>? get deckLayoutContent;

}
/// @nodoc
class __$ProtocolPrepareRequestCopyWithImpl<$Res>
    implements _$ProtocolPrepareRequestCopyWith<$Res> {
  __$ProtocolPrepareRequestCopyWithImpl(this._self, this._then);

  final _ProtocolPrepareRequest _self;
  final $Res Function(_ProtocolPrepareRequest) _then;

/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? protocolPath = null,Object? parameters = null,Object? assignedAssets = freezed,Object? deckLayoutPath = freezed,Object? deckLayoutContent = freezed,}) {
  return _then(_ProtocolPrepareRequest(
protocolPath: null == protocolPath ? _self.protocolPath : protocolPath // ignore: cast_nullable_to_non_nullable
as String,parameters: null == parameters ? _self._parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,assignedAssets: freezed == assignedAssets ? _self._assignedAssets : assignedAssets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutPath: freezed == deckLayoutPath ? _self.deckLayoutPath : deckLayoutPath // ignore: cast_nullable_to_non_nullable
as String?,deckLayoutContent: freezed == deckLayoutContent ? _self.deckLayoutContent : deckLayoutContent // ignore: cast_nullable_to_non_nullable
as DeckLayout?,
  ));
}

/// Create a copy of ProtocolPrepareRequest
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DeckLayoutCopyWith<$Res>? get deckLayoutContent {
    if (_self.deckLayoutContent == null) {
    return null;
  }

  return $DeckLayoutCopyWith<$Res>(_self.deckLayoutContent!, (value) {
    return _then(_self.copyWith(deckLayoutContent: value));
  });
}
}

// dart format on
