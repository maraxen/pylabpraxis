// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'rich_form_state.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ParameterUIHints implements DiagnosticableTreeMixin {




@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ParameterUIHints'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParameterUIHints);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ParameterUIHints()';
}


}

/// @nodoc
class $ParameterUIHintsCopyWith<$Res>  {
$ParameterUIHintsCopyWith(ParameterUIHints _, $Res Function(ParameterUIHints) __);
}


/// @nodoc


class _NoneHints with DiagnosticableTreeMixin implements ParameterUIHints {
  const _NoneHints();
  





@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ParameterUIHints.none'))
    ;
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _NoneHints);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ParameterUIHints.none()';
}


}




/// @nodoc


class _DropdownHints with DiagnosticableTreeMixin implements ParameterUIHints {
  const _DropdownHints({required final  List<String> choices}): _choices = choices;
  

 final  List<String> _choices;
 List<String> get choices {
  if (_choices is EqualUnmodifiableListView) return _choices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_choices);
}


/// Create a copy of ParameterUIHints
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DropdownHintsCopyWith<_DropdownHints> get copyWith => __$DropdownHintsCopyWithImpl<_DropdownHints>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ParameterUIHints.dropdown'))
    ..add(DiagnosticsProperty('choices', choices));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DropdownHints&&const DeepCollectionEquality().equals(other._choices, _choices));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_choices));

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ParameterUIHints.dropdown(choices: $choices)';
}


}

/// @nodoc
abstract mixin class _$DropdownHintsCopyWith<$Res> implements $ParameterUIHintsCopyWith<$Res> {
  factory _$DropdownHintsCopyWith(_DropdownHints value, $Res Function(_DropdownHints) _then) = __$DropdownHintsCopyWithImpl;
@useResult
$Res call({
 List<String> choices
});




}
/// @nodoc
class __$DropdownHintsCopyWithImpl<$Res>
    implements _$DropdownHintsCopyWith<$Res> {
  __$DropdownHintsCopyWithImpl(this._self, this._then);

  final _DropdownHints _self;
  final $Res Function(_DropdownHints) _then;

/// Create a copy of ParameterUIHints
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? choices = null,}) {
  return _then(_DropdownHints(
choices: null == choices ? _self._choices : choices // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

/// @nodoc


class _SliderHints with DiagnosticableTreeMixin implements ParameterUIHints {
  const _SliderHints({required this.minValue, required this.maxValue, this.divisions});
  

 final  num minValue;
 final  num maxValue;
 final  num? divisions;

/// Create a copy of ParameterUIHints
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SliderHintsCopyWith<_SliderHints> get copyWith => __$SliderHintsCopyWithImpl<_SliderHints>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'ParameterUIHints.slider'))
    ..add(DiagnosticsProperty('minValue', minValue))..add(DiagnosticsProperty('maxValue', maxValue))..add(DiagnosticsProperty('divisions', divisions));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _SliderHints&&(identical(other.minValue, minValue) || other.minValue == minValue)&&(identical(other.maxValue, maxValue) || other.maxValue == maxValue)&&(identical(other.divisions, divisions) || other.divisions == divisions));
}


@override
int get hashCode => Object.hash(runtimeType,minValue,maxValue,divisions);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'ParameterUIHints.slider(minValue: $minValue, maxValue: $maxValue, divisions: $divisions)';
}


}

/// @nodoc
abstract mixin class _$SliderHintsCopyWith<$Res> implements $ParameterUIHintsCopyWith<$Res> {
  factory _$SliderHintsCopyWith(_SliderHints value, $Res Function(_SliderHints) _then) = __$SliderHintsCopyWithImpl;
@useResult
$Res call({
 num minValue, num maxValue, num? divisions
});




}
/// @nodoc
class __$SliderHintsCopyWithImpl<$Res>
    implements _$SliderHintsCopyWith<$Res> {
  __$SliderHintsCopyWithImpl(this._self, this._then);

  final _SliderHints _self;
  final $Res Function(_SliderHints) _then;

/// Create a copy of ParameterUIHints
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? minValue = null,Object? maxValue = null,Object? divisions = freezed,}) {
  return _then(_SliderHints(
minValue: null == minValue ? _self.minValue : minValue // ignore: cast_nullable_to_non_nullable
as num,maxValue: null == maxValue ? _self.maxValue : maxValue // ignore: cast_nullable_to_non_nullable
as num,divisions: freezed == divisions ? _self.divisions : divisions // ignore: cast_nullable_to_non_nullable
as num?,
  ));
}


}

