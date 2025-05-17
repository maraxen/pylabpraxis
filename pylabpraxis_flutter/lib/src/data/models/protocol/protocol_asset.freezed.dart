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

// A unique name or identifier for the asset within the protocol.
 String get name;// The type of asset (e.g., 'labware', 'reagent', 'instrument_module').
 String get type;// A human-readable description of the asset and its role.
 String? get description;// Indicates if this asset must be assigned by the user.
 bool get required;// Optional: Specific constraints or accepted values for this asset.
// This could be a list of IDs, a type pattern, etc.
// For simplicity, keeping as dynamic or string for now.
// Could be a more specific type if asset constraints become complex.
 dynamic get constraints;// Optional: The default value or assignment for this asset, if any.
@JsonKey(name: 'default_value') String? get defaultValue;// Optional: Current value assigned by the user during configuration.
 String? get value;
/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolAssetCopyWith<ProtocolAsset> get copyWith => _$ProtocolAssetCopyWithImpl<ProtocolAsset>(this as ProtocolAsset, _$identity);

  /// Serializes this ProtocolAsset to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAsset&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.required, required) || other.required == required)&&const DeepCollectionEquality().equals(other.constraints, constraints)&&(identical(other.defaultValue, defaultValue) || other.defaultValue == defaultValue)&&(identical(other.value, value) || other.value == value));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,required,const DeepCollectionEquality().hash(constraints),defaultValue,value);

@override
String toString() {
  return 'ProtocolAsset(name: $name, type: $type, description: $description, required: $required, constraints: $constraints, defaultValue: $defaultValue, value: $value)';
}


}

/// @nodoc
abstract mixin class $ProtocolAssetCopyWith<$Res>  {
  factory $ProtocolAssetCopyWith(ProtocolAsset value, $Res Function(ProtocolAsset) _then) = _$ProtocolAssetCopyWithImpl;
@useResult
$Res call({
 String name, String type, String? description, bool required, dynamic constraints,@JsonKey(name: 'default_value') String? defaultValue, String? value
});




}
/// @nodoc
class _$ProtocolAssetCopyWithImpl<$Res>
    implements $ProtocolAssetCopyWith<$Res> {
  _$ProtocolAssetCopyWithImpl(this._self, this._then);

  final ProtocolAsset _self;
  final $Res Function(ProtocolAsset) _then;

/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? required = null,Object? constraints = freezed,Object? defaultValue = freezed,Object? value = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as dynamic,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as String?,value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolAsset implements ProtocolAsset {
  const _ProtocolAsset({required this.name, required this.type, this.description, this.required = false, this.constraints, @JsonKey(name: 'default_value') this.defaultValue, this.value});
  factory _ProtocolAsset.fromJson(Map<String, dynamic> json) => _$ProtocolAssetFromJson(json);

// A unique name or identifier for the asset within the protocol.
@override final  String name;
// The type of asset (e.g., 'labware', 'reagent', 'instrument_module').
@override final  String type;
// A human-readable description of the asset and its role.
@override final  String? description;
// Indicates if this asset must be assigned by the user.
@override@JsonKey() final  bool required;
// Optional: Specific constraints or accepted values for this asset.
// This could be a list of IDs, a type pattern, etc.
// For simplicity, keeping as dynamic or string for now.
// Could be a more specific type if asset constraints become complex.
@override final  dynamic constraints;
// Optional: The default value or assignment for this asset, if any.
@override@JsonKey(name: 'default_value') final  String? defaultValue;
// Optional: Current value assigned by the user during configuration.
@override final  String? value;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolAsset&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.required, required) || other.required == required)&&const DeepCollectionEquality().equals(other.constraints, constraints)&&(identical(other.defaultValue, defaultValue) || other.defaultValue == defaultValue)&&(identical(other.value, value) || other.value == value));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,required,const DeepCollectionEquality().hash(constraints),defaultValue,value);

@override
String toString() {
  return 'ProtocolAsset(name: $name, type: $type, description: $description, required: $required, constraints: $constraints, defaultValue: $defaultValue, value: $value)';
}


}

/// @nodoc
abstract mixin class _$ProtocolAssetCopyWith<$Res> implements $ProtocolAssetCopyWith<$Res> {
  factory _$ProtocolAssetCopyWith(_ProtocolAsset value, $Res Function(_ProtocolAsset) _then) = __$ProtocolAssetCopyWithImpl;
@override @useResult
$Res call({
 String name, String type, String? description, bool required, dynamic constraints,@JsonKey(name: 'default_value') String? defaultValue, String? value
});




}
/// @nodoc
class __$ProtocolAssetCopyWithImpl<$Res>
    implements _$ProtocolAssetCopyWith<$Res> {
  __$ProtocolAssetCopyWithImpl(this._self, this._then);

  final _ProtocolAsset _self;
  final $Res Function(_ProtocolAsset) _then;

/// Create a copy of ProtocolAsset
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? required = null,Object? constraints = freezed,Object? defaultValue = freezed,Object? value = freezed,}) {
  return _then(_ProtocolAsset(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as dynamic,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as String?,value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
