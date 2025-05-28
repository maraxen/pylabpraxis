// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_parameter_detail.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolParameterDetail {

 bool get isRequired; dynamic get defaultValue;// 'default' is a reserved keyword in Dart
 String? get description; Map<String, dynamic>? get constraints;
/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolParameterDetailCopyWith<ProtocolParameterDetail> get copyWith => _$ProtocolParameterDetailCopyWithImpl<ProtocolParameterDetail>(this as ProtocolParameterDetail, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParameterDetail&&(identical(other.isRequired, isRequired) || other.isRequired == isRequired)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.constraints, constraints));
}


@override
int get hashCode => Object.hash(runtimeType,isRequired,const DeepCollectionEquality().hash(defaultValue),description,const DeepCollectionEquality().hash(constraints));

@override
String toString() {
  return 'ProtocolParameterDetail(isRequired: $isRequired, defaultValue: $defaultValue, description: $description, constraints: $constraints)';
}


}

/// @nodoc
abstract mixin class $ProtocolParameterDetailCopyWith<$Res>  {
  factory $ProtocolParameterDetailCopyWith(ProtocolParameterDetail value, $Res Function(ProtocolParameterDetail) _then) = _$ProtocolParameterDetailCopyWithImpl;
@useResult
$Res call({
 bool isRequired, dynamic defaultValue, String? description, Map<String, dynamic>? constraints
});




}
/// @nodoc
class _$ProtocolParameterDetailCopyWithImpl<$Res>
    implements $ProtocolParameterDetailCopyWith<$Res> {
  _$ProtocolParameterDetailCopyWithImpl(this._self, this._then);

  final ProtocolParameterDetail _self;
  final $Res Function(ProtocolParameterDetail) _then;

/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? isRequired = null,Object? defaultValue = freezed,Object? description = freezed,Object? constraints = freezed,}) {
  return _then(_self.copyWith(
isRequired: null == isRequired ? _self.isRequired : isRequired // ignore: cast_nullable_to_non_nullable
as bool,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,constraints: freezed == constraints ? _self.constraints : constraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

}


/// @nodoc


class _ProtocolParameterDetail implements ProtocolParameterDetail {
  const _ProtocolParameterDetail({required this.isRequired, this.defaultValue, this.description, final  Map<String, dynamic>? constraints}): _constraints = constraints;
  

@override final  bool isRequired;
@override final  dynamic defaultValue;
// 'default' is a reserved keyword in Dart
@override final  String? description;
 final  Map<String, dynamic>? _constraints;
@override Map<String, dynamic>? get constraints {
  final value = _constraints;
  if (value == null) return null;
  if (_constraints is EqualUnmodifiableMapView) return _constraints;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolParameterDetailCopyWith<_ProtocolParameterDetail> get copyWith => __$ProtocolParameterDetailCopyWithImpl<_ProtocolParameterDetail>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolParameterDetail&&(identical(other.isRequired, isRequired) || other.isRequired == isRequired)&&const DeepCollectionEquality().equals(other.defaultValue, defaultValue)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._constraints, _constraints));
}


@override
int get hashCode => Object.hash(runtimeType,isRequired,const DeepCollectionEquality().hash(defaultValue),description,const DeepCollectionEquality().hash(_constraints));

@override
String toString() {
  return 'ProtocolParameterDetail(isRequired: $isRequired, defaultValue: $defaultValue, description: $description, constraints: $constraints)';
}


}

/// @nodoc
abstract mixin class _$ProtocolParameterDetailCopyWith<$Res> implements $ProtocolParameterDetailCopyWith<$Res> {
  factory _$ProtocolParameterDetailCopyWith(_ProtocolParameterDetail value, $Res Function(_ProtocolParameterDetail) _then) = __$ProtocolParameterDetailCopyWithImpl;
@override @useResult
$Res call({
 bool isRequired, dynamic defaultValue, String? description, Map<String, dynamic>? constraints
});




}
/// @nodoc
class __$ProtocolParameterDetailCopyWithImpl<$Res>
    implements _$ProtocolParameterDetailCopyWith<$Res> {
  __$ProtocolParameterDetailCopyWithImpl(this._self, this._then);

  final _ProtocolParameterDetail _self;
  final $Res Function(_ProtocolParameterDetail) _then;

/// Create a copy of ProtocolParameterDetail
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? isRequired = null,Object? defaultValue = freezed,Object? description = freezed,Object? constraints = freezed,}) {
  return _then(_ProtocolParameterDetail(
isRequired: null == isRequired ? _self.isRequired : isRequired // ignore: cast_nullable_to_non_nullable
as bool,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue // ignore: cast_nullable_to_non_nullable
as dynamic,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,constraints: freezed == constraints ? _self._constraints : constraints // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}


}

// dart format on
