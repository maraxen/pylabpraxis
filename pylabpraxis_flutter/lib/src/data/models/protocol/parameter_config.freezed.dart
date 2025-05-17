// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'parameter_config.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ParameterConfig {

 String get name; String get type; String? get description;@JsonKey(name: 'default_value') dynamic get defaultValue;// The 'value' field has been removed as it represents runtime state,
// not static configuration.
 Map<String, dynamic>? get constraints; bool get required; String? get group; String? get label; bool get hidden;
/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<ParameterConfig> get copyWith => _$ParameterConfigCopyWithImpl<ParameterConfig>(this as ParameterConfig, _$identity);

  /// Serializes this ParameterConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterConfig&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&const DeepCollectionEquality().equals(other.constraints, constraints)&&(identical(other.required, required) || other.required == required)&&(identical(other.group, group) || other.group == group)&&(identical(other.label, label) || other.label == label)&&(identical(other.hidden, hidden) || other.hidden == hidden));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,const DeepCollectionEquality().hash(defaultValue),const DeepCollectionEquality().hash(constraints),required,group,label,hidden);

@override
String toString() {
  return 'ParameterConfig(name: $name, type: $type, description: $description, defaultValue: $defaultValue, constraints: $constraints, required: $required, group: $group, label: $label, hidden: $hidden)';
}


}

/// @nodoc
abstract mixin class $ParameterConfigCopyWith<$Res>  {
  factory $ParameterConfigCopyWith(ParameterConfig value, $Res Function(ParameterConfig) _then) = _$ParameterConfigCopyWithImpl;
@useResult
$Res call({
 String name, String type, String? description,@JsonKey(name: 'default_value') dynamic defaultValue, Map<String, dynamic>? constraints, bool required, String? group, String? label, bool hidden
});




}
/// @nodoc
class _$ParameterConfigCopyWithImpl<$Res>
    implements $ParameterConfigCopyWith<$Res> {
  _$ParameterConfigCopyWithImpl(this._self, this._then);

  final ParameterConfig _self;
  final $Res Function(ParameterConfig) _then;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? defaultValue = freezed,Object? constraints = freezed,Object? required = null,Object? group = freezed,Object? label = freezed,Object? hidden = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,group: freezed == group ? _self.group : group // ignore: cast_nullable_to_non_nullable
as String?,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,hidden: null == hidden ? _self.hidden : hidden // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ParameterConfig implements ParameterConfig {
  const _ParameterConfig({required this.name, required this.type, this.description, @JsonKey(name: 'default_value') this.defaultValue, final  Map<String, dynamic>? constraints, this.required = false, this.group, this.label, this.hidden = false}): _constraints = constraints;
  factory _ParameterConfig.fromJson(Map<String, dynamic> json) => _$ParameterConfigFromJson(json);

@override final  String name;
@override final  String type;
@override final  String? description;
@override@JsonKey(name: 'default_value') final  dynamic defaultValue;
// The 'value' field has been removed as it represents runtime state,
// not static configuration.
 final  Map<String, dynamic>? _constraints;
// The 'value' field has been removed as it represents runtime state,
// not static configuration.
@override Map<String, dynamic>? get constraints {
  final value = _constraints;
  if (value == null) return null;
  if (_constraints is EqualUnmodifiableMapView) return _constraints;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey() final  bool required;
@override final  String? group;
@override final  String? label;
@override@JsonKey() final  bool hidden;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParameterConfigCopyWith<_ParameterConfig> get copyWith => __$ParameterConfigCopyWithImpl<_ParameterConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParameterConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterConfig&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&const DeepCollectionEquality().equals(other._constraints, _constraints)&&(identical(other.required, required) || other.required == required)&&(identical(other.group, group) || other.group == group)&&(identical(other.label, label) || other.label == label)&&(identical(other.hidden, hidden) || other.hidden == hidden));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,description,const DeepCollectionEquality().hash(defaultValue),const DeepCollectionEquality().hash(_constraints),required,group,label,hidden);

@override
String toString() {
  return 'ParameterConfig(name: $name, type: $type, description: $description, defaultValue: $defaultValue, constraints: $constraints, required: $required, group: $group, label: $label, hidden: $hidden)';
}


}

