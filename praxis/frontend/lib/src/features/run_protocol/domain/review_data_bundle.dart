import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:file_picker/file_picker.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_info.dart';
import 'package:praxis_lab_management/src/data/models/protocol/protocol_details.dart'; // Added for completeness

part 'review_data_bundle.freezed.dart';

@freezed
abstract class ReviewDataBundle with _$ReviewDataBundle {
  const factory ReviewDataBundle({
    required ProtocolInfo selectedProtocolInfo,

    /// Optional: Including full details might be useful for display on review screen
    /// if ProtocolInfo doesn't have everything (e.g. full description, author).
    ProtocolDetails? selectedProtocolDetails,
    required Map<String, dynamic> configuredParameters,
    required Map<String, String> assignedAssets,
    String? deckLayoutName,
    PlatformFile? uploadedDeckFile,
  }) = _ReviewDataBundle;
}
