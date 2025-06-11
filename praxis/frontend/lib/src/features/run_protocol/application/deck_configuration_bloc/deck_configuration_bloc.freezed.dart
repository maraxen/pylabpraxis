// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'deck_instance_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$DeckInstanceEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckInstanceEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'DeckInstanceEvent()';
}


}

/// @nodoc
class $DeckInstanceEventCopyWith<$Res>  {
$DeckInstanceEventCopyWith(DeckInstanceEvent _, $Res Function(DeckInstanceEvent) __);
}


/// @nodoc


class FetchAvailableDeckLayouts implements DeckInstanceEvent {
  const FetchAvailableDeckLayouts();







@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FetchAvailableDeckLayouts);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'DeckInstanceEvent.fetchAvailableDeckLayouts()';
}


}




/// @nodoc


class DeckLayoutSelected implements DeckInstanceEvent {
  const DeckLayoutSelected({this.layoutName});


 final  String? layoutName;

/// Create a copy of DeckInstanceEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckLayoutSelectedCopyWith<DeckLayoutSelected> get copyWith => _$DeckLayoutSelectedCopyWithImpl<DeckLayoutSelected>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckLayoutSelected&&(identical(other.layoutName, layoutName) || other.layoutName == layoutName));
}


@override
int get hashCode => Object.hash(runtimeType,layoutName);

@override
String toString() {
  return 'DeckInstanceEvent.deckLayoutSelected(layoutName: $layoutName)';
}


}

/// @nodoc
abstract mixin class $DeckLayoutSelectedCopyWith<$Res> implements $DeckInstanceEventCopyWith<$Res> {
  factory $DeckLayoutSelectedCopyWith(DeckLayoutSelected value, $Res Function(DeckLayoutSelected) _then) = _$DeckLayoutSelectedCopyWithImpl;
@useResult
$Res call({
 String? layoutName
});




}
/// @nodoc
class _$DeckLayoutSelectedCopyWithImpl<$Res>
    implements $DeckLayoutSelectedCopyWith<$Res> {
  _$DeckLayoutSelectedCopyWithImpl(this._self, this._then);

  final DeckLayoutSelected _self;
  final $Res Function(DeckLayoutSelected) _then;

/// Create a copy of DeckInstanceEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? layoutName = freezed,}) {
  return _then(DeckLayoutSelected(
layoutName: freezed == layoutName ? _self.layoutName : layoutName // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc


class DeckFilePicked implements DeckInstanceEvent {
  const DeckFilePicked({required this.file});


 final  PlatformFile file;

/// Create a copy of DeckInstanceEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckFilePickedCopyWith<DeckFilePicked> get copyWith => _$DeckFilePickedCopyWithImpl<DeckFilePicked>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckFilePicked&&(identical(other.file, file) || other.file == file));
}


@override
int get hashCode => Object.hash(runtimeType,file);

@override
String toString() {
  return 'DeckInstanceEvent.deckFilePicked(file: $file)';
}


}

/// @nodoc
abstract mixin class $DeckFilePickedCopyWith<$Res> implements $DeckInstanceEventCopyWith<$Res> {
  factory $DeckFilePickedCopyWith(DeckFilePicked value, $Res Function(DeckFilePicked) _then) = _$DeckFilePickedCopyWithImpl;
@useResult
$Res call({
 PlatformFile file
});




}
/// @nodoc
class _$DeckFilePickedCopyWithImpl<$Res>
    implements $DeckFilePickedCopyWith<$Res> {
  _$DeckFilePickedCopyWithImpl(this._self, this._then);

  final DeckFilePicked _self;
  final $Res Function(DeckFilePicked) _then;

/// Create a copy of DeckInstanceEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? file = null,}) {
  return _then(DeckFilePicked(
file: null == file ? _self.file : file // ignore: cast_nullable_to_non_nullable
as PlatformFile,
  ));
}


}

/// @nodoc


class ClearDeckSelection implements DeckInstanceEvent {
  const ClearDeckSelection();







@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ClearDeckSelection);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'DeckInstanceEvent.clearDeckSelection()';
}


}




/// @nodoc


class InitializeDeckInstance implements DeckInstanceEvent {
  const InitializeDeckInstance({this.initialSelectedLayoutName, this.initialPickedFile, final  List<String>? availableLayouts}): _availableLayouts = availableLayouts;


 final  String? initialSelectedLayoutName;
 final  PlatformFile? initialPickedFile;
 final  List<String>? _availableLayouts;
 List<String>? get availableLayouts {
  final value = _availableLayouts;
  if (value == null) return null;
  if (_availableLayouts is EqualUnmodifiableListView) return _availableLayouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of DeckInstanceEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InitializeDeckInstanceCopyWith<InitializeDeckInstance> get copyWith => _$InitializeDeckInstanceCopyWithImpl<InitializeDeckInstance>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InitializeDeckInstance&&(identical(other.initialSelectedLayoutName, initialSelectedLayoutName) || other.initialSelectedLayoutName == initialSelectedLayoutName)&&(identical(other.initialPickedFile, initialPickedFile) || other.initialPickedFile == initialPickedFile)&&const DeepCollectionEquality().equals(other._availableLayouts, _availableLayouts));
}


