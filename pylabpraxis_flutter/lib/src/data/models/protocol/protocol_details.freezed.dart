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

// Basic information about the protocol, can be embedded or referenced.
// Embedding ProtocolInfo directly using a spread operator in Freezed
// is not directly supported for the constructor.
// Instead, we list its fields or have a dedicated 'info' field.
// For simplicity and direct mapping, let's include ProtocolInfo fields,
// or have an 'info' field of type ProtocolInfo.
// Option 1: Dedicated 'info' field
 ProtocolInfo get info;// Option 2: Flattened fields (if you prefer direct access, but less clean)
// required String name,
// required String path,
// required String description,
// String? version,
// @JsonKey(name: 'last_modified') DateTime? lastModified,
// List<String>? tags,
// ... other fields from ProtocolInfo
// Parameters required by the protocol.
 Map<String, ParameterConfig> get parameters;// We don't add parameterGroups directly as it will be derived
// Assets (labware, reagents, etc.) required or used by the protocol.
 List<ProtocolAsset>? get assets;// Steps involved in executing the protocol.
 List<ProtocolStep>? get steps;// Hardware requirements or configurations.
 List<ProtocolHardware>? get hardware;// Deck layout configuration for the protocol.
// This might be optional or could be a specific structure.
 DeckLayout? get deckLayout;// Assuming you have a DeckLayout model
// Schema version for the protocol definition itself.
 String? get schemaVersion;// Any other global metadata specific to the protocol's execution or definition.
 Map<String, dynamic>? get metadata;// Entry points or commands that can be run (e.g. "run", "calibrate")
// The key could be the command name, value could be details or entry step ID.
 Map<String, dynamic>? get commands;// Authorship and contact information.
 String? get author;// Redundant if in ProtocolInfo, but sometimes present
 String? get email;// Organization or lab associated with the protocol.
 String? get organization;// Publication or reference links.
 List<String>? get publications;// Changelog or version history notes.
 String? get changelog;
/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolDetailsCopyWith<ProtocolDetails> get copyWith => _$ProtocolDetailsCopyWithImpl<ProtocolDetails>(this as ProtocolDetails, _$identity);

  /// Serializes this ProtocolDetails to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolDetails&&(identical(other.info, info) || other.info == info)&&const DeepCollectionEquality().equals(other.parameters, parameters)&&const DeepCollectionEquality().equals(other.assets, assets)&&const DeepCollectionEquality().equals(other.steps, steps)&&const DeepCollectionEquality().equals(other.hardware, hardware)&&(identical(other.deckLayout, deckLayout) || other.deckLayout == deckLayout)&&(identical(other.schemaVersion, schemaVersion) || other.schemaVersion == schemaVersion)&&const DeepCollectionEquality().equals(other.metadata, metadata)&&const DeepCollectionEquality().equals(other.commands, commands)&&(identical(other.author, author) || other.author == author)&&(identical(other.email, email) || other.email == email)&&(identical(other.organization, organization) || other.organization == organization)&&const DeepCollectionEquality().equals(other.publications, publications)&&(identical(other.changelog, changelog) || other.changelog == changelog));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,info,const DeepCollectionEquality().hash(parameters),const DeepCollectionEquality().hash(assets),const DeepCollectionEquality().hash(steps),const DeepCollectionEquality().hash(hardware),deckLayout,schemaVersion,const DeepCollectionEquality().hash(metadata),const DeepCollectionEquality().hash(commands),author,email,organization,const DeepCollectionEquality().hash(publications),changelog);

@override
String toString() {
  return 'ProtocolDetails(info: $info, parameters: $parameters, assets: $assets, steps: $steps, hardware: $hardware, deckLayout: $deckLayout, schemaVersion: $schemaVersion, metadata: $metadata, commands: $commands, author: $author, email: $email, organization: $organization, publications: $publications, changelog: $changelog)';
}


}

