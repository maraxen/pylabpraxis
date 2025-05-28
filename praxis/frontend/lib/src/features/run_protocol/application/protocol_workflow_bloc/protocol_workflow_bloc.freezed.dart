// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_workflow_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolWorkflowEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolWorkflowEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolWorkflowEvent()';
}


}

/// @nodoc
class $ProtocolWorkflowEventCopyWith<$Res>  {
$ProtocolWorkflowEventCopyWith(ProtocolWorkflowEvent _, $Res Function(ProtocolWorkflowEvent) __);
}


/// @nodoc


class InitializeWorkflow implements ProtocolWorkflowEvent {
  const InitializeWorkflow();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is InitializeWorkflow);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolWorkflowEvent.initializeWorkflow()';
}


}




/// @nodoc


class ProtocolSelectedInWorkflow implements ProtocolWorkflowEvent {
  const ProtocolSelectedInWorkflow({required this.selectedProtocol});
  

 final  ProtocolInfo selectedProtocol;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolSelectedInWorkflowCopyWith<ProtocolSelectedInWorkflow> get copyWith => _$ProtocolSelectedInWorkflowCopyWithImpl<ProtocolSelectedInWorkflow>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolSelectedInWorkflow&&(identical(other.selectedProtocol, selectedProtocol) || other.selectedProtocol == selectedProtocol));
}


@override
int get hashCode => Object.hash(runtimeType,selectedProtocol);

@override
String toString() {
  return 'ProtocolWorkflowEvent.protocolSelected(selectedProtocol: $selectedProtocol)';
}


}

/// @nodoc
abstract mixin class $ProtocolSelectedInWorkflowCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $ProtocolSelectedInWorkflowCopyWith(ProtocolSelectedInWorkflow value, $Res Function(ProtocolSelectedInWorkflow) _then) = _$ProtocolSelectedInWorkflowCopyWithImpl;
@useResult
$Res call({
 ProtocolInfo selectedProtocol
});


$ProtocolInfoCopyWith<$Res> get selectedProtocol;

}
/// @nodoc
class _$ProtocolSelectedInWorkflowCopyWithImpl<$Res>
    implements $ProtocolSelectedInWorkflowCopyWith<$Res> {
  _$ProtocolSelectedInWorkflowCopyWithImpl(this._self, this._then);

  final ProtocolSelectedInWorkflow _self;
  final $Res Function(ProtocolSelectedInWorkflow) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? selectedProtocol = null,}) {
  return _then(ProtocolSelectedInWorkflow(
selectedProtocol: null == selectedProtocol ? _self.selectedProtocol : selectedProtocol // ignore: cast_nullable_to_non_nullable
as ProtocolInfo,
  ));
}

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res> get selectedProtocol {
  
  return $ProtocolInfoCopyWith<$Res>(_self.selectedProtocol, (value) {
    return _then(_self.copyWith(selectedProtocol: value));
  });
}
}

/// @nodoc


class ParametersSubmittedToWorkflow implements ProtocolWorkflowEvent {
  const ParametersSubmittedToWorkflow({required final  Map<String, dynamic> parameters}): _parameters = parameters;
  

 final  Map<String, dynamic> _parameters;
 Map<String, dynamic> get parameters {
  if (_parameters is EqualUnmodifiableMapView) return _parameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_parameters);
}


/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ParametersSubmittedToWorkflowCopyWith<ParametersSubmittedToWorkflow> get copyWith => _$ParametersSubmittedToWorkflowCopyWithImpl<ParametersSubmittedToWorkflow>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ParametersSubmittedToWorkflow&&const DeepCollectionEquality().equals(other._parameters, _parameters));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_parameters));

@override
String toString() {
  return 'ProtocolWorkflowEvent.parametersSubmitted(parameters: $parameters)';
}


}

/// @nodoc
abstract mixin class $ParametersSubmittedToWorkflowCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $ParametersSubmittedToWorkflowCopyWith(ParametersSubmittedToWorkflow value, $Res Function(ParametersSubmittedToWorkflow) _then) = _$ParametersSubmittedToWorkflowCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> parameters
});




}
/// @nodoc
class _$ParametersSubmittedToWorkflowCopyWithImpl<$Res>
    implements $ParametersSubmittedToWorkflowCopyWith<$Res> {
  _$ParametersSubmittedToWorkflowCopyWithImpl(this._self, this._then);

  final ParametersSubmittedToWorkflow _self;
  final $Res Function(ParametersSubmittedToWorkflow) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? parameters = null,}) {
  return _then(ParametersSubmittedToWorkflow(
parameters: null == parameters ? _self._parameters : parameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc


class AssetsSubmittedToWorkflow implements ProtocolWorkflowEvent {
  const AssetsSubmittedToWorkflow({required final  Map<String, String> assets}): _assets = assets;
  

 final  Map<String, String> _assets;
 Map<String, String> get assets {
  if (_assets is EqualUnmodifiableMapView) return _assets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_assets);
}


/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AssetsSubmittedToWorkflowCopyWith<AssetsSubmittedToWorkflow> get copyWith => _$AssetsSubmittedToWorkflowCopyWithImpl<AssetsSubmittedToWorkflow>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AssetsSubmittedToWorkflow&&const DeepCollectionEquality().equals(other._assets, _assets));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_assets));

