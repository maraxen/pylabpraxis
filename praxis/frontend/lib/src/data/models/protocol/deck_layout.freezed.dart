// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'deck_layout.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DeckLayout {

// Unique identifier for this deck layout configuration.
 String? get id;// Human-readable name for the deck layout.
 String? get name;// List of resource items placed on the deck.
 List<DeckItem>? get items;// Optional: schema version for the deck layout definition.
 String? get schemaVersion;// Optional: metadata about the robot or deck type.
 Map<String, dynamic>? get robot;// e.g., { "model": "OT-2", "deckId": "ot2_standard" }
 List<String>? get positions;
/// Create a copy of DeckLayout
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckLayoutCopyWith<DeckLayout> get copyWith => _$DeckLayoutCopyWithImpl<DeckLayout>(this as DeckLayout, _$identity);

  /// Serializes this DeckLayout to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckLayout&&(identical(other.accession_id, id) || other.accession_id == id)&&(identical(other.name, name) || other.name == name)&&const DeepCollectionEquality().equals(other.items, items)&&(identical(other.schemaVersion, schemaVersion) || other.schemaVersion == schemaVersion)&&const DeepCollectionEquality().equals(other.robot, robot)&&const DeepCollectionEquality().equals(other.positions, positions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,const DeepCollectionEquality().hash(items),schemaVersion,const DeepCollectionEquality().hash(robot),const DeepCollectionEquality().hash(positions));

@override
String toString() {
  return 'DeckLayout(id: $id, name: $name, items: $items, schemaVersion: $schemaVersion, robot: $robot, positions: $positions)';
}


}