/// @nodoc
abstract mixin class _$ParameterConfigCopyWith<$Res> implements $ParameterConfigCopyWith<$Res> {
  factory _$ParameterConfigCopyWith(_ParameterConfig value, $Res Function(_ParameterConfig) _then) = __$ParameterConfigCopyWithImpl;
@override @useResult
$Res call({
 String name, String type, String? description,@JsonKey(name: 'default_value') dynamic defaultValue, Map<String, dynamic>? constraints, bool required, String? group, String? label, bool hidden
});




}
/// @nodoc
class __$ParameterConfigCopyWithImpl<$Res>
    implements _$ParameterConfigCopyWith<$Res> {
  __$ParameterConfigCopyWithImpl(this._self, this._then);

  final _ParameterConfig _self;
  final $Res Function(_ParameterConfig) _then;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? type = null,Object? description = freezed,Object? defaultValue = freezed,Object? constraints = freezed,Object? required = null,Object? group = freezed,Object? label = freezed,Object? hidden = null,}) {
  return _then(_ParameterConfig(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,constraints: freezed == constraints ? _self._constraints : constraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,group: freezed == group ? _self.group : group // ignore: cast_nullable_to_non_nullable
as String?,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,hidden: null == hidden ? _self.hidden : hidden // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$DictionaryConstraints {

@JsonKey(name: 'key_constraints') ParameterConfig? get keyConstraints;@JsonKey(name: 'value_constraints') ParameterConfig? get valueConstraints;
/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DictionaryConstraintsCopyWith<DictionaryConstraints> get copyWith => _$DictionaryConstraintsCopyWithImpl<DictionaryConstraints>(this as DictionaryConstraints, _$identity);

  /// Serializes this DictionaryConstraints to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DictionaryConstraints&&(identical(other.keyConstraints, keyConstraints) || other.keyConstraints == keyConstraints)&&(identical(other.valueConstraints, valueConstraints) || other.valueConstraints == valueConstraints));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,keyConstraints,valueConstraints);

@override
String toString() {
  return 'DictionaryConstraints(keyConstraints: $keyConstraints, valueConstraints: $valueConstraints)';
}


}

/// @nodoc
abstract mixin class $DictionaryConstraintsCopyWith<$Res>  {
  factory $DictionaryConstraintsCopyWith(DictionaryConstraints value, $Res Function(DictionaryConstraints) _then) = _$DictionaryConstraintsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'key_constraints') ParameterConfig? keyConstraints,@JsonKey(name: 'value_constraints') ParameterConfig? valueConstraints
});


$ParameterConfigCopyWith<$Res>? get keyConstraints;$ParameterConfigCopyWith<$Res>? get valueConstraints;

}
/// @nodoc
class _$DictionaryConstraintsCopyWithImpl<$Res>
    implements $DictionaryConstraintsCopyWith<$Res> {
  _$DictionaryConstraintsCopyWithImpl(this._self, this._then);

  final DictionaryConstraints _self;
  final $Res Function(DictionaryConstraints) _then;

/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? keyConstraints = freezed,Object? valueConstraints = freezed,}) {
  return _then(_self.copyWith(
keyConstraints: freezed == keyConstraints ? _self.keyConstraints : keyConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConfig?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConfig?,
  ));
}
/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res>? get keyConstraints {
    if (_self.keyConstraints == null) {
    return null;
  }

  return $ParameterConfigCopyWith<$Res>(_self.keyConstraints!, (value) {
    return _then(_self.copyWith(keyConstraints: value));
  });
}/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res>? get valueConstraints {
    if (_self.valueConstraints == null) {
    return null;
  }

  return $ParameterConfigCopyWith<$Res>(_self.valueConstraints!, (value) {
    return _then(_self.copyWith(valueConstraints: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _DictionaryConstraints implements DictionaryConstraints {
  const _DictionaryConstraints({@JsonKey(name: 'key_constraints') this.keyConstraints, @JsonKey(name: 'value_constraints') this.valueConstraints});
  factory _DictionaryConstraints.fromJson(Map<String, dynamic> json) => _$DictionaryConstraintsFromJson(json);

@override@JsonKey(name: 'key_constraints') final  ParameterConfig? keyConstraints;
@override@JsonKey(name: 'value_constraints') final  ParameterConfig? valueConstraints;

/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DictionaryConstraintsCopyWith<_DictionaryConstraints> get copyWith => __$DictionaryConstraintsCopyWithImpl<_DictionaryConstraints>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DictionaryConstraintsToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DictionaryConstraints&&(identical(other.keyConstraints, keyConstraints) || other.keyConstraints == keyConstraints)&&(identical(other.valueConstraints, valueConstraints) || other.valueConstraints == valueConstraints));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,keyConstraints,valueConstraints);

@override
String toString() {
  return 'DictionaryConstraints(keyConstraints: $keyConstraints, valueConstraints: $valueConstraints)';
}


}

/// @nodoc
abstract mixin class _$DictionaryConstraintsCopyWith<$Res> implements $DictionaryConstraintsCopyWith<$Res> {
  factory _$DictionaryConstraintsCopyWith(_DictionaryConstraints value, $Res Function(_DictionaryConstraints) _then) = __$DictionaryConstraintsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'key_constraints') ParameterConfig? keyConstraints,@JsonKey(name: 'value_constraints') ParameterConfig? valueConstraints
});


@override $ParameterConfigCopyWith<$Res>? get keyConstraints;@override $ParameterConfigCopyWith<$Res>? get valueConstraints;

}
/// @nodoc
class __$DictionaryConstraintsCopyWithImpl<$Res>
    implements _$DictionaryConstraintsCopyWith<$Res> {
  __$DictionaryConstraintsCopyWithImpl(this._self, this._then);

  final _DictionaryConstraints _self;
  final $Res Function(_DictionaryConstraints) _then;

/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? keyConstraints = freezed,Object? valueConstraints = freezed,}) {
  return _then(_DictionaryConstraints(
keyConstraints: freezed == keyConstraints ? _self.keyConstraints : keyConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConfig?,valueConstraints: freezed == valueConstraints ? _self.valueConstraints : valueConstraints // ignore: cast_nullable_to_non_nullable
as ParameterConfig?,
  ));
}