@override
String toString() {
  return 'ProtocolWorkflowEvent.assetsSubmittedToWorkflow(assets: $assets)';
}


}

/// @nodoc
abstract mixin class $AssetsSubmittedToWorkflowCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $AssetsSubmittedToWorkflowCopyWith(AssetsSubmittedToWorkflow value, $Res Function(AssetsSubmittedToWorkflow) _then) = _$AssetsSubmittedToWorkflowCopyWithImpl;
@useResult
$Res call({
 Map<String, String> assets
});




}
/// @nodoc
class _$AssetsSubmittedToWorkflowCopyWithImpl<$Res>
    implements $AssetsSubmittedToWorkflowCopyWith<$Res> {
  _$AssetsSubmittedToWorkflowCopyWithImpl(this._self, this._then);

  final AssetsSubmittedToWorkflow _self;
  final $Res Function(AssetsSubmittedToWorkflow) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? assets = null,}) {
  return _then(AssetsSubmittedToWorkflow(
assets: null == assets ? _self._assets : assets // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}


}

/// @nodoc


class DeckConfigSubmittedToWorkflow implements ProtocolWorkflowEvent {
  const DeckConfigSubmittedToWorkflow({this.layoutName, this.uploadedFile});
  

 final  String? layoutName;
 final  PlatformFile? uploadedFile;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DeckConfigSubmittedToWorkflowCopyWith<DeckConfigSubmittedToWorkflow> get copyWith => _$DeckConfigSubmittedToWorkflowCopyWithImpl<DeckConfigSubmittedToWorkflow>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DeckConfigSubmittedToWorkflow&&(identical(other.layoutName, layoutName) || other.layoutName == layoutName)&&(identical(other.uploadedFile, uploadedFile) || other.uploadedFile == uploadedFile));
}


@override
int get hashCode => Object.hash(runtimeType,layoutName,uploadedFile);

@override
String toString() {
  return 'ProtocolWorkflowEvent.deckConfigSubmitted(layoutName: $layoutName, uploadedFile: $uploadedFile)';
}


}

/// @nodoc
abstract mixin class $DeckConfigSubmittedToWorkflowCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $DeckConfigSubmittedToWorkflowCopyWith(DeckConfigSubmittedToWorkflow value, $Res Function(DeckConfigSubmittedToWorkflow) _then) = _$DeckConfigSubmittedToWorkflowCopyWithImpl;
@useResult
$Res call({
 String? layoutName, PlatformFile? uploadedFile
});




}
/// @nodoc
class _$DeckConfigSubmittedToWorkflowCopyWithImpl<$Res>
    implements $DeckConfigSubmittedToWorkflowCopyWith<$Res> {
  _$DeckConfigSubmittedToWorkflowCopyWithImpl(this._self, this._then);

  final DeckConfigSubmittedToWorkflow _self;
  final $Res Function(DeckConfigSubmittedToWorkflow) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? layoutName = freezed,Object? uploadedFile = freezed,}) {
  return _then(DeckConfigSubmittedToWorkflow(
layoutName: freezed == layoutName ? _self.layoutName : layoutName // ignore: cast_nullable_to_non_nullable
as String?,uploadedFile: freezed == uploadedFile ? _self.uploadedFile : uploadedFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,
  ));
}


}

/// @nodoc


class ProtocolSuccessfullyPrepared implements ProtocolWorkflowEvent {
  const ProtocolSuccessfullyPrepared({required final  Map<String, dynamic> preparedConfig}): _preparedConfig = preparedConfig;
  

 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}


/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolSuccessfullyPreparedCopyWith<ProtocolSuccessfullyPrepared> get copyWith => _$ProtocolSuccessfullyPreparedCopyWithImpl<ProtocolSuccessfullyPrepared>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolSuccessfullyPrepared&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_preparedConfig));

@override
String toString() {
  return 'ProtocolWorkflowEvent.protocolPrepared(preparedConfig: $preparedConfig)';
}


}

