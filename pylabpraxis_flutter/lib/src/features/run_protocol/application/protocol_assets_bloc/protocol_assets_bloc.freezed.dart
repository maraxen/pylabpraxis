// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_assets_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolAssetsEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAssetsEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolAssetsEvent()';
}


}

/// @nodoc
class $ProtocolAssetsEventCopyWith<$Res>  {
$ProtocolAssetsEventCopyWith(ProtocolAssetsEvent _, $Res Function(ProtocolAssetsEvent) __);
}


/// @nodoc


class LoadRequested implements ProtocolAssetsEvent {
  const LoadRequested();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LoadRequested);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolAssetsEvent.loadRequested()';
}


}




/// @nodoc


class LoadRequiredAssets implements ProtocolAssetsEvent {
  const LoadRequiredAssets({required final  List<ProtocolAsset> assetsFromProtocolDetails, final  Map<String, String>? existingAssignments}): _assetsFromProtocolDetails = assetsFromProtocolDetails,_existingAssignments = existingAssignments;
  

 final  List<ProtocolAsset> _assetsFromProtocolDetails;
 List<ProtocolAsset> get assetsFromProtocolDetails {
  if (_assetsFromProtocolDetails is EqualUnmodifiableListView) return _assetsFromProtocolDetails;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_assetsFromProtocolDetails);
}

 final  Map<String, String>? _existingAssignments;
 Map<String, String>? get existingAssignments {
  final value = _existingAssignments;
  if (value == null) return null;
  if (_existingAssignments is EqualUnmodifiableMapView) return _existingAssignments;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ProtocolAssetsEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LoadRequiredAssetsCopyWith<LoadRequiredAssets> get copyWith => _$LoadRequiredAssetsCopyWithImpl<LoadRequiredAssets>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LoadRequiredAssets&&const DeepCollectionEquality().equals(other._assetsFromProtocolDetails, _assetsFromProtocolDetails)&&const DeepCollectionEquality().equals(other._existingAssignments, _existingAssignments));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_assetsFromProtocolDetails),const DeepCollectionEquality().hash(_existingAssignments));

@override
String toString() {
  return 'ProtocolAssetsEvent.loadRequiredAssets(assetsFromProtocolDetails: $assetsFromProtocolDetails, existingAssignments: $existingAssignments)';
}


}

/// @nodoc
abstract mixin class $LoadRequiredAssetsCopyWith<$Res> implements $ProtocolAssetsEventCopyWith<$Res> {
  factory $LoadRequiredAssetsCopyWith(LoadRequiredAssets value, $Res Function(LoadRequiredAssets) _then) = _$LoadRequiredAssetsCopyWithImpl;
@useResult
$Res call({
 List<ProtocolAsset> assetsFromProtocolDetails, Map<String, String>? existingAssignments
});




}
/// @nodoc
class _$LoadRequiredAssetsCopyWithImpl<$Res>
    implements $LoadRequiredAssetsCopyWith<$Res> {
  _$LoadRequiredAssetsCopyWithImpl(this._self, this._then);

  final LoadRequiredAssets _self;
  final $Res Function(LoadRequiredAssets) _then;

/// Create a copy of ProtocolAssetsEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? assetsFromProtocolDetails = null,Object? existingAssignments = freezed,}) {
  return _then(LoadRequiredAssets(
assetsFromProtocolDetails: null == assetsFromProtocolDetails ? _self._assetsFromProtocolDetails : assetsFromProtocolDetails // ignore: cast_nullable_to_non_nullable
as List<ProtocolAsset>,existingAssignments: freezed == existingAssignments ? _self._existingAssignments : existingAssignments // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,
  ));
}


}

/// @nodoc


class AssetAssignmentChanged implements ProtocolAssetsEvent {
  const AssetAssignmentChanged({required this.assetName, required this.assignedValue});
  

 final  String assetName;
 final  String assignedValue;

/// Create a copy of ProtocolAssetsEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssetAssignmentChangedCopyWith<AssetAssignmentChanged> get copyWith => _$AssetAssignmentChangedCopyWithImpl<AssetAssignmentChanged>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetAssignmentChanged&&(identical(other.assetName, assetName) || other.assetName == assetName)&&(identical(other.assignedValue, assignedValue) || other.assignedValue == assignedValue));
}


@override
int get hashCode => Object.hash(runtimeType,assetName,assignedValue);

@override
String toString() {
  return 'ProtocolAssetsEvent.assetAssignmentChanged(assetName: $assetName, assignedValue: $assignedValue)';
}


}

