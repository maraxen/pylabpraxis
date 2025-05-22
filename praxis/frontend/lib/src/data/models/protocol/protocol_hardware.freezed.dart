// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_hardware.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolHardware {

// Name of the hardware component (e.g., 'pipette_p300_single', 'temperature_module').
 String get name;// Type of hardware (e.g., 'pipette', 'module', 'robot_arm').
 String get type;// Specific configuration or settings for this hardware.
// e.g., { 'mount': 'left', 'model': 'GEN2' }
 Map<String, dynamic>? get configuration;// Indicates if this hardware is mandatory for the protocol.
 bool get required;// Optional human-readable description or purpose.
 String? get description;
/// Create a copy of ProtocolHardware
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolHardwareCopyWith<ProtocolHardware> get copyWith => _$ProtocolHardwareCopyWithImpl<ProtocolHardware>(this as ProtocolHardware, _$identity);

  /// Serializes this ProtocolHardware to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolHardware&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&const DeepCollectionEquality().equals(other.configuration, configuration)&&(identical(other.required, required) || other.required == required)&&(identical(other.description, description) || other.description == description));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,const DeepCollectionEquality().hash(configuration),required,description);

@override
String toString() {
  return 'ProtocolHardware(name: $name, type: $type, configuration: $configuration, required: $required, description: $description)';
}


}

/// @nodoc
abstract mixin class $ProtocolHardwareCopyWith<$Res>  {
  factory $ProtocolHardwareCopyWith(ProtocolHardware value, $Res Function(ProtocolHardware) _then) = _$ProtocolHardwareCopyWithImpl;
@useResult
$Res call({
 String name, String type, Map<String, dynamic>? configuration, bool required, String? description
});




}
/// @nodoc
class _$ProtocolHardwareCopyWithImpl<$Res>
    implements $ProtocolHardwareCopyWith<$Res> {
  _$ProtocolHardwareCopyWithImpl(this._self, this._then);

  final ProtocolHardware _self;
  final $Res Function(ProtocolHardware) _then;

/// Create a copy of ProtocolHardware
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? type = null,Object? configuration = freezed,Object? required = null,Object? description = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,configuration: freezed == configuration ? _self.configuration : configuration // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolHardware implements ProtocolHardware {
  const _ProtocolHardware({required this.name, required this.type, final  Map<String, dynamic>? configuration, this.required = true, this.description}): _configuration = configuration;
  factory _ProtocolHardware.fromJson(Map<String, dynamic> json) => _$ProtocolHardwareFromJson(json);

// Name of the hardware component (e.g., 'pipette_p300_single', 'temperature_module').
@override final  String name;
// Type of hardware (e.g., 'pipette', 'module', 'robot_arm').
@override final  String type;
// Specific configuration or settings for this hardware.
// e.g., { 'mount': 'left', 'model': 'GEN2' }
 final  Map<String, dynamic>? _configuration;
// Specific configuration or settings for this hardware.
// e.g., { 'mount': 'left', 'model': 'GEN2' }
@override Map<String, dynamic>? get configuration {
  final value = _configuration;
  if (value == null) return null;
  if (_configuration is EqualUnmodifiableMapView) return _configuration;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Indicates if this hardware is mandatory for the protocol.
@override@JsonKey() final  bool required;
// Optional human-readable description or purpose.
@override final  String? description;

/// Create a copy of ProtocolHardware
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolHardwareCopyWith<_ProtocolHardware> get copyWith => __$ProtocolHardwareCopyWithImpl<_ProtocolHardware>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolHardwareToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolHardware&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&const DeepCollectionEquality().equals(other._configuration, _configuration)&&(identical(other.required, required) || other.required == required)&&(identical(other.description, description) || other.description == description));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,type,const DeepCollectionEquality().hash(_configuration),required,description);

@override
String toString() {
  return 'ProtocolHardware(name: $name, type: $type, configuration: $configuration, required: $required, description: $description)';
}


}

/// @nodoc
abstract mixin class _$ProtocolHardwareCopyWith<$Res> implements $ProtocolHardwareCopyWith<$Res> {
  factory _$ProtocolHardwareCopyWith(_ProtocolHardware value, $Res Function(_ProtocolHardware) _then) = __$ProtocolHardwareCopyWithImpl;
@override @useResult
$Res call({
 String name, String type, Map<String, dynamic>? configuration, bool required, String? description
});




}
/// @nodoc
class __$ProtocolHardwareCopyWithImpl<$Res>
    implements _$ProtocolHardwareCopyWith<$Res> {
  __$ProtocolHardwareCopyWithImpl(this._self, this._then);

  final _ProtocolHardware _self;
  final $Res Function(_ProtocolHardware) _then;

/// Create a copy of ProtocolHardware
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? type = null,Object? configuration = freezed,Object? required = null,Object? description = freezed,}) {
  return _then(_ProtocolHardware(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,configuration: freezed == configuration ? _self._configuration : configuration // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