@override
int get hashCode => Object.hash(runtimeType,initialSelectedLayoutName,initialPickedFile,const DeepCollectionEquality().hash(_availableLayouts));

@override
String toString() {
  return 'DeckInstanceEvent.initializeDeckInstance(initialSelectedLayoutName: $initialSelectedLayoutName, initialPickedFile: $initialPickedFile, availableLayouts: $availableLayouts)';
}


}

/// @nodoc
abstract mixin class $InitializeDeckInstanceCopyWith<$Res> implements $DeckInstanceEventCopyWith<$Res> {
  factory $InitializeDeckInstanceCopyWith(InitializeDeckInstance value, $Res Function(InitializeDeckInstance) _then) = _$InitializeDeckInstanceCopyWithImpl;
@useResult
$Res call({
 String? initialSelectedLayoutName, PlatformFile? initialPickedFile, List<String>? availableLayouts
});




}
/// @nodoc
class _$InitializeDeckInstanceCopyWithImpl<$Res>
    implements $InitializeDeckInstanceCopyWith<$Res> {
  _$InitializeDeckInstanceCopyWithImpl(this._self, this._then);

  final InitializeDeckInstance _self;
  final $Res Function(InitializeDeckInstance) _then;

/// Create a copy of DeckInstanceEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? initialSelectedLayoutName = freezed,Object? initialPickedFile = freezed,Object? availableLayouts = freezed,}) {
  return _then(InitializeDeckInstance(
initialSelectedLayoutName: freezed == initialSelectedLayoutName ? _self.initialSelectedLayoutName : initialSelectedLayoutName // ignore: cast_nullable_to_non_nullable
as String?,initialPickedFile: freezed == initialPickedFile ? _self.initialPickedFile : initialPickedFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,availableLayouts: freezed == availableLayouts ? _self._availableLayouts : availableLayouts // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}


}

/// @nodoc
mixin _$DeckInstanceState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckInstanceState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'DeckInstanceState()';
}


}

/// @nodoc
class $DeckInstanceStateCopyWith<$Res>  {
$DeckInstanceStateCopyWith(DeckInstanceState _, $Res Function(DeckInstanceState) __);
}


/// @nodoc


class DeckInstanceInitial implements DeckInstanceState {
  const DeckInstanceInitial();







@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckInstanceInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'DeckInstanceState.initial()';
}


}




/// @nodoc


class DeckInstanceLoading implements DeckInstanceState {
  const DeckInstanceLoading({final  List<String>? availableLayouts, this.selectedLayoutName, this.pickedFile}): _availableLayouts = availableLayouts;


 final  List<String>? _availableLayouts;
 List<String>? get availableLayouts {
  final value = _availableLayouts;
  if (value == null) return null;
  if (_availableLayouts is EqualUnmodifiableListView) return _availableLayouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Previous list while loading new one
 final  String? selectedLayoutName;
 final  PlatformFile? pickedFile;

/// Create a copy of DeckInstanceState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckInstanceLoadingCopyWith<DeckInstanceLoading> get copyWith => _$DeckInstanceLoadingCopyWithImpl<DeckInstanceLoading>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckInstanceLoading&&const DeepCollectionEquality().equals(other._availableLayouts, _availableLayouts)&&(identical(other.selectedLayoutName, selectedLayoutName) || other.selectedLayoutName == selectedLayoutName)&&(identical(other.pickedFile, pickedFile) || other.pickedFile == pickedFile));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_availableLayouts),selectedLayoutName,pickedFile);

@override
String toString() {
  return 'DeckInstanceState.loading(availableLayouts: $availableLayouts, selectedLayoutName: $selectedLayoutName, pickedFile: $pickedFile)';
}


}

/// @nodoc
abstract mixin class $DeckInstanceLoadingCopyWith<$Res> implements $DeckInstanceStateCopyWith<$Res> {
  factory $DeckInstanceLoadingCopyWith(DeckInstanceLoading value, $Res Function(DeckInstanceLoading) _then) = _$DeckInstanceLoadingCopyWithImpl;
@useResult
$Res call({
 List<String>? availableLayouts, String? selectedLayoutName, PlatformFile? pickedFile
});




}
/// @nodoc
class _$DeckInstanceLoadingCopyWithImpl<$Res>
    implements $DeckInstanceLoadingCopyWith<$Res> {
  _$DeckInstanceLoadingCopyWithImpl(this._self, this._then);

  final DeckInstanceLoading _self;
  final $Res Function(DeckInstanceLoading) _then;

/// Create a copy of DeckInstanceState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? availableLayouts = freezed,Object? selectedLayoutName = freezed,Object? pickedFile = freezed,}) {
  return _then(DeckInstanceLoading(
availableLayouts: freezed == availableLayouts ? _self._availableLayouts : availableLayouts // ignore: cast_nullable_to_non_nullable
as List<String>?,selectedLayoutName: freezed == selectedLayoutName ? _self.selectedLayoutName : selectedLayoutName // ignore: cast_nullable_to_non_nullable
as String?,pickedFile: freezed == pickedFile ? _self.pickedFile : pickedFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,
  ));
}


}

