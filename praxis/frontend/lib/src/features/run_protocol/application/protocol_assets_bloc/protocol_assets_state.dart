part of 'protocol_assets_bloc.dart';

@freezed
sealed class ProtocolAssetsState with _$ProtocolAssetsState {
  /// Initial state before assets are loaded or processed.
  const factory ProtocolAssetsState.initial() = ProtocolAssetsInitial;

  /// State indicating that assets have been loaded and are ready for assignment.
  ///
  /// [requiredAssets] is the list of all assets required by the protocol.
  /// [currentAssignments] is a map where keys are asset names and values are
  /// the user-assigned IDs/names.
  /// [isValid] indicates if all required assets have been assigned.
  const factory ProtocolAssetsState.loaded({
    required List<ProtocolAsset> requiredAssets,
    required Map<String, String> currentAssignments,
    @Default(false) bool isValid,
  }) = ProtocolAssetsLoaded;

  /// State indicating an error occurred.
  const factory ProtocolAssetsState.error({required String message}) =
      ProtocolAssetsError;
}
