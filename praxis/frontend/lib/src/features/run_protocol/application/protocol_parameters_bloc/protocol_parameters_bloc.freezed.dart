// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_parameters_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolParametersEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParametersEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolParametersEvent()';
}


}

/// @nodoc
class $ProtocolParametersEventCopyWith<$Res>  {
$ProtocolParametersEventCopyWith(ProtocolParametersEvent _, $Res Function(ProtocolParametersEvent) __);
}


/// @nodoc


class LoadProtocolParameters implements ProtocolParametersEvent {
  const LoadProtocolParameters({required this.protocolDetails, final  Map<String, dynamic>? existingConfiguredParameters}): _existingConfiguredParameters = existingConfiguredParameters;
  

 final  ProtocolDetails protocolDetails;
 final  Map<String, dynamic>? _existingConfiguredParameters;
 Map<String, dynamic>? get existingConfiguredParameters {
  final value = _existingConfiguredParameters;
  if (value == null) return null;
  if (_existingConfiguredParameters is EqualUnmodifiableMapView) return _existingConfiguredParameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LoadProtocolParametersCopyWith<LoadProtocolParameters> get copyWith => _$LoadProtocolParametersCopyWithImpl<LoadProtocolParameters>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LoadProtocolParameters&&(identical(other.protocolDetails, protocolDetails) || other.protocolDetails == protocolDetails)&&const DeepCollectionEquality().equals(other._existingConfiguredParameters, _existingConfiguredParameters));
}


@override
int get hashCode => Object.hash(runtimeType,protocolDetails,const DeepCollectionEquality().hash(_existingConfiguredParameters));

@override
String toString() {
  return 'ProtocolParametersEvent.loadProtocolParameters(protocolDetails: $protocolDetails, existingConfiguredParameters: $existingConfiguredParameters)';
}


}

/// @nodoc
abstract mixin class $LoadProtocolParametersCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $LoadProtocolParametersCopyWith(LoadProtocolParameters value, $Res Function(LoadProtocolParameters) _then) = _$LoadProtocolParametersCopyWithImpl;
@useResult
$Res call({
 ProtocolDetails protocolDetails, Map<String, dynamic>? existingConfiguredParameters
});


$ProtocolDetailsCopyWith<$Res> get protocolDetails;

}
/// @nodoc
class _$LoadProtocolParametersCopyWithImpl<$Res>
    implements $LoadProtocolParametersCopyWith<$Res> {
  _$LoadProtocolParametersCopyWithImpl(this._self, this._then);

  final LoadProtocolParameters _self;
  final $Res Function(LoadProtocolParameters) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? protocolDetails = null,Object? existingConfiguredParameters = freezed,}) {
  return _then(LoadProtocolParameters(
protocolDetails: null == protocolDetails ? _self.protocolDetails : protocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails,existingConfiguredParameters: freezed == existingConfiguredParameters ? _self._existingConfiguredParameters : existingConfiguredParameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolDetailsCopyWith<$Res> get protocolDetails {
  
  return $ProtocolDetailsCopyWith<$Res>(_self.protocolDetails, (value) {
    return _then(_self.copyWith(protocolDetails: value));
  });
}
}

/// @nodoc


class ParameterValueChanged implements ProtocolParametersEvent {
  const ParameterValueChanged({required this.parameterPath, required this.value, this.itemIndex, this.subKeyOrDictItemKey});
  

 final  String parameterPath;
 final  dynamic value;
 final  int? itemIndex;
 final  String? subKeyOrDictItemKey;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParameterValueChangedCopyWith<ParameterValueChanged> get copyWith => _$ParameterValueChangedCopyWithImpl<ParameterValueChanged>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterValueChanged&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&const DeepCollectionEquality().equals(other.value, value)&&(identical(other.itemIndex, itemIndex) || other.itemIndex == itemIndex)&&(identical(other.subKeyOrDictItemKey, subKeyOrDictItemKey) || other.subKeyOrDictItemKey == subKeyOrDictItemKey));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,const DeepCollectionEquality().hash(value),itemIndex,subKeyOrDictItemKey);

@override
String toString() {
  return 'ProtocolParametersEvent.parameterValueChanged(parameterPath: $parameterPath, value: $value, itemIndex: $itemIndex, subKeyOrDictItemKey: $subKeyOrDictItemKey)';
}


}

