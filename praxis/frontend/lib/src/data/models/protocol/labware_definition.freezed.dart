// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'labware_definition.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LabwareDefinition {

// Unique identifier for the labware definition (e.g., 'opentrons_96_tiprack_300ul').
 String get id;// Human-readable display name.
@JsonKey(name: 'display_name') String? get displayName;// Version of the labware definition.
 int? get version;// Namespace of the labware (e.g., 'opentrons').
 String? get namespace;// Category of labware (e.g., 'tipRack', 'wellPlate', 'reservoir').
 String? get category;// Dimensions of the labware.
 Map<String, double>? get dimensions;// e.g., { "xDimension": 127.76, "yDimension": 85.48, "zDimension": 14.7 }
// Well definitions (if applicable).
 Map<String, WellDefinition>? get wells;// Keyed by well name e.g., "A1"
// Ordering of wells (e.g., column-wise or row-wise).
 List<List<String>>? get ordering;// Generic metadata.
 Map<String, dynamic>? get metadata;// Brand of the labware.
 String? get brand;// Specific model or part number.
 String? get model;
/// Create a copy of LabwareDefinition
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LabwareDefinitionCopyWith<LabwareDefinition> get copyWith => _$LabwareDefinitionCopyWithImpl<LabwareDefinition>(this as LabwareDefinition, _$identity);

  /// Serializes this LabwareDefinition to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LabwareDefinition&&(identical(other.id, id) || other.id == id)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.version, version) || other.version == version)&&(identical(other.namespace, namespace) || other.namespace == namespace)&&(identical(other.category, category) || other.category == category)&&const DeepCollectionEquality().equals(other.dimensions, dimensions)&&const DeepCollectionEquality().equals(other.wells, wells)&&const DeepCollectionEquality().equals(other.ordering, ordering)&&const DeepCollectionEquality().equals(other.metadata, metadata)&&(identical(other.brand, brand) || other.brand == brand)&&(identical(other.model, model) || other.model == model));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,displayName,version,namespace,category,const DeepCollectionEquality().hash(dimensions),const DeepCollectionEquality().hash(wells),const DeepCollectionEquality().hash(ordering),const DeepCollectionEquality().hash(metadata),brand,model);

@override
String toString() {
  return 'LabwareDefinition(id: $id, displayName: $displayName, version: $version, namespace: $namespace, category: $category, dimensions: $dimensions, wells: $wells, ordering: $ordering, metadata: $metadata, brand: $brand, model: $model)';
}


}

