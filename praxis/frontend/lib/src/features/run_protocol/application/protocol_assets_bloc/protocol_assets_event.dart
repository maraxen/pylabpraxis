part of 'protocol_assets_bloc.dart';

@freezed
sealed class ProtocolAssetsEvent with _$ProtocolAssetsEvent {
  const factory ProtocolAssetsEvent.loadRequested() =
      LoadRequested; // Or your specific load event
  const factory ProtocolAssetsEvent.loadRequiredAssets({
    required List<ProtocolAsset> assetsFromProtocolDetails,
    Map<String, String>? existingAssignments, // Added for editing
  }) = LoadRequiredAssets;

  const factory ProtocolAssetsEvent.assetAssignmentChanged({
    required String assetName,
    required String assignedValue,
  }) = AssetAssignmentChanged;
}