/// @nodoc


class DeckInstanceLoaded implements DeckInstanceState {
  const DeckInstanceLoaded({required final  List<String> availableLayouts, this.selectedLayoutName, this.pickedFile, this.isSelectionValid = false}): _availableLayouts = availableLayouts;


 final  List<String> _availableLayouts;
 List<String> get availableLayouts {
  if (_availableLayouts is EqualUnmodifiableListView) return _availableLayouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_availableLayouts);
}

 final  String? selectedLayoutName;
 final  PlatformFile? pickedFile;
@JsonKey() final  bool isSelectionValid;

/// Create a copy of DeckInstanceState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckInstanceLoadedCopyWith<DeckInstanceLoaded> get copyWith => _$DeckInstanceLoadedCopyWithImpl<DeckInstanceLoaded>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckInstanceLoaded&&const DeepCollectionEquality().equals(other._availableLayouts, _availableLayouts)&&(identical(other.selectedLayoutName, selectedLayoutName) || other.selectedLayoutName == selectedLayoutName)&&(identical(other.pickedFile, pickedFile) || other.pickedFile == pickedFile)&&(identical(other.isSelectionValid, isSelectionValid) || other.isSelectionValid == isSelectionValid));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_availableLayouts),selectedLayoutName,pickedFile,isSelectionValid);

@override
String toString() {
  return 'DeckInstanceState.loaded(availableLayouts: $availableLayouts, selectedLayoutName: $selectedLayoutName, pickedFile: $pickedFile, isSelectionValid: $isSelectionValid)';
}


}

/// @nodoc
abstract mixin class $DeckInstanceLoadedCopyWith<$Res> implements $DeckInstanceStateCopyWith<$Res> {
  factory $DeckInstanceLoadedCopyWith(DeckInstanceLoaded value, $Res Function(DeckInstanceLoaded) _then) = _$DeckInstanceLoadedCopyWithImpl;
@useResult
$Res call({
 List<String> availableLayouts, String? selectedLayoutName, PlatformFile? pickedFile, bool isSelectionValid
});




}
/// @nodoc
class _$DeckInstanceLoadedCopyWithImpl<$Res>
    implements $DeckInstanceLoadedCopyWith<$Res> {
  _$DeckInstanceLoadedCopyWithImpl(this._self, this._then);

  final DeckInstanceLoaded _self;
  final $Res Function(DeckInstanceLoaded) _then;

/// Create a copy of DeckInstanceState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? availableLayouts = null,Object? selectedLayoutName = freezed,Object? pickedFile = freezed,Object? isSelectionValid = null,}) {
  return _then(DeckInstanceLoaded(
availableLayouts: null == availableLayouts ? _self._availableLayouts : availableLayouts // ignore: cast_nullable_to_non_nullable
as List<String>,selectedLayoutName: freezed == selectedLayoutName ? _self.selectedLayoutName : selectedLayoutName // ignore: cast_nullable_to_non_nullable
as String?,pickedFile: freezed == pickedFile ? _self.pickedFile : pickedFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,isSelectionValid: null == isSelectionValid ? _self.isSelectionValid : isSelectionValid // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

/// @nodoc


class DeckInstanceError implements DeckInstanceState {
  const DeckInstanceError({required this.message});


 final  String message;

/// Create a copy of DeckInstanceState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckInstanceErrorCopyWith<DeckInstanceError> get copyWith => _$DeckInstanceErrorCopyWithImpl<DeckInstanceError>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckInstanceError&&(identical(other.message, message) || other.message == message));
}


@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'DeckInstanceState.error(message: $message)';
}


}

/// @nodoc
abstract mixin class $DeckInstanceErrorCopyWith<$Res> implements $DeckInstanceStateCopyWith<$Res> {
  factory $DeckInstanceErrorCopyWith(DeckInstanceError value, $Res Function(DeckInstanceError) _then) = _$DeckInstanceErrorCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class _$DeckInstanceErrorCopyWithImpl<$Res>
    implements $DeckInstanceErrorCopyWith<$Res> {
  _$DeckInstanceErrorCopyWithImpl(this._self, this._then);

  final DeckInstanceError _self;
  final $Res Function(DeckInstanceError) _then;

/// Create a copy of DeckInstanceState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(DeckInstanceError(
message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