/// @nodoc
abstract mixin class $LabwareDefinitionCopyWith<$Res>  {
  factory $LabwareDefinitionCopyWith(LabwareDefinition value, $Res Function(LabwareDefinition) _then) = _$LabwareDefinitionCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'display_name') String? displayName, int? version, String? namespace, String? category, Map<String, double>? dimensions, Map<String, WellDefinition>? wells, List<List<String>>? ordering, Map<String, dynamic>? metadata, String? brand, String? model
});




}
/// @nodoc
class _$LabwareDefinitionCopyWithImpl<$Res>
    implements $LabwareDefinitionCopyWith<$Res> {
  _$LabwareDefinitionCopyWithImpl(this._self, this._then);

  final LabwareDefinition _self;
  final $Res Function(LabwareDefinition) _then;

/// Create a copy of LabwareDefinition
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? displayName = freezed,Object? version = freezed,Object? namespace = freezed,Object? category = freezed,Object? dimensions = freezed,Object? wells = freezed,Object? ordering = freezed,Object? metadata = freezed,Object? brand = freezed,Object? model = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,version: freezed == version ? _self.version : version // ignore: cast_nullable_to_non_nullable
as int?,namespace: freezed == namespace ? _self.namespace : namespace // ignore: cast_nullable_to_non_nullable
as String?,category: freezed == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String?,dimensions: freezed == dimensions ? _self.dimensions : dimensions // ignore: cast_nullable_to_non_nullable
as Map<String, double>?,wells: freezed == wells ? _self.wells : wells // ignore: cast_nullable_to_non_nullable
as Map<String, WellDefinition>?,ordering: freezed == ordering ? _self.ordering : ordering // ignore: cast_nullable_to_non_nullable
as List<List<String>>?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,brand: freezed == brand ? _self.brand : brand // ignore: cast_nullable_to_non_nullable
as String?,model: freezed == model ? _self.model : model // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _LabwareDefinition implements LabwareDefinition {
  const _LabwareDefinition({required this.id, @JsonKey(name: 'display_name') this.displayName, this.version, this.namespace, this.category, final  Map<String, double>? dimensions, final  Map<String, WellDefinition>? wells, final  List<List<String>>? ordering, final  Map<String, dynamic>? metadata, this.brand, this.model}): _dimensions = dimensions,_wells = wells,_ordering = ordering,_metadata = metadata;
  factory _LabwareDefinition.fromJson(Map<String, dynamic> json) => _$LabwareDefinitionFromJson(json);

// Unique identifier for the labware definition (e.g., 'opentrons_96_tiprack_300ul').
@override final  String id;
// Human-readable display name.
@override@JsonKey(name: 'display_name') final  String? displayName;
// Version of the labware definition.
@override final  int? version;
// Namespace of the labware (e.g., 'opentrons').
@override final  String? namespace;
// Category of labware (e.g., 'tipRack', 'wellPlate', 'reservoir').
@override final  String? category;
// Dimensions of the labware.
 final  Map<String, double>? _dimensions;
// Dimensions of the labware.
@override Map<String, double>? get dimensions {
  final value = _dimensions;
  if (value == null) return null;
  if (_dimensions is EqualUnmodifiableMapView) return _dimensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// e.g., { "xDimension": 127.76, "yDimension": 85.48, "zDimension": 14.7 }
// Well definitions (if applicable).
 final  Map<String, WellDefinition>? _wells;
// e.g., { "xDimension": 127.76, "yDimension": 85.48, "zDimension": 14.7 }
// Well definitions (if applicable).
@override Map<String, WellDefinition>? get wells {
  final value = _wells;
  if (value == null) return null;
  if (_wells is EqualUnmodifiableMapView) return _wells;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Keyed by well name e.g., "A1"
// Ordering of wells (e.g., column-wise or row-wise).
 final  List<List<String>>? _ordering;
// Keyed by well name e.g., "A1"
// Ordering of wells (e.g., column-wise or row-wise).
@override List<List<String>>? get ordering {
  final value = _ordering;
  if (value == null) return null;
  if (_ordering is EqualUnmodifiableListView) return _ordering;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Generic metadata.
 final  Map<String, dynamic>? _metadata;
// Generic metadata.
@override Map<String, dynamic>? get metadata {
  final value = _metadata;
  if (value == null) return null;
  if (_metadata is EqualUnmodifiableMapView) return _metadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Brand of the labware.
@override final  String? brand;
// Specific model or part number.
@override final  String? model;

/// Create a copy of LabwareDefinition
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LabwareDefinitionCopyWith<_LabwareDefinition> get copyWith => __$LabwareDefinitionCopyWithImpl<_LabwareDefinition>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LabwareDefinitionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LabwareDefinition&&(identical(other.id, id) || other.id == id)&&(identical(other.displayName, displayName) || other.displayName == displayName)&&(identical(other.version, version) || other.version == version)&&(identical(other.namespace, namespace) || other.namespace == namespace)&&(identical(other.category, category) || other.category == category)&&const DeepCollectionEquality().equals(other._dimensions, _dimensions)&&const DeepCollectionEquality().equals(other._wells, _wells)&&const DeepCollectionEquality().equals(other._ordering, _ordering)&&const DeepCollectionEquality().equals(other._metadata, _metadata)&&(identical(other.brand, brand) || other.brand == brand)&&(identical(other.model, model) || other.model == model));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,displayName,version,namespace,category,const DeepCollectionEquality().hash(_dimensions),const DeepCollectionEquality().hash(_wells),const DeepCollectionEquality().hash(_ordering),const DeepCollectionEquality().hash(_metadata),brand,model);

@override
String toString() {
  return 'LabwareDefinition(id: $id, displayName: $displayName, version: $version, namespace: $namespace, category: $category, dimensions: $dimensions, wells: $wells, ordering: $ordering, metadata: $metadata, brand: $brand, model: $model)';
}


}

/// @nodoc
abstract mixin class _$LabwareDefinitionCopyWith<$Res> implements $LabwareDefinitionCopyWith<$Res> {
  factory _$LabwareDefinitionCopyWith(_LabwareDefinition value, $Res Function(_LabwareDefinition) _then) = __$LabwareDefinitionCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'display_name') String? displayName, int? version, String? namespace, String? category, Map<String, double>? dimensions, Map<String, WellDefinition>? wells, List<List<String>>? ordering, Map<String, dynamic>? metadata, String? brand, String? model
});




}
/// @nodoc
class __$LabwareDefinitionCopyWithImpl<$Res>
    implements _$LabwareDefinitionCopyWith<$Res> {
  __$LabwareDefinitionCopyWithImpl(this._self, this._then);

  final _LabwareDefinition _self;
  final $Res Function(_LabwareDefinition) _then;

/// Create a copy of LabwareDefinition
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? displayName = freezed,Object? version = freezed,Object? namespace = freezed,Object? category = freezed,Object? dimensions = freezed,Object? wells = freezed,Object? ordering = freezed,Object? metadata = freezed,Object? brand = freezed,Object? model = freezed,}) {
  return _then(_LabwareDefinition(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,version: freezed == version ? _self.version : version // ignore: cast_nullable_to_non_nullable
as int?,namespace: freezed == namespace ? _self.namespace : namespace // ignore: cast_nullable_to_non_nullable
as String?,category: freezed == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String?,dimensions: freezed == dimensions ? _self._dimensions : dimensions // ignore: cast_nullable_to_non_nullable
as Map<String, double>?,wells: freezed == wells ? _self._wells : wells // ignore: cast_nullable_to_non_nullable
as Map<String, WellDefinition>?,ordering: freezed == ordering ? _self._ordering : ordering // ignore: cast_nullable_to_non_nullable
as List<List<String>>?,metadata: freezed == metadata ? _self._metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,brand: freezed == brand ? _self.brand : brand // ignore: cast_nullable_to_non_nullable
as String?,model: freezed == model ? _self.model : model // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$WellDefinition {

// Depth of the well in mm.
 double? get depth;// Total liquid volume of the well in µL.
 double? get totalLiquidVolume;// Shape of the well (e.g., 'circular', 'rectangular').
 String? get shape;// Diameter of the well in mm (if circular).
 double? get diameter;// X dimension of the well in mm (if rectangular).
 double? get xDimension;// Y dimension of the well in mm (if rectangular).
 double? get yDimension;// X-coordinate of the well's center relative to the labware origin.
 double get x;// Y-coordinate of the well's center relative to the labware origin.
 double get y;// Z-coordinate of the well's bottom relative to the labware origin.
 double? get z;
/// Create a copy of WellDefinition
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WellDefinitionCopyWith<WellDefinition> get copyWith => _$WellDefinitionCopyWithImpl<WellDefinition>(this as WellDefinition, _$identity);

  /// Serializes this WellDefinition to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WellDefinition&&(identical(other.depth, depth) || other.depth == depth)&&(identical(other.totalLiquidVolume, totalLiquidVolume) || other.totalLiquidVolume == totalLiquidVolume)&&(identical(other.shape, shape) || other.shape == shape)&&(identical(other.diameter, diameter) || other.diameter == diameter)&&(identical(other.xDimension, xDimension) || other.xDimension == xDimension)&&(identical(other.yDimension, yDimension) || other.yDimension == yDimension)&&(identical(other.x, x) || other.x == x)&&(identical(other.y, y) || other.y == y)&&(identical(other.z, z) || other.z == z));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,depth,totalLiquidVolume,shape,diameter,xDimension,yDimension,x,y,z);

@override
String toString() {
  return 'WellDefinition(depth: $depth, totalLiquidVolume: $totalLiquidVolume, shape: $shape, diameter: $diameter, xDimension: $xDimension, yDimension: $yDimension, x: $x, y: $y, z: $z)';
}


}

/// @nodoc
abstract mixin class $WellDefinitionCopyWith<$Res>  {
  factory $WellDefinitionCopyWith(WellDefinition value, $Res Function(WellDefinition) _then) = _$WellDefinitionCopyWithImpl;
@useResult
$Res call({
 double? depth, double? totalLiquidVolume, String? shape, double? diameter, double? xDimension, double? yDimension, double x, double y, double? z
});




}
/// @nodoc
class _$WellDefinitionCopyWithImpl<$Res>
    implements $WellDefinitionCopyWith<$Res> {
  _$WellDefinitionCopyWithImpl(this._self, this._then);

  final WellDefinition _self;
  final $Res Function(WellDefinition) _then;

/// Create a copy of WellDefinition
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? depth = freezed,Object? totalLiquidVolume = freezed,Object? shape = freezed,Object? diameter = freezed,Object? xDimension = freezed,Object? yDimension = freezed,Object? x = null,Object? y = null,Object? z = freezed,}) {
  return _then(_self.copyWith(
depth: freezed == depth ? _self.depth : depth // ignore: cast_nullable_to_non_nullable
as double?,totalLiquidVolume: freezed == totalLiquidVolume ? _self.totalLiquidVolume : totalLiquidVolume // ignore: cast_nullable_to_non_nullable
as double?,shape: freezed == shape ? _self.shape : shape // ignore: cast_nullable_to_non_nullable
as String?,diameter: freezed == diameter ? _self.diameter : diameter // ignore: cast_nullable_to_non_nullable
as double?,xDimension: freezed == xDimension ? _self.xDimension : xDimension // ignore: cast_nullable_to_non_nullable
as double?,yDimension: freezed == yDimension ? _self.yDimension : yDimension // ignore: cast_nullable_to_non_nullable
as double?,x: null == x ? _self.x : x // ignore: cast_nullable_to_non_nullable
as double,y: null == y ? _self.y : y // ignore: cast_nullable_to_non_nullable
as double,z: freezed == z ? _self.z : z // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _WellDefinition implements WellDefinition {
  const _WellDefinition({this.depth, this.totalLiquidVolume, this.shape, this.diameter, this.xDimension, this.yDimension, required this.x, required this.y, this.z});
  factory _WellDefinition.fromJson(Map<String, dynamic> json) => _$WellDefinitionFromJson(json);

// Depth of the well in mm.
@override final  double? depth;
// Total liquid volume of the well in µL.
@override final  double? totalLiquidVolume;
// Shape of the well (e.g., 'circular', 'rectangular').
@override final  String? shape;
// Diameter of the well in mm (if circular).
@override final  double? diameter;
// X dimension of the well in mm (if rectangular).
@override final  double? xDimension;
// Y dimension of the well in mm (if rectangular).
@override final  double? yDimension;
// X-coordinate of the well's center relative to the labware origin.
@override final  double x;
// Y-coordinate of the well's center relative to the labware origin.
@override final  double y;
// Z-coordinate of the well's bottom relative to the labware origin.
@override final  double? z;

/// Create a copy of WellDefinition
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WellDefinitionCopyWith<_WellDefinition> get copyWith => __$WellDefinitionCopyWithImpl<_WellDefinition>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WellDefinitionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WellDefinition&&(identical(other.depth, depth) || other.depth == depth)&&(identical(other.totalLiquidVolume, totalLiquidVolume) || other.totalLiquidVolume == totalLiquidVolume)&&(identical(other.shape, shape) || other.shape == shape)&&(identical(other.diameter, diameter) || other.diameter == diameter)&&(identical(other.xDimension, xDimension) || other.xDimension == xDimension)&&(identical(other.yDimension, yDimension) || other.yDimension == yDimension)&&(identical(other.x, x) || other.x == x)&&(identical(other.y, y) || other.y == y)&&(identical(other.z, z) || other.z == z));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,depth,totalLiquidVolume,shape,diameter,xDimension,yDimension,x,y,z);

@override
String toString() {
  return 'WellDefinition(depth: $depth, totalLiquidVolume: $totalLiquidVolume, shape: $shape, diameter: $diameter, xDimension: $xDimension, yDimension: $yDimension, x: $x, y: $y, z: $z)';
}


}

/// @nodoc
abstract mixin class _$WellDefinitionCopyWith<$Res> implements $WellDefinitionCopyWith<$Res> {
  factory _$WellDefinitionCopyWith(_WellDefinition value, $Res Function(_WellDefinition) _then) = __$WellDefinitionCopyWithImpl;
@override @useResult
$Res call({
 double? depth, double? totalLiquidVolume, String? shape, double? diameter, double? xDimension, double? yDimension, double x, double y, double? z
});




}
/// @nodoc
class __$WellDefinitionCopyWithImpl<$Res>
    implements _$WellDefinitionCopyWith<$Res> {
  __$WellDefinitionCopyWithImpl(this._self, this._then);

  final _WellDefinition _self;
  final $Res Function(_WellDefinition) _then;

/// Create a copy of WellDefinition
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? depth = freezed,Object? totalLiquidVolume = freezed,Object? shape = freezed,Object? diameter = freezed,Object? xDimension = freezed,Object? yDimension = freezed,Object? x = null,Object? y = null,Object? z = freezed,}) {
  return _then(_WellDefinition(
depth: freezed == depth ? _self.depth : depth // ignore: cast_nullable_to_non_nullable
as double?,totalLiquidVolume: freezed == totalLiquidVolume ? _self.totalLiquidVolume : totalLiquidVolume // ignore: cast_nullable_to_non_nullable
as double?,shape: freezed == shape ? _self.shape : shape // ignore: cast_nullable_to_non_nullable
as String?,diameter: freezed == diameter ? _self.diameter : diameter // ignore: cast_nullable_to_non_nullable
as double?,xDimension: freezed == xDimension ? _self.xDimension : xDimension // ignore: cast_nullable_to_non_nullable
as double?,yDimension: freezed == yDimension ? _self.yDimension : yDimension // ignore: cast_nullable_to_non_nullable
as double?,x: null == x ? _self.x : x // ignore: cast_nullable_to_non_nullable
as double,y: null == y ? _self.y : y // ignore: cast_nullable_to_non_nullable
as double,z: freezed == z ? _self.z : z // ignore: cast_nullable_to_non_nullable
as double?,
  ));
}


}

// dart format on
