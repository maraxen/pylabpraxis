// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_details.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolDetails {

 String get name; String get path; String get description; Map<String, ParameterConfig> get parameters;// UPDATE this line
 List<ProtocolAssetDetail> get assets; bool get hasAssets; bool get hasParameters; bool get requiresConfig;
/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolDetailsCopyWith<ProtocolDetails> get copyWith => _$ProtocolDetailsCopyWithImpl<ProtocolDetails>(this as ProtocolDetails, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolDetails&&(identical(other.name, name) || other.name == name)&&(identical(other.path, path) || other.path == path)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.parameters, parameters)&&const DeepCollectionEquality().equals(other.assets, assets)&&(identical(other.hasAssets, hasAssets) || other.hasAssets == hasAssets)&&(identical(other.hasParameters, hasParameters) || other.hasParameters == hasParameters)&&(identical(other.requiresConfig, requiresConfig) || other.requiresConfig == requiresConfig));
}


@override
int get hashCode => Object.hash(runtimeType,name,path,description,const DeepCollectionEquality().hash(parameters),const DeepCollectionEquality().hash(assets),hasAssets,hasParameters,requiresConfig);

@override
String toString() {
  return 'ProtocolDetails(name: $name, path: $path, description: $description, parameters: $parameters, assets: $assets, hasAssets: $hasAssets, hasParameters: $hasParameters, requiresConfig: $requiresConfig)';
}


}

/// @nodoc
abstract mixin class $ProtocolDetailsCopyWith<$Res>  {
  factory $ProtocolDetailsCopyWith(ProtocolDetails value, $Res Function(ProtocolDetails) _then) = _$ProtocolDetailsCopyWithImpl;
@useResult
$Res call({
 String name, String path, String description, Map<String, ParameterConfig> parameters, List<ProtocolAssetDetail> assets, bool hasAssets, bool hasParameters, bool requiresConfig
});




}
/// @nodoc
class _$ProtocolDetailsCopyWithImpl<$Res>
    implements $ProtocolDetailsCopyWith<$Res> {
  _$ProtocolDetailsCopyWithImpl(this._self, this._then);

  final ProtocolDetails _self;
  final $Res Function(ProtocolDetails) _then;

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? path = null,Object? description = null,Object? parameters = null,Object? assets = null,Object? hasAssets = null,Object? hasParameters = null,Object? requiresConfig = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,path: null == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,parameters: null == parameters ? _self.parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>,assets: null == assets ? _self.assets : assets // ignore: cast_nullable_to_non_nullable
as List<ProtocolAssetDetail>,hasAssets: null == hasAssets ? _self.hasAssets : hasAssets // ignore: cast_nullable_to_non_nullable
as bool,hasParameters: null == hasParameters ? _self.hasParameters : hasParameters // ignore: cast_nullable_to_non_nullable
as bool,requiresConfig: null == requiresConfig ? _self.requiresConfig : requiresConfig // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// @nodoc


class _ProtocolDetails implements ProtocolDetails {
  const _ProtocolDetails({required this.name, required this.path, required this.description, required final  Map<String, ParameterConfig> parameters, required final  List<ProtocolAssetDetail> assets, required this.hasAssets, required this.hasParameters, required this.requiresConfig}): _parameters = parameters,_assets = assets;
  

@override final  String name;
@override final  String path;
@override final  String description;
 final  Map<String, ParameterConfig> _parameters;
@override Map<String, ParameterConfig> get parameters {
  if (_parameters is EqualUnmodifiableMapView) return _parameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_parameters);
}

// UPDATE this line
 final  List<ProtocolAssetDetail> _assets;
// UPDATE this line
@override List<ProtocolAssetDetail> get assets {
  if (_assets is EqualUnmodifiableListView) return _assets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_assets);
}

@override final  bool hasAssets;
@override final  bool hasParameters;
@override final  bool requiresConfig;

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolDetailsCopyWith<_ProtocolDetails> get copyWith => __$ProtocolDetailsCopyWithImpl<_ProtocolDetails>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolDetails&&(identical(other.name, name) || other.name == name)&&(identical(other.path, path) || other.path == path)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._parameters, _parameters)&&const DeepCollectionEquality().equals(other._assets, _assets)&&(identical(other.hasAssets, hasAssets) || other.hasAssets == hasAssets)&&(identical(other.hasParameters, hasParameters) || other.hasParameters == hasParameters)&&(identical(other.requiresConfig, requiresConfig) || other.requiresConfig == requiresConfig));
}


@override
int get hashCode => Object.hash(runtimeType,name,path,description,const DeepCollectionEquality().hash(_parameters),const DeepCollectionEquality().hash(_assets),hasAssets,hasParameters,requiresConfig);

@override
String toString() {
  return 'ProtocolDetails(name: $name, path: $path, description: $description, parameters: $parameters, assets: $assets, hasAssets: $hasAssets, hasParameters: $hasParameters, requiresConfig: $requiresConfig)';
}


}

/// @nodoc
abstract mixin class _$ProtocolDetailsCopyWith<$Res> implements $ProtocolDetailsCopyWith<$Res> {
  factory _$ProtocolDetailsCopyWith(_ProtocolDetails value, $Res Function(_ProtocolDetails) _then) = __$ProtocolDetailsCopyWithImpl;
@override @useResult
$Res call({
 String name, String path, String description, Map<String, ParameterConfig> parameters, List<ProtocolAssetDetail> assets, bool hasAssets, bool hasParameters, bool requiresConfig
});




}
/// @nodoc
class __$ProtocolDetailsCopyWithImpl<$Res>
    implements _$ProtocolDetailsCopyWith<$Res> {
  __$ProtocolDetailsCopyWithImpl(this._self, this._then);

  final _ProtocolDetails _self;
  final $Res Function(_ProtocolDetails) _then;

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? path = null,Object? description = null,Object? parameters = null,Object? assets = null,Object? hasAssets = null,Object? hasParameters = null,Object? requiresConfig = null,}) {
  return _then(_ProtocolDetails(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,path: null == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,parameters: null == parameters ? _self._parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>,assets: null == assets ? _self._assets : assets // ignore: cast_nullable_to_non_nullable
as List<ProtocolAssetDetail>,hasAssets: null == hasAssets ? _self.hasAssets : hasAssets // ignore: cast_nullable_to_non_nullable
as bool,hasParameters: null == hasParameters ? _self.hasParameters : hasParameters // ignore: cast_nullable_to_non_nullable
as bool,requiresConfig: null == requiresConfig ? _self.requiresConfig : requiresConfig // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