/// @nodoc
abstract mixin class $ParameterValueChangedCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $ParameterValueChangedCopyWith(ParameterValueChanged value, $Res Function(ParameterValueChanged) _then) = _$ParameterValueChangedCopyWithImpl;
@useResult
$Res call({
 String parameterPath, dynamic value, int? itemIndex, String? subKeyOrDictItemKey
});




}
/// @nodoc
class _$ParameterValueChangedCopyWithImpl<$Res>
    implements $ParameterValueChangedCopyWith<$Res> {
  _$ParameterValueChangedCopyWithImpl(this._self, this._then);

  final ParameterValueChanged _self;
  final $Res Function(ParameterValueChanged) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? value = freezed,Object? itemIndex = freezed,Object? subKeyOrDictItemKey = freezed,}) {
  return _then(ParameterValueChanged(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as dynamic,itemIndex: freezed == itemIndex ? _self.itemIndex : itemIndex // ignore: cast_nullable_to_non_nullable
as int?,subKeyOrDictItemKey: freezed == subKeyOrDictItemKey ? _self.subKeyOrDictItemKey : subKeyOrDictItemKey // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

/// @nodoc


class AddArrayItem implements ProtocolParametersEvent {
  const AddArrayItem({required this.parameterPath});
  

 final  String parameterPath;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddArrayItemCopyWith<AddArrayItem> get copyWith => _$AddArrayItemCopyWithImpl<AddArrayItem>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddArrayItem&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath);

@override
String toString() {
  return 'ProtocolParametersEvent.addArrayItem(parameterPath: $parameterPath)';
}


}

/// @nodoc
abstract mixin class $AddArrayItemCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $AddArrayItemCopyWith(AddArrayItem value, $Res Function(AddArrayItem) _then) = _$AddArrayItemCopyWithImpl;
@useResult
$Res call({
 String parameterPath
});




}
/// @nodoc
class _$AddArrayItemCopyWithImpl<$Res>
    implements $AddArrayItemCopyWith<$Res> {
  _$AddArrayItemCopyWithImpl(this._self, this._then);

  final AddArrayItem _self;
  final $Res Function(AddArrayItem) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,}) {
  return _then(AddArrayItem(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddArrayItemWithValue implements ProtocolParametersEvent {
  const AddArrayItemWithValue({required this.parameterPath, required this.value});
  

 final  String parameterPath;
 final  dynamic value;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddArrayItemWithValueCopyWith<AddArrayItemWithValue> get copyWith => _$AddArrayItemWithValueCopyWithImpl<AddArrayItemWithValue>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddArrayItemWithValue&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&const DeepCollectionEquality().equals(other.value, value));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,const DeepCollectionEquality().hash(value));

@override
String toString() {
  return 'ProtocolParametersEvent.addArrayItemWithValue(parameterPath: $parameterPath, value: $value)';
}


}

/// @nodoc
abstract mixin class $AddArrayItemWithValueCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $AddArrayItemWithValueCopyWith(AddArrayItemWithValue value, $Res Function(AddArrayItemWithValue) _then) = _$AddArrayItemWithValueCopyWithImpl;
@useResult
$Res call({
 String parameterPath, dynamic value
});




}
/// @nodoc
class _$AddArrayItemWithValueCopyWithImpl<$Res>
    implements $AddArrayItemWithValueCopyWith<$Res> {
  _$AddArrayItemWithValueCopyWithImpl(this._self, this._then);

  final AddArrayItemWithValue _self;
  final $Res Function(AddArrayItemWithValue) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? value = freezed,}) {
  return _then(AddArrayItemWithValue(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

/// @nodoc


class RemoveArrayItem implements ProtocolParametersEvent {
  const RemoveArrayItem({required this.parameterPath, required this.index});
  

 final  String parameterPath;
 final  int index;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RemoveArrayItemCopyWith<RemoveArrayItem> get copyWith => _$RemoveArrayItemCopyWithImpl<RemoveArrayItem>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RemoveArrayItem&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&(identical(other.index, index) || other.index == index));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,index);

@override
String toString() {
  return 'ProtocolParametersEvent.removeArrayItem(parameterPath: $parameterPath, index: $index)';
}


}

/// @nodoc
abstract mixin class $RemoveArrayItemCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $RemoveArrayItemCopyWith(RemoveArrayItem value, $Res Function(RemoveArrayItem) _then) = _$RemoveArrayItemCopyWithImpl;
@useResult
$Res call({
 String parameterPath, int index
});




}
/// @nodoc
class _$RemoveArrayItemCopyWithImpl<$Res>
    implements $RemoveArrayItemCopyWith<$Res> {
  _$RemoveArrayItemCopyWithImpl(this._self, this._then);

  final RemoveArrayItem _self;
  final $Res Function(RemoveArrayItem) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? index = null,}) {
  return _then(RemoveArrayItem(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,index: null == index ? _self.index : index // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

/// @nodoc


class ReorderArrayItem implements ProtocolParametersEvent {
  const ReorderArrayItem({required this.parameterPath, required this.oldIndex, required this.newIndex});
  

 final  String parameterPath;
 final  int oldIndex;
 final  int newIndex;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReorderArrayItemCopyWith<ReorderArrayItem> get copyWith => _$ReorderArrayItemCopyWithImpl<ReorderArrayItem>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ReorderArrayItem&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&(identical(other.oldIndex, oldIndex) || other.oldIndex == oldIndex)&&(identical(other.newIndex, newIndex) || other.newIndex == newIndex));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,oldIndex,newIndex);

@override
String toString() {
  return 'ProtocolParametersEvent.reorderArrayItem(parameterPath: $parameterPath, oldIndex: $oldIndex, newIndex: $newIndex)';
}


}

/// @nodoc
abstract mixin class $ReorderArrayItemCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $ReorderArrayItemCopyWith(ReorderArrayItem value, $Res Function(ReorderArrayItem) _then) = _$ReorderArrayItemCopyWithImpl;
@useResult
$Res call({
 String parameterPath, int oldIndex, int newIndex
});




}
/// @nodoc
class _$ReorderArrayItemCopyWithImpl<$Res>
    implements $ReorderArrayItemCopyWith<$Res> {
  _$ReorderArrayItemCopyWithImpl(this._self, this._then);

  final ReorderArrayItem _self;
  final $Res Function(ReorderArrayItem) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? oldIndex = null,Object? newIndex = null,}) {
  return _then(ReorderArrayItem(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,oldIndex: null == oldIndex ? _self.oldIndex : oldIndex // ignore: cast_nullable_to_non_nullable
as int,newIndex: null == newIndex ? _self.newIndex : newIndex // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

/// @nodoc


class AddDictionaryPair implements ProtocolParametersEvent {
  const AddDictionaryPair({required this.parameterPath});
  

 final  String parameterPath;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddDictionaryPairCopyWith<AddDictionaryPair> get copyWith => _$AddDictionaryPairCopyWithImpl<AddDictionaryPair>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddDictionaryPair&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath);

@override
String toString() {
  return 'ProtocolParametersEvent.addDictionaryPair(parameterPath: $parameterPath)';
}


}

/// @nodoc
abstract mixin class $AddDictionaryPairCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $AddDictionaryPairCopyWith(AddDictionaryPair value, $Res Function(AddDictionaryPair) _then) = _$AddDictionaryPairCopyWithImpl;
@useResult
$Res call({
 String parameterPath
});




}
/// @nodoc
class _$AddDictionaryPairCopyWithImpl<$Res>
    implements $AddDictionaryPairCopyWith<$Res> {
  _$AddDictionaryPairCopyWithImpl(this._self, this._then);

  final AddDictionaryPair _self;
  final $Res Function(AddDictionaryPair) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,}) {
  return _then(AddDictionaryPair(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class AddDictionaryPairWithKey implements ProtocolParametersEvent {
  const AddDictionaryPairWithKey({required this.parameterPath, required this.key});
  

 final  String parameterPath;
 final  String key;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AddDictionaryPairWithKeyCopyWith<AddDictionaryPairWithKey> get copyWith => _$AddDictionaryPairWithKeyCopyWithImpl<AddDictionaryPairWithKey>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AddDictionaryPairWithKey&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&(identical(other.key, key) || other.key == key));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,key);

@override
String toString() {
  return 'ProtocolParametersEvent.addDictionaryPairWithKey(parameterPath: $parameterPath, key: $key)';
}


}

/// @nodoc
abstract mixin class $AddDictionaryPairWithKeyCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $AddDictionaryPairWithKeyCopyWith(AddDictionaryPairWithKey value, $Res Function(AddDictionaryPairWithKey) _then) = _$AddDictionaryPairWithKeyCopyWithImpl;
@useResult
$Res call({
 String parameterPath, String key
});




}
/// @nodoc
class _$AddDictionaryPairWithKeyCopyWithImpl<$Res>
    implements $AddDictionaryPairWithKeyCopyWith<$Res> {
  _$AddDictionaryPairWithKeyCopyWithImpl(this._self, this._then);

  final AddDictionaryPairWithKey _self;
  final $Res Function(AddDictionaryPairWithKey) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? key = null,}) {
  return _then(AddDictionaryPairWithKey(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,key: null == key ? _self.key : key // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class RemoveDictionaryPair implements ProtocolParametersEvent {
  const RemoveDictionaryPair({required this.parameterPath, required this.keyToRemove});
  

 final  String parameterPath;
 final  String keyToRemove;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RemoveDictionaryPairCopyWith<RemoveDictionaryPair> get copyWith => _$RemoveDictionaryPairCopyWithImpl<RemoveDictionaryPair>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RemoveDictionaryPair&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&(identical(other.keyToRemove, keyToRemove) || other.keyToRemove == keyToRemove));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,keyToRemove);

@override
String toString() {
  return 'ProtocolParametersEvent.removeDictionaryPair(parameterPath: $parameterPath, keyToRemove: $keyToRemove)';
}


}