/// @nodoc
abstract mixin class $ProtocolSuccessfullyPreparedCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $ProtocolSuccessfullyPreparedCopyWith(ProtocolSuccessfullyPrepared value, $Res Function(ProtocolSuccessfullyPrepared) _then) = _$ProtocolSuccessfullyPreparedCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> preparedConfig
});




}
/// @nodoc
class _$ProtocolSuccessfullyPreparedCopyWithImpl<$Res>
    implements $ProtocolSuccessfullyPreparedCopyWith<$Res> {
  _$ProtocolSuccessfullyPreparedCopyWithImpl(this._self, this._then);

  final ProtocolSuccessfullyPrepared _self;
  final $Res Function(ProtocolSuccessfullyPrepared) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? preparedConfig = null,}) {
  return _then(ProtocolSuccessfullyPrepared(
preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

/// @nodoc


class ProtocolSuccessfullyStarted implements ProtocolWorkflowEvent {
  const ProtocolSuccessfullyStarted({required this.response});
  

 final  ProtocolStatusResponse response;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolSuccessfullyStartedCopyWith<ProtocolSuccessfullyStarted> get copyWith => _$ProtocolSuccessfullyStartedCopyWithImpl<ProtocolSuccessfullyStarted>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolSuccessfullyStarted&&(identical(other.response, response) || other.response == response));
}


@override
int get hashCode => Object.hash(runtimeType,response);

@override
String toString() {
  return 'ProtocolWorkflowEvent.protocolStarted(response: $response)';
}


}

/// @nodoc
abstract mixin class $ProtocolSuccessfullyStartedCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $ProtocolSuccessfullyStartedCopyWith(ProtocolSuccessfullyStarted value, $Res Function(ProtocolSuccessfullyStarted) _then) = _$ProtocolSuccessfullyStartedCopyWithImpl;
@useResult
$Res call({
 ProtocolStatusResponse response
});


$ProtocolStatusResponseCopyWith<$Res> get response;

}
/// @nodoc
class _$ProtocolSuccessfullyStartedCopyWithImpl<$Res>
    implements $ProtocolSuccessfullyStartedCopyWith<$Res> {
  _$ProtocolSuccessfullyStartedCopyWithImpl(this._self, this._then);

  final ProtocolSuccessfullyStarted _self;
  final $Res Function(ProtocolSuccessfullyStarted) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? response = null,}) {
  return _then(ProtocolSuccessfullyStarted(
response: null == response ? _self.response : response // ignore: cast_nullable_to_non_nullable
as ProtocolStatusResponse,
  ));
}

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolStatusResponseCopyWith<$Res> get response {
  
  return $ProtocolStatusResponseCopyWith<$Res>(_self.response, (value) {
    return _then(_self.copyWith(response: value));
  });
}
}

/// @nodoc


class ProceedToNextStep implements ProtocolWorkflowEvent {
  const ProceedToNextStep();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProceedToNextStep);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolWorkflowEvent.proceedToNextStep()';
}


}




/// @nodoc


class GoToStep implements ProtocolWorkflowEvent {
  const GoToStep({required this.targetStep, this.fromReviewScreen = false});
  

 final  WorkflowStep targetStep;
@JsonKey() final  bool fromReviewScreen;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GoToStepCopyWith<GoToStep> get copyWith => _$GoToStepCopyWithImpl<GoToStep>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is GoToStep&&(identical(other.targetStep, targetStep) || other.targetStep == targetStep)&&(identical(other.fromReviewScreen, fromReviewScreen) || other.fromReviewScreen == fromReviewScreen));
}


@override
int get hashCode => Object.hash(runtimeType,targetStep,fromReviewScreen);

@override
String toString() {
  return 'ProtocolWorkflowEvent.goToStep(targetStep: $targetStep, fromReviewScreen: $fromReviewScreen)';
}


}

/// @nodoc
abstract mixin class $GoToStepCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $GoToStepCopyWith(GoToStep value, $Res Function(GoToStep) _then) = _$GoToStepCopyWithImpl;
@useResult
$Res call({
 WorkflowStep targetStep, bool fromReviewScreen
});




}
/// @nodoc
class _$GoToStepCopyWithImpl<$Res>
    implements $GoToStepCopyWith<$Res> {
  _$GoToStepCopyWithImpl(this._self, this._then);

  final GoToStep _self;
  final $Res Function(GoToStep) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? targetStep = null,Object? fromReviewScreen = null,}) {
  return _then(GoToStep(
targetStep: null == targetStep ? _self.targetStep : targetStep // ignore: cast_nullable_to_non_nullable
as WorkflowStep,fromReviewScreen: null == fromReviewScreen ? _self.fromReviewScreen : fromReviewScreen // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

/// @nodoc


class GoToPreviousStep implements ProtocolWorkflowEvent {
  const GoToPreviousStep();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is GoToPreviousStep);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolWorkflowEvent.goToPreviousStep()';
}


}




/// @nodoc


class ResetWorkflow implements ProtocolWorkflowEvent {
  const ResetWorkflow();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ResetWorkflow);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolWorkflowEvent.resetWorkflow()';
}


}




/// @nodoc


class _ProtocolDetailsFetched implements ProtocolWorkflowEvent {
  const _ProtocolDetailsFetched({required this.protocolDetails});
  

 final  ProtocolDetails protocolDetails;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolDetailsFetchedCopyWith<_ProtocolDetailsFetched> get copyWith => __$ProtocolDetailsFetchedCopyWithImpl<_ProtocolDetailsFetched>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolDetailsFetched&&(identical(other.protocolDetails, protocolDetails) || other.protocolDetails == protocolDetails));
}


