// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'review_data_bundle.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ReviewDataBundle {

 ProtocolInfo get selectedProtocolInfo;/// Optional: Including full details might be useful for display on review screen
/// if ProtocolInfo doesn't have everything (e.g. full description, author).
 ProtocolDetails? get selectedProtocolDetails; Map<String, dynamic> get configuredParameters; Map<String, String> get assignedAssets; String? get deckLayoutName; PlatformFile? get uploadedDeckFile;
/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReviewDataBundleCopyWith<ReviewDataBundle> get copyWith => _$ReviewDataBundleCopyWithImpl<ReviewDataBundle>(this as ReviewDataBundle, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReviewDataBundle&&(identical(other.selectedProtocolInfo, selectedProtocolInfo) || other.selectedProtocolInfo == selectedProtocolInfo)&&(identical(other.selectedProtocolDetails, selectedProtocolDetails) || other.selectedProtocolDetails == selectedProtocolDetails)&&const DeepCollectionEquality().equals(other.configuredParameters, configuredParameters)&&const DeepCollectionEquality().equals(other.assignedAssets, assignedAssets)&&(identical(other.deckLayoutName, deckLayoutName) || other.deckLayoutName == deckLayoutName)&&(identical(other.uploadedDeckFile, uploadedDeckFile) || other.uploadedDeckFile == uploadedDeckFile));
}


@override
int get hashCode => Object.hash(runtimeType,selectedProtocolInfo,selectedProtocolDetails,const DeepCollectionEquality().hash(configuredParameters),const DeepCollectionEquality().hash(assignedAssets),deckLayoutName,uploadedDeckFile);

@override
String toString() {
  return 'ReviewDataBundle(selectedProtocolInfo: $selectedProtocolInfo, selectedProtocolDetails: $selectedProtocolDetails, configuredParameters: $configuredParameters, assignedAssets: $assignedAssets, deckLayoutName: $deckLayoutName, uploadedDeckFile: $uploadedDeckFile)';
}


}

/// @nodoc
abstract mixin class $ReviewDataBundleCopyWith<$Res>  {
  factory $ReviewDataBundleCopyWith(ReviewDataBundle value, $Res Function(ReviewDataBundle) _then) = _$ReviewDataBundleCopyWithImpl;
@useResult
$Res call({
 ProtocolInfo selectedProtocolInfo, ProtocolDetails? selectedProtocolDetails, Map<String, dynamic> configuredParameters, Map<String, String> assignedAssets, String? deckLayoutName, PlatformFile? uploadedDeckFile
});


$ProtocolInfoCopyWith<$Res> get selectedProtocolInfo;$ProtocolDetailsCopyWith<$Res>? get selectedProtocolDetails;

}
/// @nodoc
class _$ReviewDataBundleCopyWithImpl<$Res>
    implements $ReviewDataBundleCopyWith<$Res> {
  _$ReviewDataBundleCopyWithImpl(this._self, this._then);

  final ReviewDataBundle _self;
  final $Res Function(ReviewDataBundle) _then;

/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? selectedProtocolInfo = null,Object? selectedProtocolDetails = freezed,Object? configuredParameters = null,Object? assignedAssets = null,Object? deckLayoutName = freezed,Object? uploadedDeckFile = freezed,}) {
  return _then(_self.copyWith(
selectedProtocolInfo: null == selectedProtocolInfo ? _self.selectedProtocolInfo : selectedProtocolInfo // ignore: cast_nullable_to_non_nullable
as ProtocolInfo,selectedProtocolDetails: freezed == selectedProtocolDetails ? _self.selectedProtocolDetails : selectedProtocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails?,configuredParameters: null == configuredParameters ? _self.configuredParameters : configuredParameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,assignedAssets: null == assignedAssets ? _self.assignedAssets : assignedAssets // ignore: cast_nullable_to_non_nullable
as Map<String, String>,deckLayoutName: freezed == deckLayoutName ? _self.deckLayoutName : deckLayoutName // ignore: cast_nullable_to_non_nullable
as String?,uploadedDeckFile: freezed == uploadedDeckFile ? _self.uploadedDeckFile : uploadedDeckFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,
  ));
}
/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res> get selectedProtocolInfo {
  
  return $ProtocolInfoCopyWith<$Res>(_self.selectedProtocolInfo, (value) {
    return _then(_self.copyWith(selectedProtocolInfo: value));
  });
}/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolDetailsCopyWith<$Res>? get selectedProtocolDetails {
    if (_self.selectedProtocolDetails == null) {
    return null;
  }

  return $ProtocolDetailsCopyWith<$Res>(_self.selectedProtocolDetails!, (value) {
    return _then(_self.copyWith(selectedProtocolDetails: value));
  });
}
}


/// @nodoc


