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

 String get type; bool get isRequired; ParameterConstraints? get constraints; String? get displayName; String? get description; dynamic get defaultValue; String? get group; String? get units; String? get examples; String? get format;
/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<ParameterConfig> get copyWith => _$ParameterConfigCopyWithImpl<ParameterConfig>(this as ParameterConfig, _$identity);

  /// Serializes this ParameterConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterConfig&&(identical(other.type, type) || other.type == type)&&(identical(other.isRequired, isRequired) || other.isRequired == isRequired)&&(identical(other.constraints, constraints) || other.constraints == constraints)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.group, group) || other.group == group)&&(identical(other.units, units) || other.units == units)&&(identical(other.examples, examples) || other.examples == examples)&&(identical(other.format, format) || other.format == format));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,isRequired,constraints,displayName,description,const DeepCollectionEquality().hash(defaultValue),group,units,examples,format);

@override
String toString() {
  return 'ParameterConfig(type: $type, isRequired: $isRequired, constraints: $constraints, displayName: $displayName, description: $description, defaultValue: $defaultValue, group: $group, units: $units, examples: $examples, format: $format)';
}


}

/// @nodoc
abstract mixin class $ParameterConfigCopyWith<$Res>  {
  factory $ParameterConfigCopyWith(ParameterConfig value, $Res Function(ParameterConfig) _then) = _$ParameterConfigCopyWithImpl;
@useResult
$Res call({
 String type, bool isRequired, ParameterConstraints? constraints, String? displayName, String? description, dynamic defaultValue, String? group, String? units, String? examples, String? format
});


$ParameterConstraintsCopyWith<$Res>? get constraints;

}
/// @nodoc
class _$ParameterConfigCopyWithImpl<$Res>
    implements $ParameterConfigCopyWith<$Res> {
  _$ParameterConfigCopyWithImpl(this._self, this._then);

  final ParameterConfig _self;
  final $Res Function(ParameterConfig) _then;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = null,Object? isRequired = null,Object? constraints = freezed,Object? displayName = freezed,Object? description = freezed,Object? defaultValue = freezed,Object? group = freezed,Object? units = freezed,Object? examples = freezed,Object? format = freezed,}) {
  return _then(_self.copyWith(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,isRequired: null == isRequired ? _self.isRequired : isRequired // ignore: cast_nullable_to_non_nullable
as bool,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as ParameterConstraints?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,group: freezed == group ? _self.group : group // ignore: cast_nullable_to_non_nullable
as String?,units: freezed == units ? _self.units : units // ignore: cast_nullable_to_non_nullable
as String?,examples: freezed == examples ? _self.examples : examples // ignore: cast_nullable_to_non_nullable
as String?,format: freezed == format ? _self.format : format // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConstraintsCopyWith<$Res>? get constraints {
    if (_self.constraints == null) {
    return null;
  }

  return $ParameterConstraintsCopyWith<$Res>(_self.constraints!, (value) {
    return _then(_self.copyWith(constraints: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ParameterConfig implements ParameterConfig {
  const _ParameterConfig({required this.type, this.isRequired = false, this.constraints, this.displayName, this.description, this.defaultValue, this.group, this.units, this.examples, this.format});
  factory _ParameterConfig.fromJson(Map<String, dynamic> json) => _$ParameterConfigFromJson(json);

@override final  String type;
@override@JsonKey() final  bool isRequired;
@override final  ParameterConstraints? constraints;
@override final  String? displayName;
@override final  String? description;
@override final  dynamic defaultValue;
@override final  String? group;
@override final  String? units;
@override final  String? examples;
@override final  String? format;

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
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterConfig&&(identical(other.type, type) || other.type == type)&&(identical(other.isRequired, isRequired) || other.isRequired == isRequired)&&(identical(other.constraints, constraints) || other.constraints == constraints)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.group, group) || other.group == group)&&(identical(other.units, units) || other.units == units)&&(identical(other.examples, examples) || other.examples == examples)&&(identical(other.format, format) || other.format == format));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,isRequired,constraints,displayName,description,const DeepCollectionEquality().hash(defaultValue),group,units,examples,format);

@override
String toString() {
  return 'ParameterConfig(type: $type, isRequired: $isRequired, constraints: $constraints, displayName: $displayName, description: $description, defaultValue: $defaultValue, group: $group, units: $units, examples: $examples, format: $format)';
}


}

/// @nodoc
abstract mixin class _$ParameterConfigCopyWith<$Res> implements $ParameterConfigCopyWith<$Res> {
  factory _$ParameterConfigCopyWith(_ParameterConfig value, $Res Function(_ParameterConfig) _then) = __$ParameterConfigCopyWithImpl;
@override @useResult
$Res call({
 String type, bool isRequired, ParameterConstraints? constraints, String? displayName, String? description, dynamic defaultValue, String? group, String? units, String? examples, String? format
});


@override $ParameterConstraintsCopyWith<$Res>? get constraints;

}
/// @nodoc
class __$ParameterConfigCopyWithImpl<$Res>
    implements _$ParameterConfigCopyWith<$Res> {
  __$ParameterConfigCopyWithImpl(this._self, this._then);

  final _ParameterConfig _self;
  final $Res Function(_ParameterConfig) _then;

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = null,Object? isRequired = null,Object? constraints = freezed,Object? displayName = freezed,Object? description = freezed,Object? defaultValue = freezed,Object? group = freezed,Object? units = freezed,Object? examples = freezed,Object? format = freezed,}) {
  return _then(_ParameterConfig(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,isRequired: null == isRequired ? _self.isRequired : isRequired // ignore: cast_nullable_to_non_nullable
as bool,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as ParameterConstraints?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,group: freezed == group ? _self.group : group // ignore: cast_nullable_to_non_nullable
as String?,units: freezed == units ? _self.units : units // ignore: cast_nullable_to_non_nullable
as String?,examples: freezed == examples ? _self.examples : examples // ignore: cast_nullable_to_non_nullable
as String?,format: freezed == format ? _self.format : format // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of ParameterConfig
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConstraintsCopyWith<$Res>? get constraints {
    if (_self.constraints == null) {
    return null;
  }

  return $ParameterConstraintsCopyWith<$Res>(_self.constraints!, (value) {
    return _then(_self.copyWith(constraints: value));
  });
}
}


/// @nodoc
mixin _$ParameterDefinition {

 String get name; String? get displayName; String? get description; dynamic get defaultValue; ParameterConfig get config;
/// Create a copy of ParameterDefinition
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterDefinitionCopyWith<ParameterDefinition> get copyWith => _$ParameterDefinitionCopyWithImpl<ParameterDefinition>(this as ParameterDefinition, _$identity);

  /// Serializes this ParameterDefinition to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterDefinition&&(identical(other.name, name) || other.name == name)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.config, config) || other.config == config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,displayName,description,const DeepCollectionEquality().hash(defaultValue),config);

@override
String toString() {
  return 'ParameterDefinition(name: $name, displayName: $displayName, description: $description, defaultValue: $defaultValue, config: $config)';
}


}

/// @nodoc
abstract mixin class $ParameterDefinitionCopyWith<$Res>  {
  factory $ParameterDefinitionCopyWith(ParameterDefinition value, $Res Function(ParameterDefinition) _then) = _$ParameterDefinitionCopyWithImpl;
@useResult
$Res call({
 String name, String? displayName, String? description, dynamic defaultValue, ParameterConfig config
});


$ParameterConfigCopyWith<$Res> get config;

}
/// @nodoc
class _$ParameterDefinitionCopyWithImpl<$Res>
    implements $ParameterDefinitionCopyWith<$Res> {
  _$ParameterDefinitionCopyWithImpl(this._self, this._then);

  final ParameterDefinition _self;
  final $Res Function(ParameterDefinition) _then;

/// Create a copy of ParameterDefinition
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? displayName = freezed,Object? description = freezed,Object? defaultValue = freezed,Object? config = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,config: null == config ? _self.config : config // ignore: cast_nullable_to_non_nullable
as ParameterConfig,
  ));
}
/// Create a copy of ParameterDefinition
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res> get config {
  
  return $ParameterConfigCopyWith<$Res>(_self.config, (value) {
    return _then(_self.copyWith(config: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ParameterDefinition implements ParameterDefinition {
  const _ParameterDefinition({required this.name, this.displayName, this.description, this.defaultValue, required this.config});
  factory _ParameterDefinition.fromJson(Map<String, dynamic> json) => _$ParameterDefinitionFromJson(json);

@override final  String name;
@override final  String? displayName;
@override final  String? description;
@override final  dynamic defaultValue;
@override final  ParameterConfig config;

/// Create a copy of ParameterDefinition
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ParameterDefinitionCopyWith<_ParameterDefinition> get copyWith => __$ParameterDefinitionCopyWithImpl<_ParameterDefinition>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ParameterDefinitionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ParameterDefinition&&(identical(other.name, name) || other.name == name)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.config, config) || other.config == config));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,displayName,description,const DeepCollectionEquality().hash(defaultValue),config);

@override
String toString() {
  return 'ParameterDefinition(name: $name, displayName: $displayName, description: $description, defaultValue: $defaultValue, config: $config)';
}


}

/// @nodoc
abstract mixin class _$ParameterDefinitionCopyWith<$Res> implements $ParameterDefinitionCopyWith<$Res> {
  factory _$ParameterDefinitionCopyWith(_ParameterDefinition value, $Res Function(_ParameterDefinition) _then) = __$ParameterDefinitionCopyWithImpl;
@override @useResult
$Res call({
 String name, String? displayName, String? description, dynamic defaultValue, ParameterConfig config
});


@override $ParameterConfigCopyWith<$Res> get config;

}
/// @nodoc
class __$ParameterDefinitionCopyWithImpl<$Res>
    implements _$ParameterDefinitionCopyWith<$Res> {
  __$ParameterDefinitionCopyWithImpl(this._self, this._then);

  final _ParameterDefinition _self;
  final $Res Function(_ParameterDefinition) _then;

/// Create a copy of ParameterDefinition
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? displayName = freezed,Object? description = freezed,Object? defaultValue = freezed,Object? config = null,}) {
  return _then(_ParameterDefinition(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,config: null == config ? _self.config : config // ignore: cast_nullable_to_non_nullable
as ParameterConfig,
  ));
}

/// Create a copy of ParameterDefinition
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterConfigCopyWith<$Res> get config {
  
  return $ParameterConfigCopyWith<$Res>(_self.config, (value) {
    return _then(_self.copyWith(config: value));
  });
}
}

// dart format on