/// @nodoc
abstract mixin class $RemoveDictionaryPairCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $RemoveDictionaryPairCopyWith(RemoveDictionaryPair value, $Res Function(RemoveDictionaryPair) _then) = _$RemoveDictionaryPairCopyWithImpl;
@useResult
$Res call({
 String parameterPath, String keyToRemove
});




}
/// @nodoc
class _$RemoveDictionaryPairCopyWithImpl<$Res>
    implements $RemoveDictionaryPairCopyWith<$Res> {
  _$RemoveDictionaryPairCopyWithImpl(this._self, this._then);

  final RemoveDictionaryPair _self;
  final $Res Function(RemoveDictionaryPair) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? keyToRemove = null,}) {
  return _then(RemoveDictionaryPair(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,keyToRemove: null == keyToRemove ? _self.keyToRemove : keyToRemove // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class UpdateDictionaryKey implements ProtocolParametersEvent {
  const UpdateDictionaryKey({required this.parameterPath, required this.oldKey, required this.newKey});
  

 final  String parameterPath;
 final  String oldKey;
 final  String newKey;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateDictionaryKeyCopyWith<UpdateDictionaryKey> get copyWith => _$UpdateDictionaryKeyCopyWithImpl<UpdateDictionaryKey>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateDictionaryKey&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&(identical(other.oldKey, oldKey) || other.oldKey == oldKey)&&(identical(other.newKey, newKey) || other.newKey == newKey));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,oldKey,newKey);

@override
String toString() {
  return 'ProtocolParametersEvent.updateDictionaryKey(parameterPath: $parameterPath, oldKey: $oldKey, newKey: $newKey)';
}


}

