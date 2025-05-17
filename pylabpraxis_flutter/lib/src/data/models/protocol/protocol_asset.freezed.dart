// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_asset.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolAsset {

 String get name; String get type; String? get description; bool get required;@JsonKey(name: 'validation_config') ParameterConfig? get validationConfig;@JsonKey(name: 'allowed_extensions') List<String>? get allowedExtensions;@JsonKey(name: 'content_type') String? get contentType;
/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolAssetCopyWith<ProtocolAsset> get copyWith => _$ProtocolAssetCopyWithImpl<ProtocolAsset>(this as ProtocolAsset, _$identity);

  /// Serializes this ProtocolAsset to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAsset&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.required, required) || other.required == required)&&(identical(other.validationConfig, validationConfig) || other.validationConfig == validationConfig)&&const DeepCollectionEquality().equals(other.allowedExtensions, allowedExtensions)&&(identical(other.contentType, contentType) || other.contentType == contentType));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,required,validationConfig,const DeepCollectionEquality().hash(allowedExtensions),contentType);

@override
String toString() {
  return 'ProtocolAsset(name: $name, type: $type, description: $description, required: $required, validationConfig: $validationConfig, allowedExtensions: $allowedExtensions, contentType: $contentType)';
}


}

/// @nodoc
abstract mixin class $ProtocolAssetCopyWith<$Res>  {
  factory $ProtocolAssetCopyWith(ProtocolAsset value, $Res Function(ProtocolAsset) _then) = _$ProtocolAssetCopyWithImpl;
@useResult
$Res call({
 String name, String type, String? description, bool required,@JsonKey(name: 'validation_config') ParameterConfig? validationConfig,@JsonKey(name: 'allowed_extensions') List<String>? allowedExtensions,@JsonKey(name: 'content_type') String? contentType
});


$ParameterConfigCopyWith<$Res>? get validationConfig;

}
/// @nodoc
class _$ProtocolAssetCopyWithImpl<$Res>
    implements $ProtocolAssetCopyWith<$Res> {
  _$ProtocolAssetCopyWithImpl(this._self, this._then);

  final ProtocolAsset _self;
  final $Res Function(ProtocolAsset) _then;

/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? required = null,Object? validationConfig = freezed,Object? allowedExtensions = freezed,Object? contentType = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,validationConfig: freezed == validationConfig ? _self.validationConfig : validationConfig // ignore: cast_nullable_to_non_nullable
as ParameterConfig?,allowedExtensions: freezed == allowedExtensions ? _self.allowedExtensions : allowedExtensions // ignore: cast_nullable_to_non_nullable
as List<String>?,contentType: freezed == contentType ? _self.contentType : contentType // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res>? get validationConfig {
    if (_self.validationConfig == null) {
    return null;
  }

  return $ParameterConfigCopyWith<$Res>(_self.validationConfig!, (value) {
    return _then(_self.copyWith(validationConfig: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ProtocolAsset implements ProtocolAsset {
  const _ProtocolAsset({required this.name, required this.type, this.description, this.required = true, @JsonKey(name: 'validation_config') this.validationConfig, @JsonKey(name: 'allowed_extensions') final  List<String>? allowedExtensions, @JsonKey(name: 'content_type') this.contentType}): _allowedExtensions = allowedExtensions;
  factory _ProtocolAsset.fromJson(Map<String, dynamic> json) => _$ProtocolAssetFromJson(json);

@override final  String name;
@override final  String type;
@override final  String? description;
@override@JsonKey() final  bool required;
@override@JsonKey(name: 'validation_config') final  ParameterConfig? validationConfig;
 final  List<String>? _allowedExtensions;
@override@JsonKey(name: 'allowed_extensions') List<String>? get allowedExtensions {
  final value = _allowedExtensions;
  if (value == null) return null;
  if (_allowedExtensions is EqualUnmodifiableListView) return _allowedExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey(name: 'content_type') final  String? contentType;

/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolAssetCopyWith<_ProtocolAsset> get copyWith => __$ProtocolAssetCopyWithImpl<_ProtocolAsset>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolAssetToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolAsset&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.required, required) || other.required == required)&&(identical(other.validationConfig, validationConfig) || other.validationConfig == validationConfig)&&const DeepCollectionEquality().equals(other._allowedExtensions, _allowedExtensions)&&(identical(other.contentType, contentType) || other.contentType == contentType));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,required,validationConfig,const DeepCollectionEquality().hash(_allowedExtensions),contentType);

@override
String toString() {
  return 'ProtocolAsset(name: $name, type: $type, description: $description, required: $required, validationConfig: $validationConfig, allowedExtensions: $allowedExtensions, contentType: $contentType)';
}


}

/// @nodoc
abstract mixin class _$ProtocolAssetCopyWith<$Res> implements $ProtocolAssetCopyWith<$Res> {
  factory _$ProtocolAssetCopyWith(_ProtocolAsset value, $Res Function(_ProtocolAsset) _then) = __$ProtocolAssetCopyWithImpl;
@override @useResult
$Res call({
 String name, String type, String? description, bool required,@JsonKey(name: 'validation_config') ParameterConfig? validationConfig,@JsonKey(name: 'allowed_extensions') List<String>? allowedExtensions,@JsonKey(name: 'content_type') String? contentType
});


@override $ParameterConfigCopyWith<$Res>? get validationConfig;

}
/// @nodoc
class __$ProtocolAssetCopyWithImpl<$Res>
    implements _$ProtocolAssetCopyWith<$Res> {
  __$ProtocolAssetCopyWithImpl(this._self, this._then);

  final _ProtocolAsset _self;
  final $Res Function(_ProtocolAsset) _then;

/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? required = null,Object? validationConfig = freezed,Object? allowedExtensions = freezed,Object? contentType = freezed,}) {
  return _then(_ProtocolAsset(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,validationConfig: freezed == validationConfig ? _self.validationConfig : validationConfig // ignore: cast_nullable_to_non_nullable
as ParameterConfig?,allowedExtensions: freezed == allowedExtensions ? _self._allowedExtensions : allowedExtensions // ignore: cast_nullable_to_non_nullable
as List<String>?,contentType: freezed == contentType ? _self.contentType : contentType // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res>? get validationConfig {
    if (_self.validationConfig == null) {
    return null;
  }

  return $ParameterConfigCopyWith<$Res>(_self.validationConfig!, (value) {
    return _then(_self.copyWith(validationConfig: value));
  });
}
}

// dart format on