/// @nodoc
abstract mixin class $DeckLayoutCopyWith<$Res>  {
  factory $DeckLayoutCopyWith(DeckLayout value, $Res Function(DeckLayout) _then) = _$DeckLayoutCopyWithImpl;
@useResult
$Res call({
 String? id, String? name, List<DeckItem>? items, String? schemaVersion, Map<String, dynamic>? robot, List<String>? positions
});




}
/// @nodoc
class _$DeckLayoutCopyWithImpl<$Res>
    implements $DeckLayoutCopyWith<$Res> {
  _$DeckLayoutCopyWithImpl(this._self, this._then);

  final DeckLayout _self;
  final $Res Function(DeckLayout) _then;

/// Create a copy of DeckLayout
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? name = freezed,Object? items = freezed,Object? schemaVersion = freezed,Object? robot = freezed,Object? positions = freezed,}) {
  return _then(_self.copyWith(
id: freezed == id ? _self.accession_id : id // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,items: freezed == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as List<DeckItem>?,schemaVersion: freezed == schemaVersion ? _self.schemaVersion : schemaVersion // ignore: cast_nullable_to_non_nullable
as String?,robot: freezed == robot ? _self.robot : robot // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,positions: freezed == positions ? _self.positions : positions // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _DeckLayout implements DeckLayout {
  const _DeckLayout({this.accession_id, this.name, final  List<DeckItem>? items, this.schemaVersion, final  Map<String, dynamic>? robot, final  List<String>? positions}): _items = items,_robot = robot,_positions = positions;
  factory _DeckLayout.fromJson(Map<String, dynamic> json) => _$DeckLayoutFromJson(json);

// Unique identifier for this deck layout configuration.
@override final  String? id;
// Human-readable name for the deck layout.
@override final  String? name;
// List of resource items placed on the deck.
 final  List<DeckItem>? _items;
// List of resource items placed on the deck.
@override List<DeckItem>? get items {
  final value = _items;
  if (value == null) return null;
  if (_items is EqualUnmodifiableListView) return _items;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Optional: schema version for the deck layout definition.
@override final  String? schemaVersion;
// Optional: metadata about the robot or deck type.
 final  Map<String, dynamic>? _robot;
// Optional: metadata about the robot or deck type.
@override Map<String, dynamic>? get robot {
  final value = _robot;
  if (value == null) return null;
  if (_robot is EqualUnmodifiableMapView) return _robot;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// e.g., { "model": "OT-2", "deckId": "ot2_standard" }
 final  List<String>? _positions;
// e.g., { "model": "OT-2", "deckId": "ot2_standard" }
@override List<String>? get positions {
  final value = _positions;
  if (value == null) return null;
  if (_positions is EqualUnmodifiableListView) return _positions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of DeckLayout
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DeckLayoutCopyWith<_DeckLayout> get copyWith => __$DeckLayoutCopyWithImpl<_DeckLayout>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DeckLayoutToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DeckLayout&&(identical(other.accession_id, id) || other.accession_id == id)&&(identical(other.name, name) || other.name == name)&&const DeepCollectionEquality().equals(other._items, _items)&&(identical(other.schemaVersion, schemaVersion) || other.schemaVersion == schemaVersion)&&const DeepCollectionEquality().equals(other._robot, _robot)&&const DeepCollectionEquality().equals(other._positions, _positions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,const DeepCollectionEquality().hash(_items),schemaVersion,const DeepCollectionEquality().hash(_robot),const DeepCollectionEquality().hash(_positions));

@override
String toString() {
  return 'DeckLayout(id: $id, name: $name, items: $items, schemaVersion: $schemaVersion, robot: $robot, positions: $positions)';
}


}

/// @nodoc
abstract mixin class _$DeckLayoutCopyWith<$Res> implements $DeckLayoutCopyWith<$Res> {
  factory _$DeckLayoutCopyWith(_DeckLayout value, $Res Function(_DeckLayout) _then) = __$DeckLayoutCopyWithImpl;
@override @useResult
$Res call({
 String? id, String? name, List<DeckItem>? items, String? schemaVersion, Map<String, dynamic>? robot, List<String>? positions
});




}
/// @nodoc
class __$DeckLayoutCopyWithImpl<$Res>
    implements _$DeckLayoutCopyWith<$Res> {
  __$DeckLayoutCopyWithImpl(this._self, this._then);

  final _DeckLayout _self;
  final $Res Function(_DeckLayout) _then;

/// Create a copy of DeckLayout
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? name = freezed,Object? items = freezed,Object? schemaVersion = freezed,Object? robot = freezed,Object? positions = freezed,}) {
  return _then(_DeckLayout(
id: freezed == id ? _self.accession_id : id // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,items: freezed == items ? _self._items : items // ignore: cast_nullable_to_non_nullable
as List<DeckItem>?,schemaVersion: freezed == schemaVersion ? _self.schemaVersion : schemaVersion // ignore: cast_nullable_to_non_nullable
as String?,robot: freezed == robot ? _self._robot : robot // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,positions: freezed == positions ? _self._positions : positions // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}


}


/// @nodoc
mixin _$DeckItem {

// Unique ID for this item on the deck.
 String get id;// The slot on the deck where this item is placed (e.g., "1", "A1").
 String get slot;// The ID of the resource definition being used.
@JsonKey(name: 'resource_definition_accession_id') String get resourceDefinitionId;// Optional: A specific resource definition, if not just referencing by ID.
// This could be embedded or fetched separately.
@JsonKey(name: 'resource_definition') ResourceDefinition? get resourceDefinition;// Human-readable display name for this item in this context.
@JsonKey(name: 'display_name') String? get displayName;
/// Create a copy of DeckItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckItemCopyWith<DeckItem> get copyWith => _$DeckItemCopyWithImpl<DeckItem>(this as DeckItem, _$identity);

  /// Serializes this DeckItem to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckItem&&(identical(other.accession_id, id) || other.accession_id == id)&&(identical(other.slot, slot) || other.slot == slot)&&(identical(other.resourceDefinitionId, resourceDefinitionId) || other.resourceDefinitionId == resourceDefinitionId)&&(identical(other.resourceDefinition, resourceDefinition) || other.resourceDefinition == resourceDefinition)&&(identical(other.displayName, displayName) || other.displayName == displayName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slot,resourceDefinitionId,resourceDefinition,displayName);

@override
String toString() {
  return 'DeckItem(id: $id, slot: $slot, resourceDefinitionId: $resourceDefinitionId, resourceDefinition: $resourceDefinition, displayName: $displayName)';
}


}

/// @nodoc
abstract mixin class $DeckItemCopyWith<$Res>  {
  factory $DeckItemCopyWith(DeckItem value, $Res Function(DeckItem) _then) = _$DeckItemCopyWithImpl;
@useResult
$Res call({
 String id, String slot,@JsonKey(name: 'resource_definition_accession_id') String resourceDefinitionId,@JsonKey(name: 'resource_definition') ResourceDefinition? resourceDefinition,@JsonKey(name: 'display_name') String? displayName
});


$ResourceDefinitionCopyWith<$Res>? get resourceDefinition;

}
/// @nodoc
class _$DeckItemCopyWithImpl<$Res>
    implements $DeckItemCopyWith<$Res> {
  _$DeckItemCopyWithImpl(this._self, this._then);

  final DeckItem _self;
  final $Res Function(DeckItem) _then;

/// Create a copy of DeckItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slot = null,Object? resourceDefinitionId = null,Object? resourceDefinition = freezed,Object? displayName = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.accession_id : id // ignore: cast_nullable_to_non_nullable
as String,slot: null == slot ? _self.slot : slot // ignore: cast_nullable_to_non_nullable
as String,resourceDefinitionId: null == resourceDefinitionId ? _self.resourceDefinitionId : resourceDefinitionId // ignore: cast_nullable_to_non_nullable
as String,resourceDefinition: freezed == resourceDefinition ? _self.resourceDefinition : resourceDefinition // ignore: cast_nullable_to_non_nullable
as ResourceDefinition?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of DeckItem
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ResourceDefinitionCopyWith<$Res>? get resourceDefinition {
    if (_self.resourceDefinition == null) {
    return null;
  }

  return $ResourceDefinitionCopyWith<$Res>(_self.resourceDefinition!, (value) {
    return _then(_self.copyWith(resourceDefinition: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _DeckItem implements DeckItem {
  const _DeckItem({required this.accession_id, required this.slot, @JsonKey(name: 'resource_definition_accession_id') required this.resourceDefinitionId, @JsonKey(name: 'resource_definition') this.resourceDefinition, @JsonKey(name: 'display_name') this.displayName});
  factory _DeckItem.fromJson(Map<String, dynamic> json) => _$DeckItemFromJson(json);

// Unique ID for this item on the deck.
@override final  String id;
// The slot on the deck where this item is placed (e.g., "1", "A1").
@override final  String slot;
// The ID of the resource definition being used.
@override@JsonKey(name: 'resource_definition_accession_id') final  String resourceDefinitionId;
// Optional: A specific resource definition, if not just referencing by ID.
// This could be embedded or fetched separately.
@override@JsonKey(name: 'resource_definition') final  ResourceDefinition? resourceDefinition;
// Human-readable display name for this item in this context.
@override@JsonKey(name: 'display_name') final  String? displayName;

/// Create a copy of DeckItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DeckItemCopyWith<_DeckItem> get copyWith => __$DeckItemCopyWithImpl<_DeckItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DeckItemToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DeckItem&&(identical(other.accession_id, id) || other.accession_id == id)&&(identical(other.slot, slot) || other.slot == slot)&&(identical(other.resourceDefinitionId, resourceDefinitionId) || other.resourceDefinitionId == resourceDefinitionId)&&(identical(other.resourceDefinition, resourceDefinition) || other.resourceDefinition == resourceDefinition)&&(identical(other.displayName, displayName) || other.displayName == displayName));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slot,resourceDefinitionId,resourceDefinition,displayName);

@override
String toString() {
  return 'DeckItem(id: $id, slot: $slot, resourceDefinitionId: $resourceDefinitionId, resourceDefinition: $resourceDefinition, displayName: $displayName)';
}


}

/// @nodoc
abstract mixin class _$DeckItemCopyWith<$Res> implements $DeckItemCopyWith<$Res> {
  factory _$DeckItemCopyWith(_DeckItem value, $Res Function(_DeckItem) _then) = __$DeckItemCopyWithImpl;
@override @useResult
$Res call({
 String id, String slot,@JsonKey(name: 'resource_definition_accession_id') String resourceDefinitionId,@JsonKey(name: 'resource_definition') ResourceDefinition? resourceDefinition,@JsonKey(name: 'display_name') String? displayName
});


@override $ResourceDefinitionCopyWith<$Res>? get resourceDefinition;

}
/// @nodoc
class __$DeckItemCopyWithImpl<$Res>
    implements _$DeckItemCopyWith<$Res> {
  __$DeckItemCopyWithImpl(this._self, this._then);

  final _DeckItem _self;
  final $Res Function(_DeckItem) _then;

/// Create a copy of DeckItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slot = null,Object? resourceDefinitionId = null,Object? resourceDefinition = freezed,Object? displayName = freezed,}) {
  return _then(_DeckItem(
id: null == id ? _self.accession_id : id // ignore: cast_nullable_to_non_nullable
as String,slot: null == slot ? _self.slot : slot // ignore: cast_nullable_to_non_nullable
as String,resourceDefinitionId: null == resourceDefinitionId ? _self.resourceDefinitionId : resourceDefinitionId // ignore: cast_nullable_to_non_nullable
as String,resourceDefinition: freezed == resourceDefinition ? _self.resourceDefinition : resourceDefinition // ignore: cast_nullable_to_non_nullable
as ResourceDefinition?,displayName: freezed == displayName ? _self.displayName : displayName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of DeckItem
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ResourceDefinitionCopyWith<$Res>? get resourceDefinition {
    if (_self.resourceDefinition == null) {
    return null;
  }

  return $ResourceDefinitionCopyWith<$Res>(_self.resourceDefinition!, (value) {
    return _then(_self.copyWith(resourceDefinition: value));
  });
}
}

// dart format on