/// @nodoc
abstract mixin class $UpdateDictionaryKeyCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $UpdateDictionaryKeyCopyWith(UpdateDictionaryKey value, $Res Function(UpdateDictionaryKey) _then) = _$UpdateDictionaryKeyCopyWithImpl;
@useResult
$Res call({
 String parameterPath, String oldKey, String newKey
});




}
/// @nodoc
class _$UpdateDictionaryKeyCopyWithImpl<$Res>
    implements $UpdateDictionaryKeyCopyWith<$Res> {
  _$UpdateDictionaryKeyCopyWithImpl(this._self, this._then);

  final UpdateDictionaryKey _self;
  final $Res Function(UpdateDictionaryKey) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? oldKey = null,Object? newKey = null,}) {
  return _then(UpdateDictionaryKey(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,oldKey: null == oldKey ? _self.oldKey : oldKey // ignore: cast_nullable_to_non_nullable
as String,newKey: null == newKey ? _self.newKey : newKey // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class UpdateDictionaryValue implements ProtocolParametersEvent {
  const UpdateDictionaryValue({required this.parameterPath, required this.key, required this.newValue});
  

 final  String parameterPath;
 final  String key;
 final  dynamic newValue;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateDictionaryValueCopyWith<UpdateDictionaryValue> get copyWith => _$UpdateDictionaryValueCopyWithImpl<UpdateDictionaryValue>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateDictionaryValue&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&(identical(other.key, key) || other.key == key)&&const DeepCollectionEquality().equals(other.newValue, newValue));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,key,const DeepCollectionEquality().hash(newValue));

@override
String toString() {
  return 'ProtocolParametersEvent.updateDictionaryValue(parameterPath: $parameterPath, key: $key, newValue: $newValue)';
}


}

