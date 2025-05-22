// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_step.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolStep {

// Unique identifier for the step.
 String get id;// Human-readable name or title of the step.
 String get name;// Detailed description of what happens in this step.
 String? get description;// The command or function to be executed in this step.
// e.g., 'aspirate', 'dispense', 'incubate', 'custom_script'.
 String get command;// Parameters specific to this command.
// Structure will depend on the command; using Map<String, dynamic> for flexibility.
// This might later be refined to use specific parameter types if commands are well-defined.
 Map<String, dynamic>? get arguments;// Estimated duration for this step (e.g., "PT5M" for 5 minutes).
@JsonKey(name: 'estimated_duration') String? get estimatedDuration;// Order of execution.
 int? get order;// Conditions under which this step should be skipped.
 String? get skipConditions;// Could be a more structured condition object later
// IDs of previous steps this step depends on.
 List<String>? get dependencies;// Resources or assets required or used in this step.
 List<String>? get resources;// e.g., names of assets defined in ProtocolDetails.assets
// Visual representation or notes for the UI.
 Map<String, dynamic>? get uiHints;
/// Create a copy of ProtocolStep
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolStepCopyWith<ProtocolStep> get copyWith => _$ProtocolStepCopyWithImpl<ProtocolStep>(this as ProtocolStep, _$identity);

  /// Serializes this ProtocolStep to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolStep&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.command, command) || other.command == command)&&const DeepCollectionEquality().equals(other.arguments, arguments)&&(identical(other.estimatedDuration, estimatedDuration) || other.estimatedDuration == estimatedDuration)&&(identical(other.order, order) || other.order == order)&&(identical(other.skipConditions, skipConditions) || other.skipConditions == skipConditions)&&const DeepCollectionEquality().equals(other.dependencies, dependencies)&&const DeepCollectionEquality().equals(other.resources, resources)&&const DeepCollectionEquality().equals(other.uiHints, uiHints));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,command,const DeepCollectionEquality().hash(arguments),estimatedDuration,order,skipConditions,const DeepCollectionEquality().hash(dependencies),const DeepCollectionEquality().hash(resources),const DeepCollectionEquality().hash(uiHints));

@override
String toString() {
  return 'ProtocolStep(id: $id, name: $name, description: $description, command: $command, arguments: $arguments, estimatedDuration: $estimatedDuration, order: $order, skipConditions: $skipConditions, dependencies: $dependencies, resources: $resources, uiHints: $uiHints)';
}


}

