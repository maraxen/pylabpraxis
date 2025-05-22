// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'protocol_review_bloc.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;
/// @nodoc
mixin _$ProtocolReviewEvent {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolReviewEvent);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolReviewEvent()';
}


}

/// @nodoc
class $ProtocolReviewEventCopyWith<$Res>  {
$ProtocolReviewEventCopyWith(ProtocolReviewEvent _, $Res Function(ProtocolReviewEvent) __);
}


/// @nodoc


class LoadReviewData implements ProtocolReviewEvent {
  const LoadReviewData({required this.reviewData});
  

 final  ReviewDataBundle reviewData;

/// Create a copy of ProtocolReviewEvent
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LoadReviewDataCopyWith<LoadReviewData> get copyWith => _$LoadReviewDataCopyWithImpl<LoadReviewData>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LoadReviewData&&(identical(other.reviewData, reviewData) || other.reviewData == reviewData));
}


@override
int get hashCode => Object.hash(runtimeType,reviewData);

@override
String toString() {
  return 'ProtocolReviewEvent.loadReviewData(reviewData: $reviewData)';
}


}

/// @nodoc
abstract mixin class $LoadReviewDataCopyWith<$Res> implements $ProtocolReviewEventCopyWith<$Res> {
  factory $LoadReviewDataCopyWith(LoadReviewData value, $Res Function(LoadReviewData) _then) = _$LoadReviewDataCopyWithImpl;
@useResult
$Res call({
 ReviewDataBundle reviewData
});


$ReviewDataBundleCopyWith<$Res> get reviewData;

}
/// @nodoc
class _$LoadReviewDataCopyWithImpl<$Res>
    implements $LoadReviewDataCopyWith<$Res> {
  _$LoadReviewDataCopyWithImpl(this._self, this._then);

  final LoadReviewData _self;
  final $Res Function(LoadReviewData) _then;

/// Create a copy of ProtocolReviewEvent
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? reviewData = null,}) {
  return _then(LoadReviewData(
reviewData: null == reviewData ? _self.reviewData : reviewData // ignore: cast_nullable_to_non_nullable
as ReviewDataBundle,
  ));
}

/// Create a copy of ProtocolReviewEvent
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReviewDataBundleCopyWith<$Res> get reviewData {
  
  return $ReviewDataBundleCopyWith<$Res>(_self.reviewData, (value) {
    return _then(_self.copyWith(reviewData: value));
  });
}
}

/// @nodoc


class PrepareProtocolRequested implements ProtocolReviewEvent {
  const PrepareProtocolRequested();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PrepareProtocolRequested);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolReviewEvent.prepareProtocolRequested()';
}


}




/// @nodoc


class ResetReview implements ProtocolReviewEvent {
  const ResetReview();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ResetReview);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolReviewEvent.resetReview()';
}


}




/// @nodoc
mixin _$ProtocolReviewState {





@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolReviewState);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolReviewState()';
}


}

/// @nodoc
class $ProtocolReviewStateCopyWith<$Res>  {
$ProtocolReviewStateCopyWith(ProtocolReviewState _, $Res Function(ProtocolReviewState) __);
}


/// @nodoc


class ProtocolReviewInitial implements ProtocolReviewState {
  const ProtocolReviewInitial();
  






@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolReviewInitial);
}


@override
int get hashCode => runtimeType.hashCode;

@override
String toString() {
  return 'ProtocolReviewState.initial()';
}


}




/// @nodoc


class ProtocolReviewReady implements ProtocolReviewState {
  const ProtocolReviewReady({required this.displayData});
  

 final  ReviewDataBundle displayData;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolReviewReadyCopyWith<ProtocolReviewReady> get copyWith => _$ProtocolReviewReadyCopyWithImpl<ProtocolReviewReady>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolReviewReady&&(identical(other.displayData, displayData) || other.displayData == displayData));
}


@override
int get hashCode => Object.hash(runtimeType,displayData);

@override
String toString() {
  return 'ProtocolReviewState.ready(displayData: $displayData)';
}


}