/// @nodoc
abstract mixin class $UpdateDictionaryValueCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $UpdateDictionaryValueCopyWith(UpdateDictionaryValue value, $Res Function(UpdateDictionaryValue) _then) = _$UpdateDictionaryValueCopyWithImpl;
@useResult
$Res call({
 String parameterPath, String key, dynamic newValue
});




}
/// @nodoc
class _$UpdateDictionaryValueCopyWithImpl<$Res>
    implements $UpdateDictionaryValueCopyWith<$Res> {
  _$UpdateDictionaryValueCopyWithImpl(this._self, this._then);

  final UpdateDictionaryValue _self;
  final $Res Function(UpdateDictionaryValue) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? key = null,Object? newValue = freezed,}) {
  return _then(UpdateDictionaryValue(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,key: null == key ? _self.key : key // ignore: cast_nullable_to_non_nullable
as String,newValue: freezed == newValue ? _self.newValue : newValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

/// @nodoc


class AssignValueToDictionaryKey implements ProtocolParametersEvent {
  const AssignValueToDictionaryKey({required this.dictParameterPath, required this.targetKey, required this.draggableValue});
  

 final  String dictParameterPath;
 final  String targetKey;
 final  dynamic draggableValue;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssignValueToDictionaryKeyCopyWith<AssignValueToDictionaryKey> get copyWith => _$AssignValueToDictionaryKeyCopyWithImpl<AssignValueToDictionaryKey>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssignValueToDictionaryKey&&(identical(other.dictParameterPath, dictParameterPath) || other.dictParameterPath == dictParameterPath)&&(identical(other.targetKey, targetKey) || other.targetKey == targetKey)&&const DeepCollectionEquality().equals(other.draggableValue, draggableValue));
}


@override
int get hashCode => Object.hash(runtimeType,dictParameterPath,targetKey,const DeepCollectionEquality().hash(draggableValue));

@override
String toString() {
  return 'ProtocolParametersEvent.assignValueToDictionaryKey(dictParameterPath: $dictParameterPath, targetKey: $targetKey, draggableValue: $draggableValue)';
}


}

/// @nodoc
abstract mixin class $AssignValueToDictionaryKeyCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $AssignValueToDictionaryKeyCopyWith(AssignValueToDictionaryKey value, $Res Function(AssignValueToDictionaryKey) _then) = _$AssignValueToDictionaryKeyCopyWithImpl;
@useResult
$Res call({
 String dictParameterPath, String targetKey, dynamic draggableValue
});




}
/// @nodoc
class _$AssignValueToDictionaryKeyCopyWithImpl<$Res>
    implements $AssignValueToDictionaryKeyCopyWith<$Res> {
  _$AssignValueToDictionaryKeyCopyWithImpl(this._self, this._then);

  final AssignValueToDictionaryKey _self;
  final $Res Function(AssignValueToDictionaryKey) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? dictParameterPath = null,Object? targetKey = null,Object? draggableValue = freezed,}) {
  return _then(AssignValueToDictionaryKey(
dictParameterPath: null == dictParameterPath ? _self.dictParameterPath : dictParameterPath // ignore: cast_nullable_to_non_nullable
as String,targetKey: null == targetKey ? _self.targetKey : targetKey // ignore: cast_nullable_to_non_nullable
as String,draggableValue: freezed == draggableValue ? _self.draggableValue : draggableValue // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

/// @nodoc


class ValidateParameterValue implements ProtocolParametersEvent {
  const ValidateParameterValue({required this.parameterPath, required this.value});
  

 final  String parameterPath;
 final  dynamic value;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ValidateParameterValueCopyWith<ValidateParameterValue> get copyWith => _$ValidateParameterValueCopyWithImpl<ValidateParameterValue>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ValidateParameterValue&&(identical(other.parameterPath, parameterPath) || other.parameterPath == parameterPath)&&const DeepCollectionEquality().equals(other.value, value));
}


@override
int get hashCode => Object.hash(runtimeType,parameterPath,const DeepCollectionEquality().hash(value));

@override
String toString() {
  return 'ProtocolParametersEvent.validateParameterValue(parameterPath: $parameterPath, value: $value)';
}


}

/// @nodoc
abstract mixin class $ValidateParameterValueCopyWith<$Res> implements $ProtocolParametersEventCopyWith<$Res> {
  factory $ValidateParameterValueCopyWith(ValidateParameterValue value, $Res Function(ValidateParameterValue) _then) = _$ValidateParameterValueCopyWithImpl;
@useResult
$Res call({
 String parameterPath, dynamic value
});




}
/// @nodoc
class _$ValidateParameterValueCopyWithImpl<$Res>
    implements $ValidateParameterValueCopyWith<$Res> {
  _$ValidateParameterValueCopyWithImpl(this._self, this._then);

  final ValidateParameterValue _self;
  final $Res Function(ValidateParameterValue) _then;

/// Create a copy of ProtocolParametersEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameterPath = null,Object? value = freezed,}) {
  return _then(ValidateParameterValue(
parameterPath: null == parameterPath ? _self.parameterPath : parameterPath // ignore: cast_nullable_to_non_nullable
as String,value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as dynamic,
  ));
}


}