/// @nodoc
abstract mixin class $ProtocolStepCopyWith<$Res>  {
  factory $ProtocolStepCopyWith(ProtocolStep value, $Res Function(ProtocolStep) _then) = _$ProtocolStepCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description, String command, Map<String, dynamic>? arguments,@JsonKey(name: 'estimated_duration') String? estimatedDuration, int? order, String? skipConditions, List<String>? dependencies, List<String>? resources, Map<String, dynamic>? uiHints
});




}
/// @nodoc
class _$ProtocolStepCopyWithImpl<$Res>
    implements $ProtocolStepCopyWith<$Res> {
  _$ProtocolStepCopyWithImpl(this._self, this._then);

  final ProtocolStep _self;
  final $Res Function(ProtocolStep) _then;

/// Create a copy of ProtocolStep
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? command = null,Object? arguments = freezed,Object? estimatedDuration = freezed,Object? order = freezed,Object? skipConditions = freezed,Object? dependencies = freezed,Object? resources = freezed,Object? uiHints = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,command: null == command ? _self.command : command // ignore: cast_nullable_to_non_nullable
as String,arguments: freezed == arguments ? _self.arguments : arguments // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,estimatedDuration: freezed == estimatedDuration ? _self.estimatedDuration : estimatedDuration // ignore: cast_nullable_to_non_nullable
as String?,order: freezed == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int?,skipConditions: freezed == skipConditions ? _self.skipConditions : skipConditions // ignore: cast_nullable_to_non_nullable
as String?,dependencies: freezed == dependencies ? _self.dependencies : dependencies // ignore: cast_nullable_to_non_nullable
as List<String>?,resources: freezed == resources ? _self.resources : resources // ignore: cast_nullable_to_non_nullable
as List<String>?,uiHints: freezed == uiHints ? _self.uiHints : uiHints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolStep implements ProtocolStep {
  const _ProtocolStep({required this.id, required this.name, this.description, required this.command, final  Map<String, dynamic>? arguments, @JsonKey(name: 'estimated_duration') this.estimatedDuration, this.order, this.skipConditions, final  List<String>? dependencies, final  List<String>? resources, final  Map<String, dynamic>? uiHints}): _arguments = arguments,_dependencies = dependencies,_resources = resources,_uiHints = uiHints;
  factory _ProtocolStep.fromJson(Map<String, dynamic> json) => _$ProtocolStepFromJson(json);

// Unique identifier for the step.
@override final  String id;
// Human-readable name or title of the step.
@override final  String name;
// Detailed description of what happens in this step.
@override final  String? description;
// The command or function to be executed in this step.
// e.g., 'aspirate', 'dispense', 'incubate', 'custom_script'.
@override final  String command;
// Parameters specific to this command.
// Structure will depend on the command; using Map<String, dynamic> for flexibility.
// This might later be refined to use specific parameter types if commands are well-defined.
 final  Map<String, dynamic>? _arguments;
// Parameters specific to this command.
// Structure will depend on the command; using Map<String, dynamic> for flexibility.
// This might later be refined to use specific parameter types if commands are well-defined.
@override Map<String, dynamic>? get arguments {
  final value = _arguments;
  if (value == null) return null;
  if (_arguments is EqualUnmodifiableMapView) return _arguments;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Estimated duration for this step (e.g., "PT5M" for 5 minutes).
@override@JsonKey(name: 'estimated_duration') final  String? estimatedDuration;
// Order of execution.
@override final  int? order;
// Conditions under which this step should be skipped.
@override final  String? skipConditions;
// Could be a more structured condition object later
// IDs of previous steps this step depends on.
 final  List<String>? _dependencies;
// Could be a more structured condition object later
// IDs of previous steps this step depends on.
@override List<String>? get dependencies {
  final value = _dependencies;
  if (value == null) return null;
  if (_dependencies is EqualUnmodifiableListView) return _dependencies;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Resources or assets required or used in this step.
 final  List<String>? _resources;
// Resources or assets required or used in this step.
@override List<String>? get resources {
  final value = _resources;
  if (value == null) return null;
  if (_resources is EqualUnmodifiableListView) return _resources;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// e.g., names of assets defined in ProtocolDetails.assets
// Visual representation or notes for the UI.
 final  Map<String, dynamic>? _uiHints;
// e.g., names of assets defined in ProtocolDetails.assets
// Visual representation or notes for the UI.
@override Map<String, dynamic>? get uiHints {
  final value = _uiHints;
  if (value == null) return null;
  if (_uiHints is EqualUnmodifiableMapView) return _uiHints;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ProtocolStep
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolStepCopyWith<_ProtocolStep> get copyWith => __$ProtocolStepCopyWithImpl<_ProtocolStep>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolStepToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolStep&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.command, command) || other.command == command)&&const DeepCollectionEquality().equals(other._arguments, _arguments)&&(identical(other.estimatedDuration, estimatedDuration) || other.estimatedDuration == estimatedDuration)&&(identical(other.order, order) || other.order == order)&&(identical(other.skipConditions, skipConditions) || other.skipConditions == skipConditions)&&const DeepCollectionEquality().equals(other._dependencies, _dependencies)&&const DeepCollectionEquality().equals(other._resources, _resources)&&const DeepCollectionEquality().equals(other._uiHints, _uiHints));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,command,const DeepCollectionEquality().hash(_arguments),estimatedDuration,order,skipConditions,const DeepCollectionEquality().hash(_dependencies),const DeepCollectionEquality().hash(_resources),const DeepCollectionEquality().hash(_uiHints));

@override
String toString() {
  return 'ProtocolStep(id: $id, name: $name, description: $description, command: $command, arguments: $arguments, estimatedDuration: $estimatedDuration, order: $order, skipConditions: $skipConditions, dependencies: $dependencies, resources: $resources, uiHints: $uiHints)';
}


}

/// @nodoc
abstract mixin class _$ProtocolStepCopyWith<$Res> implements $ProtocolStepCopyWith<$Res> {
  factory _$ProtocolStepCopyWith(_ProtocolStep value, $Res Function(_ProtocolStep) _then) = __$ProtocolStepCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description, String command, Map<String, dynamic>? arguments,@JsonKey(name: 'estimated_duration') String? estimatedDuration, int? order, String? skipConditions, List<String>? dependencies, List<String>? resources, Map<String, dynamic>? uiHints
});




}
/// @nodoc
class __$ProtocolStepCopyWithImpl<$Res>
    implements _$ProtocolStepCopyWith<$Res> {
  __$ProtocolStepCopyWithImpl(this._self, this._then);

  final _ProtocolStep _self;
  final $Res Function(_ProtocolStep) _then;

/// Create a copy of ProtocolStep
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? command = null,Object? arguments = freezed,Object? estimatedDuration = freezed,Object? order = freezed,Object? skipConditions = freezed,Object? dependencies = freezed,Object? resources = freezed,Object? uiHints = freezed,}) {
  return _then(_ProtocolStep(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,command: null == command ? _self.command : command // ignore: cast_nullable_to_non_nullable
as String,arguments: freezed == arguments ? _self._arguments : arguments // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,estimatedDuration: freezed == estimatedDuration ? _self.estimatedDuration : estimatedDuration // ignore: cast_nullable_to_non_nullable
as String?,order: freezed == order ? _self.order : order // ignore: cast_nullable_to_non_nullable
as int?,skipConditions: freezed == skipConditions ? _self.skipConditions : skipConditions // ignore: cast_nullable_to_non_nullable
as String?,dependencies: freezed == dependencies ? _self._dependencies : dependencies // ignore: cast_nullable_to_non_nullable
as List<String>?,resources: freezed == resources ? _self._resources : resources // ignore: cast_nullable_to_non_nullable
as List<String>?,uiHints: freezed == uiHints ? _self._uiHints : uiHints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}


}

// dart format on