/// @nodoc
abstract mixin class $AssetAssignmentChangedCopyWith<$Res> implements $ProtocolAssetsEventCopyWith<$Res> {
  factory $AssetAssignmentChangedCopyWith(AssetAssignmentChanged value, $Res Function(AssetAssignmentChanged) _then) = _$AssetAssignmentChangedCopyWithImpl;
@useResult
$Res call({
 String assetName, String assignedValue
});




}
/// @nodoc
class _$AssetAssignmentChangedCopyWithImpl<$Res>
    implements $AssetAssignmentChangedCopyWith<$Res> {
  _$AssetAssignmentChangedCopyWithImpl(this._self, this._then);

  final AssetAssignmentChanged _self;
  final $Res Function(AssetAssignmentChanged) _then;

/// Create a copy of ProtocolAssetsEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? assetName = null,Object? assignedValue = null,}) {
  return _then(AssetAssignmentChanged(
assetName: null == assetName ? _self.assetName : assetName // ignore: cast_nullable_to_non_nullable
as String,assignedValue: null == assignedValue ? _self.assignedValue : assignedValue // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc
mixin _$ProtocolAssetsState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAssetsState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolAssetsState()';
}


}

/// @nodoc
class $ProtocolAssetsStateCopyWith<$Res>  {
$ProtocolAssetsStateCopyWith(ProtocolAssetsState _, $Res Function(ProtocolAssetsState) __);
}


/// @nodoc


class ProtocolAssetsInitial implements ProtocolAssetsState {
  const ProtocolAssetsInitial();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAssetsInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolAssetsState.initial()';
}


}




/// @nodoc


class ProtocolAssetsLoaded implements ProtocolAssetsState {
  const ProtocolAssetsLoaded({required final  List<ProtocolAsset> requiredAssets, required final  Map<String, String> currentAssignments, this.isValid = false}): _requiredAssets = requiredAssets,_currentAssignments = currentAssignments;
  

 final  List<ProtocolAsset> _requiredAssets;
 List<ProtocolAsset> get requiredAssets {
  if (_requiredAssets is EqualUnmodifiableListView) return _requiredAssets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_requiredAssets);
}

 final  Map<String, String> _currentAssignments;
 Map<String, String> get currentAssignments {
  if (_currentAssignments is EqualUnmodifiableMapView) return _currentAssignments;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_currentAssignments);
}

@JsonKey() final  bool isValid;

/// Create a copy of ProtocolAssetsState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolAssetsLoadedCopyWith<ProtocolAssetsLoaded> get copyWith => _$ProtocolAssetsLoadedCopyWithImpl<ProtocolAssetsLoaded>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAssetsLoaded&&const DeepCollectionEquality().equals(other._requiredAssets, _requiredAssets)&&const DeepCollectionEquality().equals(other._currentAssignments, _currentAssignments)&&(identical(other.isValid, isValid) || other.isValid == isValid));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_requiredAssets),const DeepCollectionEquality().hash(_currentAssignments),isValid);

@override
String toString() {
  return 'ProtocolAssetsState.loaded(requiredAssets: $requiredAssets, currentAssignments: $currentAssignments, isValid: $isValid)';
}


}

/// @nodoc
abstract mixin class $ProtocolAssetsLoadedCopyWith<$Res> implements $ProtocolAssetsStateCopyWith<$Res> {
  factory $ProtocolAssetsLoadedCopyWith(ProtocolAssetsLoaded value, $Res Function(ProtocolAssetsLoaded) _then) = _$ProtocolAssetsLoadedCopyWithImpl;
@useResult
$Res call({
 List<ProtocolAsset> requiredAssets, Map<String, String> currentAssignments, bool isValid
});




}
/// @nodoc
class _$ProtocolAssetsLoadedCopyWithImpl<$Res>
    implements $ProtocolAssetsLoadedCopyWith<$Res> {
  _$ProtocolAssetsLoadedCopyWithImpl(this._self, this._then);

  final ProtocolAssetsLoaded _self;
  final $Res Function(ProtocolAssetsLoaded) _then;

/// Create a copy of ProtocolAssetsState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? requiredAssets = null,Object? currentAssignments = null,Object? isValid = null,}) {
  return _then(ProtocolAssetsLoaded(
requiredAssets: null == requiredAssets ? _self._requiredAssets : requiredAssets // ignore: cast_nullable_to_non_nullable
as List<ProtocolAsset>,currentAssignments: null == currentAssignments ? _self._currentAssignments : currentAssignments // ignore: cast_nullable_to_non_nullable
as Map<String, String>,isValid: null == isValid ? _self.isValid : isValid // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

/// @nodoc


class ProtocolAssetsError implements ProtocolAssetsState {
  const ProtocolAssetsError({required this.message});
  

 final  String message;

/// Create a copy of ProtocolAssetsState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolAssetsErrorCopyWith<ProtocolAssetsError> get copyWith => _$ProtocolAssetsErrorCopyWithImpl<ProtocolAssetsError>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolAssetsError&&(identical(other.message, message) || other.message == message));
}


@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'ProtocolAssetsState.error(message: $message)';
}


}

/// @nodoc
abstract mixin class $ProtocolAssetsErrorCopyWith<$Res> implements $ProtocolAssetsStateCopyWith<$Res> {
  factory $ProtocolAssetsErrorCopyWith(ProtocolAssetsError value, $Res Function(ProtocolAssetsError) _then) = _$ProtocolAssetsErrorCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class _$ProtocolAssetsErrorCopyWithImpl<$Res>
    implements $ProtocolAssetsErrorCopyWith<$Res> {
  _$ProtocolAssetsErrorCopyWithImpl(this._self, this._then);

  final ProtocolAssetsError _self;
  final $Res Function(ProtocolAssetsError) _then;

/// Create a copy of ProtocolAssetsState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(ProtocolAssetsError(
message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