/// @nodoc
mixin _$ProtocolParametersState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParametersState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolParametersState()';
}


}

/// @nodoc
class $ProtocolParametersStateCopyWith<$Res>  {
$ProtocolParametersStateCopyWith(ProtocolParametersState _, $Res Function(ProtocolParametersState) __);
}


/// @nodoc


class ProtocolParametersInitial implements ProtocolParametersState {
  const ProtocolParametersInitial();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParametersInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolParametersState.initial()';
}


}




/// @nodoc


class ProtocolParametersLoading implements ProtocolParametersState {
  const ProtocolParametersLoading();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParametersLoading);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolParametersState.loading()';
}


}




/// @nodoc


class ProtocolParametersLoaded implements ProtocolParametersState {
  const ProtocolParametersLoaded({required this.protocolDetails, required this.formState, this.isFormValid = false, this.requiredParametersCompletionPercent = 0.0});
  

 final  ProtocolDetails protocolDetails;
 final  RichFormState formState;
@JsonKey() final  bool isFormValid;
@JsonKey() final  double requiredParametersCompletionPercent;

/// Create a copy of ProtocolParametersState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolParametersLoadedCopyWith<ProtocolParametersLoaded> get copyWith => _$ProtocolParametersLoadedCopyWithImpl<ProtocolParametersLoaded>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParametersLoaded&&(identical(other.protocolDetails, protocolDetails) || other.protocolDetails == protocolDetails)&&(identical(other.formState, formState) || other.formState == formState)&&(identical(other.isFormValid, isFormValid) || other.isFormValid == isFormValid)&&(identical(other.requiredParametersCompletionPercent, requiredParametersCompletionPercent) || other.requiredParametersCompletionPercent == requiredParametersCompletionPercent));
}