/// @nodoc
abstract mixin class $ProtocolDetailsCopyWith<$Res>  {
  factory $ProtocolDetailsCopyWith(ProtocolDetails value, $Res Function(ProtocolDetails) _then) = _$ProtocolDetailsCopyWithImpl;
@useResult
$Res call({
 ProtocolInfo info, Map<String, ParameterConfig> parameters, List<ProtocolAsset>? assets, List<ProtocolStep>? steps, List<ProtocolHardware>? hardware, DeckLayout? deckLayout, String? schemaVersion, Map<String, dynamic>? metadata, Map<String, dynamic>? commands, String? author, String? email, String? organization, List<String>? publications, String? changelog
});


$ProtocolInfoCopyWith<$Res> get info;$DeckLayoutCopyWith<$Res>? get deckLayout;

}
/// @nodoc
class _$ProtocolDetailsCopyWithImpl<$Res>
    implements $ProtocolDetailsCopyWith<$Res> {
  _$ProtocolDetailsCopyWithImpl(this._self, this._then);

  final ProtocolDetails _self;
  final $Res Function(ProtocolDetails) _then;

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? info = null,Object? parameters = null,Object? assets = freezed,Object? steps = freezed,Object? hardware = freezed,Object? deckLayout = freezed,Object? schemaVersion = freezed,Object? metadata = freezed,Object? commands = freezed,Object? author = freezed,Object? email = freezed,Object? organization = freezed,Object? publications = freezed,Object? changelog = freezed,}) {
  return _then(_self.copyWith(
info: null == info ? _self.info : info // ignore: cast_nullable_to_non_nullable
as ProtocolInfo,parameters: null == parameters ? _self.parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>,assets: freezed == assets ? _self.assets : assets // ignore: cast_nullable_to_non_nullable
as List<ProtocolAsset>?,steps: freezed == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<ProtocolStep>?,hardware: freezed == hardware ? _self.hardware : hardware // ignore: cast_nullable_to_non_nullable
as List<ProtocolHardware>?,deckLayout: freezed == deckLayout ? _self.deckLayout : deckLayout // ignore: cast_nullable_to_non_nullable
as DeckLayout?,schemaVersion: freezed == schemaVersion ? _self.schemaVersion : schemaVersion // ignore: cast_nullable_to_non_nullable
as String?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,commands: freezed == commands ? _self.commands : commands // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,author: freezed == author ? _self.author : author // ignore: cast_nullable_to_non_nullable
as String?,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,organization: freezed == organization ? _self.organization : organization // ignore: cast_nullable_to_non_nullable
as String?,publications: freezed == publications ? _self.publications : publications // ignore: cast_nullable_to_non_nullable
as List<String>?,changelog: freezed == changelog ? _self.changelog : changelog // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res> get info {
  
  return $ProtocolInfoCopyWith<$Res>(_self.info, (value) {
    return _then(_self.copyWith(info: value));
  });
}/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DeckLayoutCopyWith<$Res>? get deckLayout {
    if (_self.deckLayout == null) {
    return null;
  }

  return $DeckLayoutCopyWith<$Res>(_self.deckLayout!, (value) {
    return _then(_self.copyWith(deckLayout: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ProtocolDetails extends ProtocolDetails {
  const _ProtocolDetails({required this.info, required final  Map<String, ParameterConfig> parameters, final  List<ProtocolAsset>? assets, final  List<ProtocolStep>? steps, final  List<ProtocolHardware>? hardware, this.deckLayout, this.schemaVersion, final  Map<String, dynamic>? metadata, final  Map<String, dynamic>? commands, this.author, this.email, this.organization, final  List<String>? publications, this.changelog}): _parameters = parameters,_assets = assets,_steps = steps,_hardware = hardware,_metadata = metadata,_commands = commands,_publications = publications,super._();
  factory _ProtocolDetails.fromJson(Map<String, dynamic> json) => _$ProtocolDetailsFromJson(json);

// Basic information about the protocol, can be embedded or referenced.
// Embedding ProtocolInfo directly using a spread operator in Freezed
// is not directly supported for the constructor.
// Instead, we list its fields or have a dedicated 'info' field.
// For simplicity and direct mapping, let's include ProtocolInfo fields,
// or have an 'info' field of type ProtocolInfo.
// Option 1: Dedicated 'info' field
@override final  ProtocolInfo info;
// Option 2: Flattened fields (if you prefer direct access, but less clean)
// required String name,
// required String path,
// required String description,
// String? version,
// @JsonKey(name: 'last_modified') DateTime? lastModified,
// List<String>? tags,
// ... other fields from ProtocolInfo
// Parameters required by the protocol.
 final  Map<String, ParameterConfig> _parameters;
// Option 2: Flattened fields (if you prefer direct access, but less clean)
// required String name,
// required String path,
// required String description,
// String? version,
// @JsonKey(name: 'last_modified') DateTime? lastModified,
// List<String>? tags,
// ... other fields from ProtocolInfo
// Parameters required by the protocol.
@override Map<String, ParameterConfig> get parameters {
  if (_parameters is EqualUnmodifiableMapView) return _parameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_parameters);
}

// We don't add parameterGroups directly as it will be derived
// Assets (labware, reagents, etc.) required or used by the protocol.
 final  List<ProtocolAsset>? _assets;
// We don't add parameterGroups directly as it will be derived
// Assets (labware, reagents, etc.) required or used by the protocol.
@override List<ProtocolAsset>? get assets {
  final value = _assets;
  if (value == null) return null;
  if (_assets is EqualUnmodifiableListView) return _assets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Steps involved in executing the protocol.
 final  List<ProtocolStep>? _steps;
// Steps involved in executing the protocol.
@override List<ProtocolStep>? get steps {
  final value = _steps;
  if (value == null) return null;
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Hardware requirements or configurations.
 final  List<ProtocolHardware>? _hardware;
// Hardware requirements or configurations.
@override List<ProtocolHardware>? get hardware {
  final value = _hardware;
  if (value == null) return null;
  if (_hardware is EqualUnmodifiableListView) return _hardware;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Deck layout configuration for the protocol.
// This might be optional or could be a specific structure.
@override final  DeckLayout? deckLayout;
// Assuming you have a DeckLayout model
// Schema version for the protocol definition itself.
@override final  String? schemaVersion;
// Any other global metadata specific to the protocol's execution or definition.
 final  Map<String, dynamic>? _metadata;
// Any other global metadata specific to the protocol's execution or definition.
@override Map<String, dynamic>? get metadata {
  final value = _metadata;
  if (value == null) return null;
  if (_metadata is EqualUnmodifiableMapView) return _metadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Entry points or commands that can be run (e.g. "run", "calibrate")
// The key could be the command name, value could be details or entry step ID.
 final  Map<String, dynamic>? _commands;
// Entry points or commands that can be run (e.g. "run", "calibrate")
// The key could be the command name, value could be details or entry step ID.
@override Map<String, dynamic>? get commands {
  final value = _commands;
  if (value == null) return null;
  if (_commands is EqualUnmodifiableMapView) return _commands;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// Authorship and contact information.
@override final  String? author;
// Redundant if in ProtocolInfo, but sometimes present
@override final  String? email;
// Organization or lab associated with the protocol.
@override final  String? organization;
// Publication or reference links.
 final  List<String>? _publications;
// Publication or reference links.
@override List<String>? get publications {
  final value = _publications;
  if (value == null) return null;
  if (_publications is EqualUnmodifiableListView) return _publications;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Changelog or version history notes.
@override final  String? changelog;

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolDetailsCopyWith<_ProtocolDetails> get copyWith => __$ProtocolDetailsCopyWithImpl<_ProtocolDetails>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolDetailsToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolDetails&&(identical(other.info, info) || other.info == info)&&const DeepCollectionEquality().equals(other._parameters, _parameters)&&const DeepCollectionEquality().equals(other._assets, _assets)&&const DeepCollectionEquality().equals(other._steps, _steps)&&const DeepCollectionEquality().equals(other._hardware, _hardware)&&(identical(other.deckLayout, deckLayout) || other.deckLayout == deckLayout)&&(identical(other.schemaVersion, schemaVersion) || other.schemaVersion == schemaVersion)&&const DeepCollectionEquality().equals(other._metadata, _metadata)&&const DeepCollectionEquality().equals(other._commands, _commands)&&(identical(other.author, author) || other.author == author)&&(identical(other.email, email) || other.email == email)&&(identical(other.organization, organization) || other.organization == organization)&&const DeepCollectionEquality().equals(other._publications, _publications)&&(identical(other.changelog, changelog) || other.changelog == changelog));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,info,const DeepCollectionEquality().hash(_parameters),const DeepCollectionEquality().hash(_assets),const DeepCollectionEquality().hash(_steps),const DeepCollectionEquality().hash(_hardware),deckLayout,schemaVersion,const DeepCollectionEquality().hash(_metadata),const DeepCollectionEquality().hash(_commands),author,email,organization,const DeepCollectionEquality().hash(_publications),changelog);

@override
String toString() {
  return 'ProtocolDetails(info: $info, parameters: $parameters, assets: $assets, steps: $steps, hardware: $hardware, deckLayout: $deckLayout, schemaVersion: $schemaVersion, metadata: $metadata, commands: $commands, author: $author, email: $email, organization: $organization, publications: $publications, changelog: $changelog)';
}


}

/// @nodoc
abstract mixin class _$ProtocolDetailsCopyWith<$Res> implements $ProtocolDetailsCopyWith<$Res> {
  factory _$ProtocolDetailsCopyWith(_ProtocolDetails value, $Res Function(_ProtocolDetails) _then) = __$ProtocolDetailsCopyWithImpl;
@override @useResult
$Res call({
 ProtocolInfo info, Map<String, ParameterConfig> parameters, List<ProtocolAsset>? assets, List<ProtocolStep>? steps, List<ProtocolHardware>? hardware, DeckLayout? deckLayout, String? schemaVersion, Map<String, dynamic>? metadata, Map<String, dynamic>? commands, String? author, String? email, String? organization, List<String>? publications, String? changelog
});


@override $ProtocolInfoCopyWith<$Res> get info;@override $DeckLayoutCopyWith<$Res>? get deckLayout;

}
/// @nodoc
class __$ProtocolDetailsCopyWithImpl<$Res>
    implements _$ProtocolDetailsCopyWith<$Res> {
  __$ProtocolDetailsCopyWithImpl(this._self, this._then);

  final _ProtocolDetails _self;
  final $Res Function(_ProtocolDetails) _then;

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? info = null,Object? parameters = null,Object? assets = freezed,Object? steps = freezed,Object? hardware = freezed,Object? deckLayout = freezed,Object? schemaVersion = freezed,Object? metadata = freezed,Object? commands = freezed,Object? author = freezed,Object? email = freezed,Object? organization = freezed,Object? publications = freezed,Object? changelog = freezed,}) {
  return _then(_ProtocolDetails(
info: null == info ? _self.info : info // ignore: cast_nullable_to_non_nullable
as ProtocolInfo,parameters: null == parameters ? _self._parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, ParameterConfig>,assets: freezed == assets ? _self._assets : assets // ignore: cast_nullable_to_non_nullable
as List<ProtocolAsset>?,steps: freezed == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<ProtocolStep>?,hardware: freezed == hardware ? _self._hardware : hardware // ignore: cast_nullable_to_non_nullable
as List<ProtocolHardware>?,deckLayout: freezed == deckLayout ? _self.deckLayout : deckLayout // ignore: cast_nullable_to_non_nullable
as DeckLayout?,schemaVersion: freezed == schemaVersion ? _self.schemaVersion : schemaVersion // ignore: cast_nullable_to_non_nullable
as String?,metadata: freezed == metadata ? _self._metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,commands: freezed == commands ? _self._commands : commands // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,author: freezed == author ? _self.author : author // ignore: cast_nullable_to_non_nullable
as String?,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,organization: freezed == organization ? _self.organization : organization // ignore: cast_nullable_to_non_nullable
as String?,publications: freezed == publications ? _self._publications : publications // ignore: cast_nullable_to_non_nullable
as List<String>?,changelog: freezed == changelog ? _self.changelog : changelog // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res> get info {
  
  return $ProtocolInfoCopyWith<$Res>(_self.info, (value) {
    return _then(_self.copyWith(info: value));
  });
}/// Create a copy of ProtocolDetails
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$DeckLayoutCopyWith<$Res>? get deckLayout {
    if (_self.deckLayout == null) {
    return null;
  }

  return $DeckLayoutCopyWith<$Res>(_self.deckLayout!, (value) {
    return _then(_self.copyWith(deckLayout: value));
  });
}
}

// dart format on