/// @nodoc
mixin _$FormParameterState implements DiagnosticableTreeMixin {

 String get parameterName; dynamic get currentValue; bool get isValid; String? get validationError; ParameterUIHints? get uiHints; ParameterDefinition? get definition;
/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FormParameterStateCopyWith<FormParameterState> get copyWith => _$FormParameterStateCopyWithImpl<FormParameterState>(this as FormParameterState, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'FormParameterState'))
    ..add(DiagnosticsProperty('parameterName', parameterName))..add(DiagnosticsProperty('currentValue', currentValue))..add(DiagnosticsProperty('isValid', isValid))..add(DiagnosticsProperty('validationError', validationError))..add(DiagnosticsProperty('uiHints', uiHints))..add(DiagnosticsProperty('definition', definition));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is FormParameterState&&(identical(other.parameterName, parameterName) || other.parameterName == parameterName)&&const DeepCollectionEquality().equals(other.currentValue, currentValue)&&(identical(other.isValid, isValid) || other.isValid == isValid)&&(identical(other.validationError, validationError) || other.validationError == validationError)&&(identical(other.uiHints, uiHints) || other.uiHints == uiHints)&&(identical(other.definition, definition) || other.definition == definition));
}


@override
int get hashCode => Object.hash(runtimeType,parameterName,const DeepCollectionEquality().hash(currentValue),isValid,validationError,uiHints,definition);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'FormParameterState(parameterName: $parameterName, currentValue: $currentValue, isValid: $isValid, validationError: $validationError, uiHints: $uiHints, definition: $definition)';
}


}

/// @nodoc
abstract mixin class $FormParameterStateCopyWith<$Res>  {
  factory $FormParameterStateCopyWith(FormParameterState value, $Res Function(FormParameterState) _then) = _$FormParameterStateCopyWithImpl;
@useResult
$Res call({
 String parameterName, dynamic currentValue, bool isValid, String? validationError, ParameterUIHints? uiHints, ParameterDefinition? definition
});


$ParameterUIHintsCopyWith<$Res>? get uiHints;$ParameterDefinitionCopyWith<$Res>? get definition;

}
/// @nodoc
class _$FormParameterStateCopyWithImpl<$Res>
    implements $FormParameterStateCopyWith<$Res> {
  _$FormParameterStateCopyWithImpl(this._self, this._then);

  final FormParameterState _self;
  final $Res Function(FormParameterState) _then;

/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? parameterName = null,Object? currentValue = freezed,Object? isValid = null,Object? validationError = freezed,Object? uiHints = freezed,Object? definition = freezed,}) {
  return _then(_self.copyWith(
parameterName: null == parameterName ? _self.parameterName : parameterName // ignore: cast_nullable_to_non_nullable
as String,currentValue: freezed == currentValue ? _self.currentValue : currentValue // ignore: cast_nullable_to_non_nullable
as dynamic,isValid: null == isValid ? _self.isValid : isValid // ignore: cast_nullable_to_non_nullable
as bool,validationError: freezed == validationError ? _self.validationError : validationError // ignore: cast_nullable_to_non_nullable
as String?,uiHints: freezed == uiHints ? _self.uiHints : uiHints // ignore: cast_nullable_to_non_nullable
as ParameterUIHints?,definition: freezed == definition ? _self.definition : definition // ignore: cast_nullable_to_non_nullable
as ParameterDefinition?,
  ));
}
/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterUIHintsCopyWith<$Res>? get uiHints {
    if (_self.uiHints == null) {
    return null;
  }

  return $ParameterUIHintsCopyWith<$Res>(_self.uiHints!, (value) {
    return _then(_self.copyWith(uiHints: value));
  });
}/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterDefinitionCopyWith<$Res>? get definition {
    if (_self.definition == null) {
    return null;
  }

  return $ParameterDefinitionCopyWith<$Res>(_self.definition!, (value) {
    return _then(_self.copyWith(definition: value));
  });
}
}


/// @nodoc


