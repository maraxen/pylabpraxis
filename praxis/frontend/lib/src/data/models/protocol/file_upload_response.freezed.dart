// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'file_upload_response.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$FileUploadResponse {

 String get filename; String get path;
/// Create a copy of FileUploadResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FileUploadResponseCopyWith<FileUploadResponse> get copyWith => _$FileUploadResponseCopyWithImpl<FileUploadResponse>(this as FileUploadResponse, _$identity);

  /// Serializes this FileUploadResponse to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FileUploadResponse&&(identical(other.filename, filename) || other.filename == filename)&&(identical(other.path, path) || other.path == path));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,filename,path);

@override
String toString() {
  return 'FileUploadResponse(filename: $filename, path: $path)';
}


}

/// @nodoc
abstract mixin class $FileUploadResponseCopyWith<$Res>  {
  factory $FileUploadResponseCopyWith(FileUploadResponse value, $Res Function(FileUploadResponse) _then) = _$FileUploadResponseCopyWithImpl;
@useResult
$Res call({
 String filename, String path
});




}
/// @nodoc
class _$FileUploadResponseCopyWithImpl<$Res>
    implements $FileUploadResponseCopyWith<$Res> {
  _$FileUploadResponseCopyWithImpl(this._self, this._then);

  final FileUploadResponse _self;
  final $Res Function(FileUploadResponse) _then;

/// Create a copy of FileUploadResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? filename = null,Object? path = null,}) {
  return _then(_self.copyWith(
filename: null == filename ? _self.filename : filename // ignore: cast_nullable_to_non_nullable
as String,path: null == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _FileUploadResponse implements FileUploadResponse {
  const _FileUploadResponse({required this.filename, required this.path});
  factory _FileUploadResponse.fromJson(Map<String, dynamic> json) => _$FileUploadResponseFromJson(json);

@override final  String filename;
@override final  String path;

/// Create a copy of FileUploadResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FileUploadResponseCopyWith<_FileUploadResponse> get copyWith => __$FileUploadResponseCopyWithImpl<_FileUploadResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FileUploadResponseToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FileUploadResponse&&(identical(other.filename, filename) || other.filename == filename)&&(identical(other.path, path) || other.path == path));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,filename,path);

@override
String toString() {
  return 'FileUploadResponse(filename: $filename, path: $path)';
}


}

/// @nodoc
abstract mixin class _$FileUploadResponseCopyWith<$Res> implements $FileUploadResponseCopyWith<$Res> {
  factory _$FileUploadResponseCopyWith(_FileUploadResponse value, $Res Function(_FileUploadResponse) _then) = __$FileUploadResponseCopyWithImpl;
@override @useResult
$Res call({
 String filename, String path
});




}
/// @nodoc
class __$FileUploadResponseCopyWithImpl<$Res>
    implements _$FileUploadResponseCopyWith<$Res> {
  __$FileUploadResponseCopyWithImpl(this._self, this._then);

  final _FileUploadResponse _self;
  final $Res Function(_FileUploadResponse) _then;

/// Create a copy of FileUploadResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? filename = null,Object? path = null,}) {
  return _then(_FileUploadResponse(
filename: null == filename ? _self.filename : filename // ignore: cast_nullable_to_non_nullable
as String,path: null == path ? _self.path : path // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