/// @nodoc
abstract mixin class $ProtocolReviewReadyCopyWith<$Res> implements $ProtocolReviewStateCopyWith<$Res> {
  factory $ProtocolReviewReadyCopyWith(ProtocolReviewReady value, $Res Function(ProtocolReviewReady) _then) = _$ProtocolReviewReadyCopyWithImpl;
@useResult
$Res call({
 ReviewDataBundle displayData
});


$ReviewDataBundleCopyWith<$Res> get displayData;

}
/// @nodoc
class _$ProtocolReviewReadyCopyWithImpl<$Res>
    implements $ProtocolReviewReadyCopyWith<$Res> {
  _$ProtocolReviewReadyCopyWithImpl(this._self, this._then);

  final ProtocolReviewReady _self;
  final $Res Function(ProtocolReviewReady) _then;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? displayData = null,}) {
  return _then(ProtocolReviewReady(
displayData: null == displayData ? _self.displayData : displayData // ignore: cast_nullable_to_non_nullable
as ReviewDataBundle,
  ));
}

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReviewDataBundleCopyWith<$Res> get displayData {
  
  return $ReviewDataBundleCopyWith<$Res>(_self.displayData, (value) {
    return _then(_self.copyWith(displayData: value));
  });
}
}

/// @nodoc


class ProtocolPreparationInProgress implements ProtocolReviewState {
  const ProtocolPreparationInProgress({required this.reviewData});
  

 final  ReviewDataBundle reviewData;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPreparationInProgressCopyWith<ProtocolPreparationInProgress> get copyWith => _$ProtocolPreparationInProgressCopyWithImpl<ProtocolPreparationInProgress>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPreparationInProgress&&(identical(other.reviewData, reviewData) || other.reviewData == reviewData));
}


@override
int get hashCode => Object.hash(runtimeType,reviewData);

@override
String toString() {
  return 'ProtocolReviewState.preparationInProgress(reviewData: $reviewData)';
}


}

/// @nodoc
abstract mixin class $ProtocolPreparationInProgressCopyWith<$Res> implements $ProtocolReviewStateCopyWith<$Res> {
  factory $ProtocolPreparationInProgressCopyWith(ProtocolPreparationInProgress value, $Res Function(ProtocolPreparationInProgress) _then) = _$ProtocolPreparationInProgressCopyWithImpl;
@useResult
$Res call({
 ReviewDataBundle reviewData
});


$ReviewDataBundleCopyWith<$Res> get reviewData;

}
/// @nodoc
class _$ProtocolPreparationInProgressCopyWithImpl<$Res>
    implements $ProtocolPreparationInProgressCopyWith<$Res> {
  _$ProtocolPreparationInProgressCopyWithImpl(this._self, this._then);

  final ProtocolPreparationInProgress _self;
  final $Res Function(ProtocolPreparationInProgress) _then;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? reviewData = null,}) {
  return _then(ProtocolPreparationInProgress(
reviewData: null == reviewData ? _self.reviewData : reviewData // ignore: cast_nullable_to_non_nullable
as ReviewDataBundle,
  ));
}

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReviewDataBundleCopyWith<$Res> get reviewData {
  
  return $ReviewDataBundleCopyWith<$Res>(_self.reviewData, (value) {
    return _then(_self.copyWith(reviewData: value));
  });
}
}

/// @nodoc


class ProtocolPreparationSuccess implements ProtocolReviewState {
  const ProtocolPreparationSuccess({required final  Map<String, dynamic> preparedConfig, required this.reviewedData}): _preparedConfig = preparedConfig;
  

 final  Map<String, dynamic> _preparedConfig;
 Map<String, dynamic> get preparedConfig {
  if (_preparedConfig is EqualUnmodifiableMapView) return _preparedConfig;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_preparedConfig);
}

 final  ReviewDataBundle reviewedData;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPreparationSuccessCopyWith<ProtocolPreparationSuccess> get copyWith => _$ProtocolPreparationSuccessCopyWithImpl<ProtocolPreparationSuccess>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPreparationSuccess&&const DeepCollectionEquality().equals(other._preparedConfig, _preparedConfig)&&(identical(other.reviewedData, reviewedData) || other.reviewedData == reviewedData));
}