/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res>? get keyConstraints {
    if (_self.keyConstraints == null) {
    return null;
  }

  return $ParameterConfigCopyWith<$Res>(_self.keyConstraints!, (value) {
    return _then(_self.copyWith(keyConstraints: value));
  });
}/// Create a copy of DictionaryConstraints
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res>? get valueConstraints {
    if (_self.valueConstraints == null) {
    return null;
  }

  return $ParameterConfigCopyWith<$Res>(_self.valueConstraints!, (value) {
    return _then(_self.copyWith(valueConstraints: value));
  });
}
}


/// @nodoc
mixin _$ParamConstraint {

 String get param;
/// Create a copy of ParamConstraint
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParamConstraintCopyWith<ParamConstraint> get copyWith => _$ParamConstraintCopyWithImpl<ParamConstraint>(this as ParamConstraint, _$identity);

  /// Serializes this ParamConstraint to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParamConstraint&&(identical(other.param, param) || other.param == param));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,param);

@override
String toString() {
  return 'ParamConstraint(param: $param)';
}


}

/// @nodoc
abstract mixin class $ParamConstraintCopyWith<$Res>  {
  factory $ParamConstraintCopyWith(ParamConstraint value, $Res Function(ParamConstraint) _then) = _$ParamConstraintCopyWithImpl;
@useResult
$Res call({
 String param
});




}
/// @nodoc
class _$ParamConstraintCopyWithImpl<$Res>
    implements $ParamConstraintCopyWith<$Res> {
  _$ParamConstraintCopyWithImpl(this._self, this._then);

  final ParamConstraint _self;
  final $Res Function(ParamConstraint) _then;

/// Create a copy of ParamConstraint
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? param = null,}) {
  return _then(_self.copyWith(
param: null == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ParamConstraint implements ParamConstraint {
  const _ParamConstraint({required this.param});
  factory _ParamConstraint.fromJson(Map<String, dynamic> json) => _$ParamConstraintFromJson(json);

@override final  String param;

/// Create a copy of ParamConstraint
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParamConstraintCopyWith<_ParamConstraint> get copyWith => __$ParamConstraintCopyWithImpl<_ParamConstraint>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParamConstraintToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParamConstraint&&(identical(other.param, param) || other.param == param));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,param);

@override
String toString() {
  return 'ParamConstraint(param: $param)';
}


}

/// @nodoc
abstract mixin class _$ParamConstraintCopyWith<$Res> implements $ParamConstraintCopyWith<$Res> {
  factory _$ParamConstraintCopyWith(_ParamConstraint value, $Res Function(_ParamConstraint) _then) = __$ParamConstraintCopyWithImpl;
@override @useResult
$Res call({
 String param
});




}
/// @nodoc
class __$ParamConstraintCopyWithImpl<$Res>
    implements _$ParamConstraintCopyWith<$Res> {
  __$ParamConstraintCopyWithImpl(this._self, this._then);

  final _ParamConstraint _self;
  final $Res Function(_ParamConstraint) _then;

/// Create a copy of ParamConstraint
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? param = null,}) {
  return _then(_ParamConstraint(
param: null == param ? _self.param : param // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