class _FormParameterState extends FormParameterState with DiagnosticableTreeMixin {
  const _FormParameterState({required this.parameterName, this.currentValue, this.isValid = true, this.validationError, this.uiHints, this.definition}): super._();
  

@override final  String parameterName;
@override final  dynamic currentValue;
@override@JsonKey() final  bool isValid;
@override final  String? validationError;
@override final  ParameterUIHints? uiHints;
@override final  ParameterDefinition? definition;

/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FormParameterStateCopyWith<_FormParameterState> get copyWith => __$FormParameterStateCopyWithImpl<_FormParameterState>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'FormParameterState'))
    ..add(DiagnosticsProperty('parameterName', parameterName))..add(DiagnosticsProperty('currentValue', currentValue))..add(DiagnosticsProperty('isValid', isValid))..add(DiagnosticsProperty('validationError', validationError))..add(DiagnosticsProperty('uiHints', uiHints))..add(DiagnosticsProperty('definition', definition));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _FormParameterState&&(identical(other.parameterName, parameterName) || other.parameterName == parameterName)&&const DeepCollectionEquality().equals(other.currentValue, currentValue)&&(identical(other.isValid, isValid) || other.isValid == isValid)&&(identical(other.validationError, validationError) || other.validationError == validationError)&&(identical(other.uiHints, uiHints) || other.uiHints == uiHints)&&(identical(other.definition, definition) || other.definition == definition));
}


@override
int get hashCode => Object.hash(runtimeType,parameterName,const DeepCollectionEquality().hash(currentValue),isValid,validationError,uiHints,definition);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'FormParameterState(parameterName: $parameterName, currentValue: $currentValue, isValid: $isValid, validationError: $validationError, uiHints: $uiHints, definition: $definition)';
}


}

/// @nodoc
abstract mixin class _$FormParameterStateCopyWith<$Res> implements $FormParameterStateCopyWith<$Res> {
  factory _$FormParameterStateCopyWith(_FormParameterState value, $Res Function(_FormParameterState) _then) = __$FormParameterStateCopyWithImpl;
@override @useResult
$Res call({
 String parameterName, dynamic currentValue, bool isValid, String? validationError, ParameterUIHints? uiHints, ParameterDefinition? definition
});


@override $ParameterUIHintsCopyWith<$Res>? get uiHints;@override $ParameterDefinitionCopyWith<$Res>? get definition;

}
/// @nodoc
class __$FormParameterStateCopyWithImpl<$Res>
    implements _$FormParameterStateCopyWith<$Res> {
  __$FormParameterStateCopyWithImpl(this._self, this._then);

  final _FormParameterState _self;
  final $Res Function(_FormParameterState) _then;

/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? parameterName = null,Object? currentValue = freezed,Object? isValid = null,Object? validationError = freezed,Object? uiHints = freezed,Object? definition = freezed,}) {
  return _then(_FormParameterState(
parameterName: null == parameterName ? _self.parameterName : parameterName // ignore: cast_nullable_to_non_nullable
as String,currentValue: freezed == currentValue ? _self.currentValue : currentValue // ignore: cast_nullable_to_non_nullable
as dynamic,isValid: null == isValid ? _self.isValid : isValid // ignore: cast_nullable_to_non_nullable
as bool,validationError: freezed == validationError ? _self.validationError : validationError // ignore: cast_nullable_to_non_nullable
as String?,uiHints: freezed == uiHints ? _self.uiHints : uiHints // ignore: cast_nullable_to_non_nullable
as ParameterUIHints?,definition: freezed == definition ? _self.definition : definition // ignore: cast_nullable_to_non_nullable
as ParameterDefinition?,
  ));
}

/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterUIHintsCopyWith<$Res>? get uiHints {
    if (_self.uiHints == null) {
    return null;
  }

  return $ParameterUIHintsCopyWith<$Res>(_self.uiHints!, (value) {
    return _then(_self.copyWith(uiHints: value));
  });
}/// Create a copy of FormParameterState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ParameterDefinitionCopyWith<$Res>? get definition {
    if (_self.definition == null) {
    return null;
  }

  return $ParameterDefinitionCopyWith<$Res>(_self.definition!, (value) {
    return _then(_self.copyWith(definition: value));
  });
}
}

