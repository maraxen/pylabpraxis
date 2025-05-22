// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_info.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ProtocolInfo {

// Mandatory fields
 String get name; String get path; String get description;// Optional fields from TypeScript model
 String? get version;@JsonKey(name: 'last_modified') DateTime? get lastModified; List<String>? get tags; String? get author; String? get license;@JsonKey(name: 'created_date') DateTime? get createdDate; String? get category; Map<String, dynamic>? get metadata;@JsonKey(name: 'is_favorite') bool? get isFavorite;@JsonKey(name: 'run_count') int? get runCount;@JsonKey(name: 'average_rating') double? get averageRating;@JsonKey(name: 'estimated_duration') String? get estimatedDuration;// Could be parsed into Duration later
 ProtocolComplexity? get complexity;@JsonKey(name: 'icon_url') String? get iconUrl;
/// Create a copy of ProtocolInfo
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<ProtocolInfo> get copyWith => _$ProtocolInfoCopyWithImpl<ProtocolInfo>(this as ProtocolInfo, _$identity);

  /// Serializes this ProtocolInfo to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolInfo&&(identical(other.name, name) || other.name == name)&&(identical(other.path, path) || other.path == path)&&(identical(other.description, description) || other.description == description)&&(identical(other.version, version) || other.version == version)&&(identical(other.lastModified, lastModified) || other.lastModified == lastModified)&&const DeepCollectionEquality().equals(other.tags, tags)&&(identical(other.author, author) || other.author == author)&&(identical(other.license, license) || other.license == license)&&(identical(other.createdDate, createdDate) || other.createdDate == createdDate)&&(identical(other.category, category) || other.category == category)&&const DeepCollectionEquality().equals(other.metadata, metadata)&&(identical(other.isFavorite, isFavorite) || other.isFavorite == isFavorite)&&(identical(other.runCount, runCount) || other.runCount == runCount)&&(identical(other.averageRating, averageRating) || other.averageRating == averageRating)&&(identical(other.estimatedDuration, estimatedDuration) || other.estimatedDuration == estimatedDuration)&&(identical(other.complexity, complexity) || other.complexity == complexity)&&(identical(other.iconUrl, iconUrl) || other.iconUrl == iconUrl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,path,description,version,lastModified,const DeepCollectionEquality().hash(tags),author,license,createdDate,category,const DeepCollectionEquality().hash(metadata),isFavorite,runCount,averageRating,estimatedDuration,complexity,iconUrl);

@override
String toString() {
  return 'ProtocolInfo(name: $name, path: $path, description: $description, version: $version, lastModified: $lastModified, tags: $tags, author: $author, license: $license, createdDate: $createdDate, category: $category, metadata: $metadata, isFavorite: $isFavorite, runCount: $runCount, averageRating: $averageRating, estimatedDuration: $estimatedDuration, complexity: $complexity, iconUrl: $iconUrl)';
}


}