@override
int get hashCode => Object.hash(runtimeType,protocolDetails);

@override
String toString() {
  return 'ProtocolWorkflowEvent.protocolDetailsFetched(protocolDetails: $protocolDetails)';
}


}

/// @nodoc
abstract mixin class _$ProtocolDetailsFetchedCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory _$ProtocolDetailsFetchedCopyWith(_ProtocolDetailsFetched value, $Res Function(_ProtocolDetailsFetched) _then) = __$ProtocolDetailsFetchedCopyWithImpl;
@useResult
$Res call({
 ProtocolDetails protocolDetails
});


$ProtocolDetailsCopyWith<$Res> get protocolDetails;

}
/// @nodoc
class __$ProtocolDetailsFetchedCopyWithImpl<$Res>
    implements _$ProtocolDetailsFetchedCopyWith<$Res> {
  __$ProtocolDetailsFetchedCopyWithImpl(this._self, this._then);

  final _ProtocolDetailsFetched _self;
  final $Res Function(_ProtocolDetailsFetched) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? protocolDetails = null,}) {
  return _then(_ProtocolDetailsFetched(
protocolDetails: null == protocolDetails ? _self.protocolDetails : protocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails,
  ));
}

/// Create a copy of ProtocolWorkflowEvent
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


class _ProtocolDetailsFetchFailed implements ProtocolWorkflowEvent {
  const _ProtocolDetailsFetchFailed({required this.error});
  

 final  String error;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolDetailsFetchFailedCopyWith<_ProtocolDetailsFetchFailed> get copyWith => __$ProtocolDetailsFetchFailedCopyWithImpl<_ProtocolDetailsFetchFailed>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolDetailsFetchFailed&&(identical(other.error, error) || other.error == error));
}


@override
int get hashCode => Object.hash(runtimeType,error);

@override
String toString() {
  return 'ProtocolWorkflowEvent.protocolDetailsFetchFailed(error: $error)';
}


}