@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(_preparedConfig),reviewedData);

@override
String toString() {
  return 'ProtocolReviewState.preparationSuccess(preparedConfig: $preparedConfig, reviewedData: $reviewedData)';
}


}

/// @nodoc
abstract mixin class $ProtocolPreparationSuccessCopyWith<$Res> implements $ProtocolReviewStateCopyWith<$Res> {
  factory $ProtocolPreparationSuccessCopyWith(ProtocolPreparationSuccess value, $Res Function(ProtocolPreparationSuccess) _then) = _$ProtocolPreparationSuccessCopyWithImpl;
@useResult
$Res call({
 Map<String, dynamic> preparedConfig, ReviewDataBundle reviewedData
});


$ReviewDataBundleCopyWith<$Res> get reviewedData;

}
/// @nodoc
class _$ProtocolPreparationSuccessCopyWithImpl<$Res>
    implements $ProtocolPreparationSuccessCopyWith<$Res> {
  _$ProtocolPreparationSuccessCopyWithImpl(this._self, this._then);

  final ProtocolPreparationSuccess _self;
  final $Res Function(ProtocolPreparationSuccess) _then;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? preparedConfig = null,Object? reviewedData = null,}) {
  return _then(ProtocolPreparationSuccess(
preparedConfig: null == preparedConfig ? _self._preparedConfig : preparedConfig // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,reviewedData: null == reviewedData ? _self.reviewedData : reviewedData // ignore: cast_nullable_to_non_nullable
as ReviewDataBundle,
  ));
}

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReviewDataBundleCopyWith<$Res> get reviewedData {
  
  return $ReviewDataBundleCopyWith<$Res>(_self.reviewedData, (value) {
    return _then(_self.copyWith(reviewedData: value));
  });
}
}

/// @nodoc


class ProtocolPreparationFailure implements ProtocolReviewState {
  const ProtocolPreparationFailure({required this.error, required this.displayData});
  

 final  String error;
 final  ReviewDataBundle? displayData;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ProtocolPreparationFailureCopyWith<ProtocolPreparationFailure> get copyWith => _$ProtocolPreparationFailureCopyWithImpl<ProtocolPreparationFailure>(this, _$identity);



@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ProtocolPreparationFailure&&(identical(other.error, error) || other.error == error)&&(identical(other.displayData, displayData) || other.displayData == displayData));
}


@override
int get hashCode => Object.hash(runtimeType,error,displayData);

@override
String toString() {
  return 'ProtocolReviewState.preparationFailure(error: $error, displayData: $displayData)';
}


}

/// @nodoc
abstract mixin class $ProtocolPreparationFailureCopyWith<$Res> implements $ProtocolReviewStateCopyWith<$Res> {
  factory $ProtocolPreparationFailureCopyWith(ProtocolPreparationFailure value, $Res Function(ProtocolPreparationFailure) _then) = _$ProtocolPreparationFailureCopyWithImpl;
@useResult
$Res call({
 String error, ReviewDataBundle? displayData
});


$ReviewDataBundleCopyWith<$Res>? get displayData;

}
/// @nodoc
class _$ProtocolPreparationFailureCopyWithImpl<$Res>
    implements $ProtocolPreparationFailureCopyWith<$Res> {
  _$ProtocolPreparationFailureCopyWithImpl(this._self, this._then);

  final ProtocolPreparationFailure _self;
  final $Res Function(ProtocolPreparationFailure) _then;

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') $Res call({Object? error = null,Object? displayData = freezed,}) {
  return _then(ProtocolPreparationFailure(
error: null == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String,displayData: freezed == displayData ? _self.displayData : displayData // ignore: cast_nullable_to_non_nullable
as ReviewDataBundle?,
  ));
}

/// Create a copy of ProtocolReviewState
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReviewDataBundleCopyWith<$Res>? get displayData {
    if (_self.displayData == null) {
    return null;
  }

  return $ReviewDataBundleCopyWith<$Res>(_self.displayData!, (value) {
    return _then(_self.copyWith(displayData: value));
  });
}
}

// dart format on