class _ReviewDataBundle implements ReviewDataBundle {
  const _ReviewDataBundle({required this.selectedProtocolInfo, this.selectedProtocolDetails, required final  Map<String, dynamic> configuredParameters, required final  Map<String, String> assignedAssets, this.deckLayoutName, this.uploadedDeckFile}): _configuredParameters = configuredParameters,_assignedAssets = assignedAssets;
  

@override final  ProtocolInfo selectedProtocolInfo;
/// Optional: Including full details might be useful for display on review screen
/// if ProtocolInfo doesn't have everything (e.g. full description, author).
@override final  ProtocolDetails? selectedProtocolDetails;
 final  Map<String, dynamic> _configuredParameters;
@override Map<String, dynamic> get configuredParameters {
  if (_configuredParameters is EqualUnmodifiableMapView) return _configuredParameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_configuredParameters);
}

 final  Map<String, String> _assignedAssets;
@override Map<String, String> get assignedAssets {
  if (_assignedAssets is EqualUnmodifiableMapView) return _assignedAssets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_assignedAssets);
}

@override final  String? deckLayoutName;
@override final  PlatformFile? uploadedDeckFile;

/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReviewDataBundleCopyWith<_ReviewDataBundle> get copyWith => __$ReviewDataBundleCopyWithImpl<_ReviewDataBundle>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ReviewDataBundle&&(identical(other.selectedProtocolInfo, selectedProtocolInfo) || other.selectedProtocolInfo == selectedProtocolInfo)&&(identical(other.selectedProtocolDetails, selectedProtocolDetails) || other.selectedProtocolDetails == selectedProtocolDetails)&&const DeepCollectionEquality().equals(other._configuredParameters, _configuredParameters)&&const DeepCollectionEquality().equals(other._assignedAssets, _assignedAssets)&&(identical(other.deckLayoutName, deckLayoutName) || other.deckLayoutName == deckLayoutName)&&(identical(other.uploadedDeckFile, uploadedDeckFile) || other.uploadedDeckFile == uploadedDeckFile));
}


@override
int get hashCode => Object.hash(runtimeType,selectedProtocolInfo,selectedProtocolDetails,const DeepCollectionEquality().hash(_configuredParameters),const DeepCollectionEquality().hash(_assignedAssets),deckLayoutName,uploadedDeckFile);

@override
String toString() {
  return 'ReviewDataBundle(selectedProtocolInfo: $selectedProtocolInfo, selectedProtocolDetails: $selectedProtocolDetails, configuredParameters: $configuredParameters, assignedAssets: $assignedAssets, deckLayoutName: $deckLayoutName, uploadedDeckFile: $uploadedDeckFile)';
}


}

/// @nodoc
abstract mixin class _$ReviewDataBundleCopyWith<$Res> implements $ReviewDataBundleCopyWith<$Res> {
  factory _$ReviewDataBundleCopyWith(_ReviewDataBundle value, $Res Function(_ReviewDataBundle) _then) = __$ReviewDataBundleCopyWithImpl;
@override @useResult
$Res call({
 ProtocolInfo selectedProtocolInfo, ProtocolDetails? selectedProtocolDetails, Map<String, dynamic> configuredParameters, Map<String, String> assignedAssets, String? deckLayoutName, PlatformFile? uploadedDeckFile
});


@override $ProtocolInfoCopyWith<$Res> get selectedProtocolInfo;@override $ProtocolDetailsCopyWith<$Res>? get selectedProtocolDetails;

}
/// @nodoc
class __$ReviewDataBundleCopyWithImpl<$Res>
    implements _$ReviewDataBundleCopyWith<$Res> {
  __$ReviewDataBundleCopyWithImpl(this._self, this._then);

  final _ReviewDataBundle _self;
  final $Res Function(_ReviewDataBundle) _then;

/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? selectedProtocolInfo = null,Object? selectedProtocolDetails = freezed,Object? configuredParameters = null,Object? assignedAssets = null,Object? deckLayoutName = freezed,Object? uploadedDeckFile = freezed,}) {
  return _then(_ReviewDataBundle(
selectedProtocolInfo: null == selectedProtocolInfo ? _self.selectedProtocolInfo : selectedProtocolInfo // ignore: cast_nullable_to_non_nullable
as ProtocolInfo,selectedProtocolDetails: freezed == selectedProtocolDetails ? _self.selectedProtocolDetails : selectedProtocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails?,configuredParameters: null == configuredParameters ? _self._configuredParameters : configuredParameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,assignedAssets: null == assignedAssets ? _self._assignedAssets : assignedAssets // ignore: cast_nullable_to_non_nullable
as Map<String, String>,deckLayoutName: freezed == deckLayoutName ? _self.deckLayoutName : deckLayoutName // ignore: cast_nullable_to_non_nullable
as String?,uploadedDeckFile: freezed == uploadedDeckFile ? _self.uploadedDeckFile : uploadedDeckFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,
  ));
}

/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res> get selectedProtocolInfo {
  
  return $ProtocolInfoCopyWith<$Res>(_self.selectedProtocolInfo, (value) {
    return _then(_self.copyWith(selectedProtocolInfo: value));
  });
}/// Create a copy of ReviewDataBundle
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolDetailsCopyWith<$Res>? get selectedProtocolDetails {
    if (_self.selectedProtocolDetails == null) {
    return null;
  }

  return $ProtocolDetailsCopyWith<$Res>(_self.selectedProtocolDetails!, (value) {
    return _then(_self.copyWith(selectedProtocolDetails: value));
  });
}
}

// dart format on