/// @nodoc
abstract mixin class _$ProtocolDetailsFetchFailedCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory _$ProtocolDetailsFetchFailedCopyWith(_ProtocolDetailsFetchFailed value, $Res Function(_ProtocolDetailsFetchFailed) _then) = __$ProtocolDetailsFetchFailedCopyWithImpl;
@useResult
$Res call({
 String error
});




}
/// @nodoc
class __$ProtocolDetailsFetchFailedCopyWithImpl<$Res>
    implements _$ProtocolDetailsFetchFailedCopyWith<$Res> {
  __$ProtocolDetailsFetchFailedCopyWithImpl(this._self, this._then);

  final _ProtocolDetailsFetchFailed _self;
  final $Res Function(_ProtocolDetailsFetchFailed) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,}) {
  return _then(_ProtocolDetailsFetchFailed(
error: null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

/// @nodoc


class UpdateStepValidity implements ProtocolWorkflowEvent {
  const UpdateStepValidity({required this.isValid});
  

 final  bool isValid;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateStepValidityCopyWith<UpdateStepValidity> get copyWith => _$UpdateStepValidityCopyWithImpl<UpdateStepValidity>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateStepValidity&&(identical(other.isValid, isValid) || other.isValid == isValid));
}


@override
int get hashCode => Object.hash(runtimeType,isValid);

@override
String toString() {
  return 'ProtocolWorkflowEvent.updateStepValidity(isValid: $isValid)';
}


}

/// @nodoc
abstract mixin class $UpdateStepValidityCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $UpdateStepValidityCopyWith(UpdateStepValidity value, $Res Function(UpdateStepValidity) _then) = _$UpdateStepValidityCopyWithImpl;
@useResult
$Res call({
 bool isValid
});




}
/// @nodoc
class _$UpdateStepValidityCopyWithImpl<$Res>
    implements $UpdateStepValidityCopyWith<$Res> {
  _$UpdateStepValidityCopyWithImpl(this._self, this._then);

  final UpdateStepValidity _self;
  final $Res Function(UpdateStepValidity) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? isValid = null,}) {
  return _then(UpdateStepValidity(
isValid: null == isValid ? _self.isValid : isValid // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

/// @nodoc


class UpdateParametersProgress implements ProtocolWorkflowEvent {
  const UpdateParametersProgress({required this.completionPercent});
  

 final  double completionPercent;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UpdateParametersProgressCopyWith<UpdateParametersProgress> get copyWith => _$UpdateParametersProgressCopyWithImpl<UpdateParametersProgress>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UpdateParametersProgress&&(identical(other.completionPercent, completionPercent) || other.completionPercent == completionPercent));
}


@override
int get hashCode => Object.hash(runtimeType,completionPercent);

@override
String toString() {
  return 'ProtocolWorkflowEvent.updateParametersProgress(completionPercent: $completionPercent)';
}


}

/// @nodoc
abstract mixin class $UpdateParametersProgressCopyWith<$Res> implements $ProtocolWorkflowEventCopyWith<$Res> {
  factory $UpdateParametersProgressCopyWith(UpdateParametersProgress value, $Res Function(UpdateParametersProgress) _then) = _$UpdateParametersProgressCopyWithImpl;
@useResult
$Res call({
 double completionPercent
});




}
/// @nodoc
class _$UpdateParametersProgressCopyWithImpl<$Res>
    implements $UpdateParametersProgressCopyWith<$Res> {
  _$UpdateParametersProgressCopyWithImpl(this._self, this._then);

  final UpdateParametersProgress _self;
  final $Res Function(UpdateParametersProgress) _then;

/// Create a copy of ProtocolWorkflowEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? completionPercent = null,}) {
  return _then(UpdateParametersProgress(
completionPercent: null == completionPercent ? _self.completionPercent : completionPercent // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}


/// @nodoc
mixin _$ProtocolWorkflowState {

 WorkflowStep get currentStep; ProtocolInfo? get selectedProtocolInfo; ProtocolDetails? get selectedProtocolDetails; Map<String, dynamic>? get configuredParameters; Map<String, String>? get assignedAssets; String? get deckLayoutName;@JsonKey(ignore: true) PlatformFile? get uploadedDeckFile;// Excluded from serialization
 Map<String, dynamic>? get preparedBackendConfig; ProtocolStatusResponse? get protocolStartResponse; bool get isLoading; String? get error; bool get isCurrentStepDataValid; double get parametersCompletionPercent; WorkflowStep? get navigationReturnTarget;
/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolWorkflowStateCopyWith<ProtocolWorkflowState> get copyWith => _$ProtocolWorkflowStateCopyWithImpl<ProtocolWorkflowState>(this as ProtocolWorkflowState, _$identity);

  /// Serializes this ProtocolWorkflowState to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolWorkflowState&&(identical(other.currentStep, currentStep) || other.currentStep == currentStep)&&(identical(other.selectedProtocolInfo, selectedProtocolInfo) || other.selectedProtocolInfo == selectedProtocolInfo)&&(identical(other.selectedProtocolDetails, selectedProtocolDetails) || other.selectedProtocolDetails == selectedProtocolDetails)&&const DeepCollectionEquality().equals(other.configuredParameters, configuredParameters)&&const DeepCollectionEquality().equals(other.assignedAssets, assignedAssets)&&(identical(other.deckLayoutName, deckLayoutName) || other.deckLayoutName == deckLayoutName)&&(identical(other.uploadedDeckFile, uploadedDeckFile) || other.uploadedDeckFile == uploadedDeckFile)&&const DeepCollectionEquality().equals(other.preparedBackendConfig, preparedBackendConfig)&&(identical(other.protocolStartResponse, protocolStartResponse) || other.protocolStartResponse == protocolStartResponse)&&(identical(other.isLoading, isLoading) || other.isLoading == isLoading)&&(identical(other.error, error) || other.error == error)&&(identical(other.isCurrentStepDataValid, isCurrentStepDataValid) || other.isCurrentStepDataValid == isCurrentStepDataValid)&&(identical(other.parametersCompletionPercent, parametersCompletionPercent) || other.parametersCompletionPercent == parametersCompletionPercent)&&(identical(other.navigationReturnTarget, navigationReturnTarget) || other.navigationReturnTarget == navigationReturnTarget));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,currentStep,selectedProtocolInfo,selectedProtocolDetails,const DeepCollectionEquality().hash(configuredParameters),const DeepCollectionEquality().hash(assignedAssets),deckLayoutName,uploadedDeckFile,const DeepCollectionEquality().hash(preparedBackendConfig),protocolStartResponse,isLoading,error,isCurrentStepDataValid,parametersCompletionPercent,navigationReturnTarget);

@override
String toString() {
  return 'ProtocolWorkflowState(currentStep: $currentStep, selectedProtocolInfo: $selectedProtocolInfo, selectedProtocolDetails: $selectedProtocolDetails, configuredParameters: $configuredParameters, assignedAssets: $assignedAssets, deckLayoutName: $deckLayoutName, uploadedDeckFile: $uploadedDeckFile, preparedBackendConfig: $preparedBackendConfig, protocolStartResponse: $protocolStartResponse, isLoading: $isLoading, error: $error, isCurrentStepDataValid: $isCurrentStepDataValid, parametersCompletionPercent: $parametersCompletionPercent, navigationReturnTarget: $navigationReturnTarget)';
}


}

/// @nodoc
abstract mixin class $ProtocolWorkflowStateCopyWith<$Res>  {
  factory $ProtocolWorkflowStateCopyWith(ProtocolWorkflowState value, $Res Function(ProtocolWorkflowState) _then) = _$ProtocolWorkflowStateCopyWithImpl;
@useResult
$Res call({
 WorkflowStep currentStep, ProtocolInfo? selectedProtocolInfo, ProtocolDetails? selectedProtocolDetails, Map<String, dynamic>? configuredParameters, Map<String, String>? assignedAssets, String? deckLayoutName,@JsonKey(ignore: true) PlatformFile? uploadedDeckFile, Map<String, dynamic>? preparedBackendConfig, ProtocolStatusResponse? protocolStartResponse, bool isLoading, String? error, bool isCurrentStepDataValid, double parametersCompletionPercent, WorkflowStep? navigationReturnTarget
});


$ProtocolInfoCopyWith<$Res>? get selectedProtocolInfo;$ProtocolDetailsCopyWith<$Res>? get selectedProtocolDetails;$ProtocolStatusResponseCopyWith<$Res>? get protocolStartResponse;

}
/// @nodoc
class _$ProtocolWorkflowStateCopyWithImpl<$Res>
    implements $ProtocolWorkflowStateCopyWith<$Res> {
  _$ProtocolWorkflowStateCopyWithImpl(this._self, this._then);

  final ProtocolWorkflowState _self;
  final $Res Function(ProtocolWorkflowState) _then;

/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? currentStep = null,Object? selectedProtocolInfo = freezed,Object? selectedProtocolDetails = freezed,Object? configuredParameters = freezed,Object? assignedAssets = freezed,Object? deckLayoutName = freezed,Object? uploadedDeckFile = freezed,Object? preparedBackendConfig = freezed,Object? protocolStartResponse = freezed,Object? isLoading = null,Object? error = freezed,Object? isCurrentStepDataValid = null,Object? parametersCompletionPercent = null,Object? navigationReturnTarget = freezed,}) {
  return _then(_self.copyWith(
currentStep: null == currentStep ? _self.currentStep : currentStep // ignore: cast_nullable_to_non_nullable
as WorkflowStep,selectedProtocolInfo: freezed == selectedProtocolInfo ? _self.selectedProtocolInfo : selectedProtocolInfo // ignore: cast_nullable_to_non_nullable
as ProtocolInfo?,selectedProtocolDetails: freezed == selectedProtocolDetails ? _self.selectedProtocolDetails : selectedProtocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails?,configuredParameters: freezed == configuredParameters ? _self.configuredParameters : configuredParameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,assignedAssets: freezed == assignedAssets ? _self.assignedAssets : assignedAssets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutName: freezed == deckLayoutName ? _self.deckLayoutName : deckLayoutName // ignore: cast_nullable_to_non_nullable
as String?,uploadedDeckFile: freezed == uploadedDeckFile ? _self.uploadedDeckFile : uploadedDeckFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,preparedBackendConfig: freezed == preparedBackendConfig ? _self.preparedBackendConfig : preparedBackendConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,protocolStartResponse: freezed == protocolStartResponse ? _self.protocolStartResponse : protocolStartResponse // ignore: cast_nullable_to_non_nullable
as ProtocolStatusResponse?,isLoading: null == isLoading ? _self.isLoading : isLoading // ignore: cast_nullable_to_non_nullable
as bool,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isCurrentStepDataValid: null == isCurrentStepDataValid ? _self.isCurrentStepDataValid : isCurrentStepDataValid // ignore: cast_nullable_to_non_nullable
as bool,parametersCompletionPercent: null == parametersCompletionPercent ? _self.parametersCompletionPercent : parametersCompletionPercent // ignore: cast_nullable_to_non_nullable
as double,navigationReturnTarget: freezed == navigationReturnTarget ? _self.navigationReturnTarget : navigationReturnTarget // ignore: cast_nullable_to_non_nullable
as WorkflowStep?,
  ));
}
/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res>? get selectedProtocolInfo {
    if (_self.selectedProtocolInfo == null) {
    return null;
  }

  return $ProtocolInfoCopyWith<$Res>(_self.selectedProtocolInfo!, (value) {
    return _then(_self.copyWith(selectedProtocolInfo: value));
  });
}/// Create a copy of ProtocolWorkflowState
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
}/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolStatusResponseCopyWith<$Res>? get protocolStartResponse {
    if (_self.protocolStartResponse == null) {
    return null;
  }

  return $ProtocolStatusResponseCopyWith<$Res>(_self.protocolStartResponse!, (value) {
    return _then(_self.copyWith(protocolStartResponse: value));
  });
}
}


/// @nodoc
@JsonSerializable()

class _ProtocolWorkflowState implements ProtocolWorkflowState {
  const _ProtocolWorkflowState({required this.currentStep, this.selectedProtocolInfo, this.selectedProtocolDetails, final  Map<String, dynamic>? configuredParameters, final  Map<String, String>? assignedAssets, this.deckLayoutName, @JsonKey(ignore: true) this.uploadedDeckFile, final  Map<String, dynamic>? preparedBackendConfig, this.protocolStartResponse, this.isLoading = false, this.error, this.isCurrentStepDataValid = false, this.parametersCompletionPercent = 0.0, this.navigationReturnTarget}): _configuredParameters = configuredParameters,_assignedAssets = assignedAssets,_preparedBackendConfig = preparedBackendConfig;
  factory _ProtocolWorkflowState.fromJson(Map<String, dynamic> json) => _$ProtocolWorkflowStateFromJson(json);

@override final  WorkflowStep currentStep;
@override final  ProtocolInfo? selectedProtocolInfo;
@override final  ProtocolDetails? selectedProtocolDetails;
 final  Map<String, dynamic>? _configuredParameters;
@override Map<String, dynamic>? get configuredParameters {
  final value = _configuredParameters;
  if (value == null) return null;
  if (_configuredParameters is EqualUnmodifiableMapView) return _configuredParameters;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, String>? _assignedAssets;
@override Map<String, String>? get assignedAssets {
  final value = _assignedAssets;
  if (value == null) return null;
  if (_assignedAssets is EqualUnmodifiableMapView) return _assignedAssets;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  String? deckLayoutName;
@override@JsonKey(ignore: true) final  PlatformFile? uploadedDeckFile;
// Excluded from serialization
 final  Map<String, dynamic>? _preparedBackendConfig;
// Excluded from serialization
@override Map<String, dynamic>? get preparedBackendConfig {
  final value = _preparedBackendConfig;
  if (value == null) return null;
  if (_preparedBackendConfig is EqualUnmodifiableMapView) return _preparedBackendConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override final  ProtocolStatusResponse? protocolStartResponse;
@override@JsonKey() final  bool isLoading;
@override final  String? error;
@override@JsonKey() final  bool isCurrentStepDataValid;
@override@JsonKey() final  double parametersCompletionPercent;
@override final  WorkflowStep? navigationReturnTarget;

/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ProtocolWorkflowStateCopyWith<_ProtocolWorkflowState> get copyWith => __$ProtocolWorkflowStateCopyWithImpl<_ProtocolWorkflowState>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ProtocolWorkflowStateToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ProtocolWorkflowState&&(identical(other.currentStep, currentStep) || other.currentStep == currentStep)&&(identical(other.selectedProtocolInfo, selectedProtocolInfo) || other.selectedProtocolInfo == selectedProtocolInfo)&&(identical(other.selectedProtocolDetails, selectedProtocolDetails) || other.selectedProtocolDetails == selectedProtocolDetails)&&const DeepCollectionEquality().equals(other._configuredParameters, _configuredParameters)&&const DeepCollectionEquality().equals(other._assignedAssets, _assignedAssets)&&(identical(other.deckLayoutName, deckLayoutName) || other.deckLayoutName == deckLayoutName)&&(identical(other.uploadedDeckFile, uploadedDeckFile) || other.uploadedDeckFile == uploadedDeckFile)&&const DeepCollectionEquality().equals(other._preparedBackendConfig, _preparedBackendConfig)&&(identical(other.protocolStartResponse, protocolStartResponse) || other.protocolStartResponse == protocolStartResponse)&&(identical(other.isLoading, isLoading) || other.isLoading == isLoading)&&(identical(other.error, error) || other.error == error)&&(identical(other.isCurrentStepDataValid, isCurrentStepDataValid) || other.isCurrentStepDataValid == isCurrentStepDataValid)&&(identical(other.parametersCompletionPercent, parametersCompletionPercent) || other.parametersCompletionPercent == parametersCompletionPercent)&&(identical(other.navigationReturnTarget, navigationReturnTarget) || other.navigationReturnTarget == navigationReturnTarget));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,currentStep,selectedProtocolInfo,selectedProtocolDetails,const DeepCollectionEquality().hash(_configuredParameters),const DeepCollectionEquality().hash(_assignedAssets),deckLayoutName,uploadedDeckFile,const DeepCollectionEquality().hash(_preparedBackendConfig),protocolStartResponse,isLoading,error,isCurrentStepDataValid,parametersCompletionPercent,navigationReturnTarget);

@override
String toString() {
  return 'ProtocolWorkflowState(currentStep: $currentStep, selectedProtocolInfo: $selectedProtocolInfo, selectedProtocolDetails: $selectedProtocolDetails, configuredParameters: $configuredParameters, assignedAssets: $assignedAssets, deckLayoutName: $deckLayoutName, uploadedDeckFile: $uploadedDeckFile, preparedBackendConfig: $preparedBackendConfig, protocolStartResponse: $protocolStartResponse, isLoading: $isLoading, error: $error, isCurrentStepDataValid: $isCurrentStepDataValid, parametersCompletionPercent: $parametersCompletionPercent, navigationReturnTarget: $navigationReturnTarget)';
}


}

/// @nodoc
abstract mixin class _$ProtocolWorkflowStateCopyWith<$Res> implements $ProtocolWorkflowStateCopyWith<$Res> {
  factory _$ProtocolWorkflowStateCopyWith(_ProtocolWorkflowState value, $Res Function(_ProtocolWorkflowState) _then) = __$ProtocolWorkflowStateCopyWithImpl;
@override @useResult
$Res call({
 WorkflowStep currentStep, ProtocolInfo? selectedProtocolInfo, ProtocolDetails? selectedProtocolDetails, Map<String, dynamic>? configuredParameters, Map<String, String>? assignedAssets, String? deckLayoutName,@JsonKey(ignore: true) PlatformFile? uploadedDeckFile, Map<String, dynamic>? preparedBackendConfig, ProtocolStatusResponse? protocolStartResponse, bool isLoading, String? error, bool isCurrentStepDataValid, double parametersCompletionPercent, WorkflowStep? navigationReturnTarget
});


@override $ProtocolInfoCopyWith<$Res>? get selectedProtocolInfo;@override $ProtocolDetailsCopyWith<$Res>? get selectedProtocolDetails;@override $ProtocolStatusResponseCopyWith<$Res>? get protocolStartResponse;

}
/// @nodoc
class __$ProtocolWorkflowStateCopyWithImpl<$Res>
    implements _$ProtocolWorkflowStateCopyWith<$Res> {
  __$ProtocolWorkflowStateCopyWithImpl(this._self, this._then);

  final _ProtocolWorkflowState _self;
  final $Res Function(_ProtocolWorkflowState) _then;

/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? currentStep = null,Object? selectedProtocolInfo = freezed,Object? selectedProtocolDetails = freezed,Object? configuredParameters = freezed,Object? assignedAssets = freezed,Object? deckLayoutName = freezed,Object? uploadedDeckFile = freezed,Object? preparedBackendConfig = freezed,Object? protocolStartResponse = freezed,Object? isLoading = null,Object? error = freezed,Object? isCurrentStepDataValid = null,Object? parametersCompletionPercent = null,Object? navigationReturnTarget = freezed,}) {
  return _then(_ProtocolWorkflowState(
currentStep: null == currentStep ? _self.currentStep : currentStep // ignore: cast_nullable_to_non_nullable
as WorkflowStep,selectedProtocolInfo: freezed == selectedProtocolInfo ? _self.selectedProtocolInfo : selectedProtocolInfo // ignore: cast_nullable_to_non_nullable
as ProtocolInfo?,selectedProtocolDetails: freezed == selectedProtocolDetails ? _self.selectedProtocolDetails : selectedProtocolDetails // ignore: cast_nullable_to_non_nullable
as ProtocolDetails?,configuredParameters: freezed == configuredParameters ? _self._configuredParameters : configuredParameters // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,assignedAssets: freezed == assignedAssets ? _self._assignedAssets : assignedAssets // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,deckLayoutName: freezed == deckLayoutName ? _self.deckLayoutName : deckLayoutName // ignore: cast_nullable_to_non_nullable
as String?,uploadedDeckFile: freezed == uploadedDeckFile ? _self.uploadedDeckFile : uploadedDeckFile // ignore: cast_nullable_to_non_nullable
as PlatformFile?,preparedBackendConfig: freezed == preparedBackendConfig ? _self._preparedBackendConfig : preparedBackendConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,protocolStartResponse: freezed == protocolStartResponse ? _self.protocolStartResponse : protocolStartResponse // ignore: cast_nullable_to_non_nullable
as ProtocolStatusResponse?,isLoading: null == isLoading ? _self.isLoading : isLoading // ignore: cast_nullable_to_non_nullable
as bool,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,isCurrentStepDataValid: null == isCurrentStepDataValid ? _self.isCurrentStepDataValid : isCurrentStepDataValid // ignore: cast_nullable_to_non_nullable
as bool,parametersCompletionPercent: null == parametersCompletionPercent ? _self.parametersCompletionPercent : parametersCompletionPercent // ignore: cast_nullable_to_non_nullable
as double,navigationReturnTarget: freezed == navigationReturnTarget ? _self.navigationReturnTarget : navigationReturnTarget // ignore: cast_nullable_to_non_nullable
as WorkflowStep?,
  ));
}

/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolInfoCopyWith<$Res>? get selectedProtocolInfo {
    if (_self.selectedProtocolInfo == null) {
    return null;
  }

  return $ProtocolInfoCopyWith<$Res>(_self.selectedProtocolInfo!, (value) {
    return _then(_self.copyWith(selectedProtocolInfo: value));
  });
}/// Create a copy of ProtocolWorkflowState
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
}/// Create a copy of ProtocolWorkflowState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ProtocolStatusResponseCopyWith<$Res>? get protocolStartResponse {
    if (_self.protocolStartResponse == null) {
    return null;
  }

  return $ProtocolStatusResponseCopyWith<$Res>(_self.protocolStartResponse!, (value) {
    return _then(_self.copyWith(protocolStartResponse: value));
  });
}
}

// dart format on