/// @nodoc
abstract mixin class $ProtocolInfoCopyWith<$Res>  {
  factory $ProtocolInfoCopyWith(ProtocolInfo value, $Res Function(ProtocolInfo) _then) = _$ProtocolInfoCopyWithImpl;
@useResult
$Res call({
 String name, String path, String description, String? version,@JsonKey(name: 'last_modified') DateTime? lastModified, List<String>? tags, String? author, String? license,@JsonKey(name: 'created_date') DateTime? createdDate, String? category, Map<String, dynamic>? metadata,@JsonKey(name: 'is_favorite') bool? isFavorite,@JsonKey(name: 'run_count') int? runCount,@JsonKey(name: 'average_rating') double? averageRating,@JsonKey(name: 'estimated_duration') String? estimatedDuration, ProtocolComplexity? complexity,@JsonKey(name: 'icon_url') String? iconUrl
});




}
/// @nodoc
class _$ProtocolInfoCopyWithImpl<$Res>
    implements $ProtocolInfoCopyWith<$Res> {
  _$ProtocolInfoCopyWithImpl(this._self, this._then);

  final ProtocolInfo _self;
  final $Res Function(ProtocolInfo) _then;

/// Create a copy of ProtocolInfo
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? path = null,Object? description = null,Object? version = freezed,Object? lastModified = freezed,Object? tags = freezed,Object? author = freezed,Object? license = freezed,Object? createdDate = freezed,Object? category = freezed,Object? metadata = freezed,Object? isFavorite = freezed,Object? runCount = freezed,Object? averageRating = freezed,Object? estimatedDuration = freezed,Object? complexity = freezed,Object? iconUrl = freezed,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,path: null == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,version: freezed == version ? _self.version : version // ignore: cast_nullable_to_non_nullable
as String?,lastModified: freezed == lastModified ? _self.lastModified : lastModified // ignore: cast_nullable_to_non_nullable
as DateTime?,tags: freezed == tags ? _self.tags : tags // ignore: cast_nullable_to_non_nullable
as List<String>?,author: freezed == author ? _self.author : author // ignore: cast_nullable_to_non_nullable
as String?,license: freezed == license ? _self.license : license // ignore: cast_nullable_to_non_nullable
as String?,createdDate: freezed == createdDate ? _self.createdDate : createdDate // ignore: cast_nullable_to_non_nullable
as DateTime?,category: freezed == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String?,metadata: freezed == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,isFavorite: freezed == isFavorite ? _self.isFavorite : isFavorite // ignore: cast_nullable_to_non_nullable
as bool?,runCount: freezed == runCount ? _self.runCount : runCount // ignore: cast_nullable_to_non_nullable
as int?,averageRating: freezed == averageRating ? _self.averageRating : averageRating // ignore: cast_nullable_to_non_nullable
as double?,estimatedDuration: freezed == estimatedDuration ? _self.estimatedDuration : estimatedDuration // ignore: cast_nullable_to_non_nullable
as String?,complexity: freezed == complexity ? _self.complexity : complexity // ignore: cast_nullable_to_non_nullable
as ProtocolComplexity?,iconUrl: freezed == iconUrl ? _self.iconUrl : iconUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _ProtocolInfo implements ProtocolInfo {
  const _ProtocolInfo({required this.name, required this.path, required this.description, this.version, @JsonKey(name: 'last_modified') this.lastModified, final  List<String>? tags, this.author, this.license, @JsonKey(name: 'created_date') this.createdDate, this.category, final  Map<String, dynamic>? metadata, @JsonKey(name: 'is_favorite') this.isFavorite, @JsonKey(name: 'run_count') this.runCount, @JsonKey(name: 'average_rating') this.averageRating, @JsonKey(name: 'estimated_duration') this.estimatedDuration, this.complexity, @JsonKey(name: 'icon_url') this.iconUrl}): _tags = tags,_metadata = metadata;
  factory _ProtocolInfo.fromJson(Map<String, dynamic> json) => _$ProtocolInfoFromJson(json);

// Mandatory fields
@override final  String name;
@override final  String path;
@override final  String description;
// Optional fields from TypeScript model
@override final  String? version;
@override@JsonKey(name: 'last_modified') final  DateTime? lastModified;
 final  List<String>? _tags;
@override List<String>? get tags {
  final value = _tags;
  if (value == null) return null;
  if (_tags is EqualUnmodifiableListView) return _tags;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override final  String? author;
@override final  String? license;
@override@JsonKey(name: 'created_date') final  DateTime? createdDate;
@override final  String? category;
 final  Map<String, dynamic>? _metadata;
@override Map<String, dynamic>? get metadata {
  final value = _metadata;
  if (value == null) return null;
  if (_metadata is EqualUnmodifiableMapView) return _metadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'is_favorite') final  bool? isFavorite;
@override@JsonKey(name: 'run_count') final  int? runCount;
@override@JsonKey(name: 'average_rating') final  double? averageRating;
@override@JsonKey(name: 'estimated_duration') final  String? estimatedDuration;
// Could be parsed into Duration later
@override final  ProtocolComplexity? complexity;
@override@JsonKey(name: 'icon_url') final  String? iconUrl;

/// Create a copy of ProtocolInfo
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolInfoCopyWith<_ProtocolInfo> get copyWith => __$ProtocolInfoCopyWithImpl<_ProtocolInfo>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolInfoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolInfo&&(identical(other.name, name) || other.name == name)&&(identical(other.path, path) || other.path == path)&&(identical(other.description, description) || other.description == description)&&(identical(other.version, version) || other.version == version)&&(identical(other.lastModified, lastModified) || other.lastModified == lastModified)&&const DeepCollectionEquality().equals(other._tags, _tags)&&(identical(other.author, author) || other.author == author)&&(identical(other.license, license) || other.license == license)&&(identical(other.createdDate, createdDate) || other.createdDate == createdDate)&&(identical(other.category, category) || other.category == category)&&const DeepCollectionEquality().equals(other._metadata, _metadata)&&(identical(other.isFavorite, isFavorite) || other.isFavorite == isFavorite)&&(identical(other.runCount, runCount) || other.runCount == runCount)&&(identical(other.averageRating, averageRating) || other.averageRating == averageRating)&&(identical(other.estimatedDuration, estimatedDuration) || other.estimatedDuration == estimatedDuration)&&(identical(other.complexity, complexity) || other.complexity == complexity)&&(identical(other.iconUrl, iconUrl) || other.iconUrl == iconUrl));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,name,path,description,version,lastModified,const DeepCollectionEquality().hash(_tags),author,license,createdDate,category,const DeepCollectionEquality().hash(_metadata),isFavorite,runCount,averageRating,estimatedDuration,complexity,iconUrl);

@override
String toString() {
  return 'ProtocolInfo(name: $name, path: $path, description: $description, version: $version, lastModified: $lastModified, tags: $tags, author: $author, license: $license, createdDate: $createdDate, category: $category, metadata: $metadata, isFavorite: $isFavorite, runCount: $runCount, averageRating: $averageRating, estimatedDuration: $estimatedDuration, complexity: $complexity, iconUrl: $iconUrl)';
}


}