/// @nodoc
mixin _$RichFormState implements DiagnosticableTreeMixin {

 Map<String, FormParameterState> get parameterStates; bool get isFormValid;
/// Create a copy of RichFormState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RichFormStateCopyWith<RichFormState> get copyWith => _$RichFormStateCopyWithImpl<RichFormState>(this as RichFormState, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'RichFormState'))
    ..add(DiagnosticsProperty('parameterStates', parameterStates))..add(DiagnosticsProperty('isFormValid', isFormValid));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RichFormState&&const DeepCollectionEquality().equals(other.parameterStates, parameterStates)&&(identical(other.isFormValid, isFormValid) || other.isFormValid == isFormValid));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(parameterStates),isFormValid);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'RichFormState(parameterStates: $parameterStates, isFormValid: $isFormValid)';
}


}

/// @nodoc
abstract mixin class $RichFormStateCopyWith<$Res>  {
  factory $RichFormStateCopyWith(RichFormState value, $Res Function(RichFormState) _then) = _$RichFormStateCopyWithImpl;
@useResult
$Res call({
 Map<String, FormParameterState> parameterStates, bool isFormValid
});




}
/// @nodoc
class _$RichFormStateCopyWithImpl<$Res>
    implements $RichFormStateCopyWith<$Res> {
  _$RichFormStateCopyWithImpl(this._self, this._then);

  final RichFormState _self;
  final $Res Function(RichFormState) _then;

/// Create a copy of RichFormState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? parameterStates = null,Object? isFormValid = null,}) {
  return _then(_self.copyWith(
parameterStates: null == parameterStates ? _self.parameterStates : parameterStates // ignore: cast_nullable_to_non_nullable
as Map<String, FormParameterState>,isFormValid: null == isFormValid ? _self.isFormValid : isFormValid // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// @nodoc


class _RichFormState extends RichFormState with DiagnosticableTreeMixin {
  const _RichFormState({required final  Map<String, FormParameterState> parameterStates, this.isFormValid = false}): _parameterStates = parameterStates,super._();
  

 final  Map<String, FormParameterState> _parameterStates;
@override Map<String, FormParameterState> get parameterStates {
  if (_parameterStates is EqualUnmodifiableMapView) return _parameterStates;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_parameterStates);
}

@override@JsonKey() final  bool isFormValid;

/// Create a copy of RichFormState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RichFormStateCopyWith<_RichFormState> get copyWith => __$RichFormStateCopyWithImpl<_RichFormState>(this, _$identity);


@override
void debugFillProperties(DiagnosticPropertiesBuilder properties) {
  properties
    ..add(DiagnosticsProperty('type', 'RichFormState'))
    ..add(DiagnosticsProperty('parameterStates', parameterStates))..add(DiagnosticsProperty('isFormValid', isFormValid));
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RichFormState&&const DeepCollectionEquality().equals(other._parameterStates, _parameterStates)&&(identical(other.isFormValid, isFormValid) || other.isFormValid == isFormValid));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_parameterStates),isFormValid);

@override
String toString({ DiagnosticLevel minLevel = DiagnosticLevel.info }) {
  return 'RichFormState(parameterStates: $parameterStates, isFormValid: $isFormValid)';
}


}

/// @nodoc
abstract mixin class _$RichFormStateCopyWith<$Res> implements $RichFormStateCopyWith<$Res> {
  factory _$RichFormStateCopyWith(_RichFormState value, $Res Function(_RichFormState) _then) = __$RichFormStateCopyWithImpl;
@override @useResult
$Res call({
 Map<String, FormParameterState> parameterStates, bool isFormValid
});




}
/// @nodoc
class __$RichFormStateCopyWithImpl<$Res>
    implements _$RichFormStateCopyWith<$Res> {
  __$RichFormStateCopyWithImpl(this._self, this._then);

  final _RichFormState _self;
  final $Res Function(_RichFormState) _then;

/// Create a copy of RichFormState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? parameterStates = null,Object? isFormValid = null,}) {
  return _then(_RichFormState(
parameterStates: null == parameterStates ? _self._parameterStates : parameterStates // ignore: cast_nullable_to_non_nullable
as Map<String, FormParameterState>,isFormValid: null == isFormValid ? _self.isFormValid : isFormValid // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
