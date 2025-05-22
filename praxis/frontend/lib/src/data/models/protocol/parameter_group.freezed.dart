// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'parameter_group.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ParameterGroup {

 String get name; String? get displayName; String? get description; List<ParameterDefinition> get parameters;
/// Create a copy of ParameterGroup
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterGroupCopyWith<ParameterGroup> get copyWith => _$ParameterGroupCopyWithImpl<ParameterGroup>(this as ParameterGroup, _$identity);

  /// Serializes this ParameterGroup to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterGroup&&(identical(other.name, name) || other.name == name)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.parameters, parameters));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,displayName,description,const DeepCollectionEquality().hash(parameters));

@override
String toString() {
  return 'ParameterGroup(name: $name, displayName: $displayName, description: $description, parameters: $parameters)';
}


}

/// @nodoc
abstract mixin class $ParameterGroupCopyWith<$Res>  {
  factory $ParameterGroupCopyWith(ParameterGroup value, $Res Function(ParameterGroup) _then) = _$ParameterGroupCopyWithImpl;
@useResult
$Res call({
 String name, String? displayName, String? description, List<ParameterDefinition> parameters
});




}
/// @nodoc
class _$ParameterGroupCopyWithImpl<$Res>
    implements $ParameterGroupCopyWith<$Res> {
  _$ParameterGroupCopyWithImpl(this._self, this._then);

  final ParameterGroup _self;
  final $Res Function(ParameterGroup) _then;

/// Create a copy of ParameterGroup
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? displayName = freezed,Object? description = freezed,Object? parameters = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,parameters: null == parameters ? _self.parameters : parameters // ignore: cast_nullable_to_non_nullable
as List<ParameterDefinition>,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ParameterGroup implements ParameterGroup {
  const _ParameterGroup({required this.name, this.displayName, this.description, final  List<ParameterDefinition> parameters = const []}): _parameters = parameters;
  factory _ParameterGroup.fromJson(Map<String, dynamic> json) => _$ParameterGroupFromJson(json);

@override final  String name;
@override final  String? displayName;
@override final  String? description;
 final  List<ParameterDefinition> _parameters;
@override@JsonKey() List<ParameterDefinition> get parameters {
  if (_parameters is EqualUnmodifiableListView) return _parameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_parameters);
}


/// Create a copy of ParameterGroup
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParameterGroupCopyWith<_ParameterGroup> get copyWith => __$ParameterGroupCopyWithImpl<_ParameterGroup>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParameterGroupToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterGroup&&(identical(other.name, name) || other.name == name)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._parameters, _parameters));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,displayName,description,const DeepCollectionEquality().hash(_parameters));

@override
String toString() {
  return 'ParameterGroup(name: $name, displayName: $displayName, description: $description, parameters: $parameters)';
}


}

/// @nodoc
abstract mixin class _$ParameterGroupCopyWith<$Res> implements $ParameterGroupCopyWith<$Res> {
  factory _$ParameterGroupCopyWith(_ParameterGroup value, $Res Function(_ParameterGroup) _then) = __$ParameterGroupCopyWithImpl;
@override @useResult
$Res call({
 String name, String? displayName, String? description, List<ParameterDefinition> parameters
});




}
/// @nodoc
class __$ParameterGroupCopyWithImpl<$Res>
    implements _$ParameterGroupCopyWith<$Res> {
  __$ParameterGroupCopyWithImpl(this._self, this._then);

  final _ParameterGroup _self;
  final $Res Function(_ParameterGroup) _then;

/// Create a copy of ParameterGroup
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? displayName = freezed,Object? description = freezed,Object? parameters = null,}) {
  return _then(_ParameterGroup(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,parameters: null == parameters ? _self._parameters : parameters // ignore: cast_nullable_to_non_nullable
as List<ParameterDefinition>,
  ));
}


}

// dart format on