/// @nodoc
abstract mixin class _$ProtocolInfoCopyWith<$Res> implements $ProtocolInfoCopyWith<$Res> {
  factory _$ProtocolInfoCopyWith(_ProtocolInfo value, $Res Function(_ProtocolInfo) _then) = __$ProtocolInfoCopyWithImpl;
@override @useResult
$Res call({
 String name, String path, String description, String? version,@JsonKey(name: 'last_modified') DateTime? lastModified, List<String>? tags, String? author, String? license,@JsonKey(name: 'created_date') DateTime? createdDate, String? category, Map<String, dynamic>? metadata,@JsonKey(name: 'is_favorite') bool? isFavorite,@JsonKey(name: 'run_count') int? runCount,@JsonKey(name: 'average_rating') double? averageRating,@JsonKey(name: 'estimated_duration') String? estimatedDuration, ProtocolComplexity? complexity,@JsonKey(name: 'icon_url') String? iconUrl
});




}
/// @nodoc
class __$ProtocolInfoCopyWithImpl<$Res>
    implements _$ProtocolInfoCopyWith<$Res> {
  __$ProtocolInfoCopyWithImpl(this._self, this._then);

  final _ProtocolInfo _self;
  final $Res Function(_ProtocolInfo) _then;

/// Create a copy of ProtocolInfo
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? path = null,Object? description = null,Object? version = freezed,Object? lastModified = freezed,Object? tags = freezed,Object? author = freezed,Object? license = freezed,Object? createdDate = freezed,Object? category = freezed,Object? metadata = freezed,Object? isFavorite = freezed,Object? runCount = freezed,Object? averageRating = freezed,Object? estimatedDuration = freezed,Object? complexity = freezed,Object? iconUrl = freezed,}) {
  return _then(_ProtocolInfo(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,path: null == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,version: freezed == version ? _self.version : version // ignore: cast_nullable_to_non_nullable
as String?,lastModified: freezed == lastModified ? _self.lastModified : lastModified // ignore: cast_nullable_to_non_nullable
as DateTime?,tags: freezed == tags ? _self._tags : tags // ignore: cast_nullable_to_non_nullable
as List<String>?,author: freezed == author ? _self.author : author // ignore: cast_nullable_to_non_nullable
as String?,license: freezed == license ? _self.license : license // ignore: cast_nullable_to_non_nullable
as String?,createdDate: freezed == createdDate ? _self.createdDate : createdDate // ignore: cast_nullable_to_non_nullable
as DateTime?,category: freezed == category ? _self.category : category // ignore: cast_nullable_to_non_nullable
as String?,metadata: freezed == metadata ? _self._metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,isFavorite: freezed == isFavorite ? _self.isFavorite : isFavorite // ignore: cast_nullable_to_non_nullable
as bool?,runCount: freezed == runCount ? _self.runCount : runCount // ignore: cast_nullable_to_non_nullable
as int?,averageRating: freezed == averageRating ? _self.averageRating : averageRating // ignore: cast_nullable_to_non_nullable
as double?,estimatedDuration: freezed == estimatedDuration ? _self.estimatedDuration : estimatedDuration // ignore: cast_nullable_to_non_nullable
as String?,complexity: freezed == complexity ? _self.complexity : complexity // ignore: cast_nullable_to_non_nullable
as ProtocolComplexity?,iconUrl: freezed == iconUrl ? _self.iconUrl : iconUrl // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