@override
int get hashCode => Object.hash(runtimeType,protocolDetails,formState,isFormValid,requiredParametersCompletionPercent);

@override
String toString() {
  return 'ProtocolParametersState.loaded(protocolDetails: $protocolDetails, formState: $formState, isFormValid: $isFormValid, requiredParametersCompletionPercent: $requiredParametersCompletionPercent)';
}


}

/// @nodoc
abstract mixin class $ProtocolParametersLoadedCopyWith<$Res> implements $ProtocolParametersStateCopyWith<$Res> {
  factory $ProtocolParametersLoadedCopyWith(ProtocolParametersLoaded value, $Res Function(ProtocolParametersLoaded) _then) = _$ProtocolParametersLoadedCopyWithImpl;
@useResult
$Res call({
 ProtocolDetails protocolDetails, RichFormState formState, bool isFormValid, double requiredParametersCompletionPercent
});


$ProtocolDetailsCopyWith<$Res> get protocolDetails;$RichFormStateCopyWith<$Res> get formState;

}
/// @nodoc
class _$ProtocolParametersLoadedCopyWithImpl<$Res>
    implements $ProtocolParametersLoadedCopyWith<$Res> {
  _$ProtocolParametersLoadedCopyWithImpl(this._self, this._then);

  final ProtocolParametersLoaded _self;
  final $Res Function(ProtocolParametersLoaded) _then;

/// Create a copy of ProtocolParametersState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? protocolDetails = null,Object? formState = null,Object? isFormValid = null,Object? requiredParametersCompletionPercent = null,}) {
  return _then(ProtocolParametersLoaded(
protocolDetails: null == protocolDetails ? _self.protocolDetails : protocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails,formState: null == formState ? _self.formState : formState // ignore: cast_nullable_to_non_nullable
as RichFormState,isFormValid: null == isFormValid ? _self.isFormValid : isFormValid // ignore: cast_nullable_to_non_nullable
as bool,requiredParametersCompletionPercent: null == requiredParametersCompletionPercent ? _self.requiredParametersCompletionPercent : requiredParametersCompletionPercent // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

/// Create a copy of ProtocolParametersState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolDetailsCopyWith<$Res> get protocolDetails {
  
  return $ProtocolDetailsCopyWith<$Res>(_self.protocolDetails, (value) {
    return _then(_self.copyWith(protocolDetails: value));
  });
}/// Create a copy of ProtocolParametersState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RichFormStateCopyWith<$Res> get formState {
  
  return $RichFormStateCopyWith<$Res>(_self.formState, (value) {
    return _then(_self.copyWith(formState: value));
  });
}
}

/// @nodoc


class ProtocolParametersError implements ProtocolParametersState {
  const ProtocolParametersError({required this.message});
  

 final  String message;

/// Create a copy of ProtocolParametersState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolParametersErrorCopyWith<ProtocolParametersError> get copyWith => _$ProtocolParametersErrorCopyWithImpl<ProtocolParametersError>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolParametersError&&(identical(other.message, message) || other.message == message));
}


@override
int get hashCode => Object.hash(runtimeType,message);

@override
String toString() {
  return 'ProtocolParametersState.error(message: $message)';
}


}

/// @nodoc
abstract mixin class $ProtocolParametersErrorCopyWith<$Res> implements $ProtocolParametersStateCopyWith<$Res> {
  factory $ProtocolParametersErrorCopyWith(ProtocolParametersError value, $Res Function(ProtocolParametersError) _then) = _$ProtocolParametersErrorCopyWithImpl;
@useResult
$Res call({
 String message
});




}
/// @nodoc
class _$ProtocolParametersErrorCopyWithImpl<$Res>
    implements $ProtocolParametersErrorCopyWith<$Res> {
  _$ProtocolParametersErrorCopyWithImpl(this._self, this._then);

  final ProtocolParametersError _self;
  final $Res Function(ProtocolParametersError) _then;

/// Create a copy of ProtocolParametersState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? message = null,}) {
  return _then(ProtocolParametersError(
message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
