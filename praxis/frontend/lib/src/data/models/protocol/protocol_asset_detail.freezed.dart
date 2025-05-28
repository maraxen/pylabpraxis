// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_asset_detail.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolAssetDetail {

 String get name; String get type; String? get description; bool get required;
/// Create a copy of ProtocolAssetDetail
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolAssetDetailCopyWith<ProtocolAssetDetail> get copyWith => _$ProtocolAssetDetailCopyWithImpl<ProtocolAssetDetail>(this as ProtocolAssetDetail, _$identity);

  /// Serializes this ProtocolAssetDetail to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAssetDetail&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.required, required) || other.required == required));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,required);

@override
String toString() {
  return 'ProtocolAssetDetail(name: $name, type: $type, description: $description, required: $required)';
}


}

/// @nodoc
abstract mixin class $ProtocolAssetDetailCopyWith<$Res>  {
  factory $ProtocolAssetDetailCopyWith(ProtocolAssetDetail value, $Res Function(ProtocolAssetDetail) _then) = _$ProtocolAssetDetailCopyWithImpl;
@useResult
$Res call({
 String name, String type, String? description, bool required
});




}
/// @nodoc
class _$ProtocolAssetDetailCopyWithImpl<$Res>
    implements $ProtocolAssetDetailCopyWith<$Res> {
  _$ProtocolAssetDetailCopyWithImpl(this._self, this._then);

  final ProtocolAssetDetail _self;
  final $Res Function(ProtocolAssetDetail) _then;

/// Create a copy of ProtocolAssetDetail
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? required = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolAssetDetail implements ProtocolAssetDetail {
  const _ProtocolAssetDetail({required this.name, required this.type, this.description, required this.required});
  factory _ProtocolAssetDetail.fromJson(Map<String, dynamic> json) => _$ProtocolAssetDetailFromJson(json);

@override final  String name;
@override final  String type;
@override final  String? description;
@override final  bool required;

/// Create a copy of ProtocolAssetDetail
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolAssetDetailCopyWith<_ProtocolAssetDetail> get copyWith => __$ProtocolAssetDetailCopyWithImpl<_ProtocolAssetDetail>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolAssetDetailToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolAssetDetail&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&(identical(other.required, required) || other.required == required));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,required);

@override
String toString() {
  return 'ProtocolAssetDetail(name: $name, type: $type, description: $description, required: $required)';
}


}

/// @nodoc
abstract mixin class _$ProtocolAssetDetailCopyWith<$Res> implements $ProtocolAssetDetailCopyWith<$Res> {
  factory _$ProtocolAssetDetailCopyWith(_ProtocolAssetDetail value, $Res Function(_ProtocolAssetDetail) _then) = __$ProtocolAssetDetailCopyWithImpl;
@override @useResult
$Res call({
 String name, String type, String? description, bool required
});




}
/// @nodoc
class __$ProtocolAssetDetailCopyWithImpl<$Res>
    implements _$ProtocolAssetDetailCopyWith<$Res> {
  __$ProtocolAssetDetailCopyWithImpl(this._self, this._then);

  final _ProtocolAssetDetail _self;
  final $Res Function(_ProtocolAssetDetail) _then;

/// Create a copy of ProtocolAssetDetail
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? required = null,}) {
  return _then(_ProtocolAssetDetail(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
