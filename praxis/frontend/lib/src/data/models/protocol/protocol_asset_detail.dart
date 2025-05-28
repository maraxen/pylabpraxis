import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_asset_detail.freezed.dart';
part 'protocol_asset_detail.g.dart';

@freezed
sealed class ProtocolAssetDetail with _$ProtocolAssetDetail {
  const factory ProtocolAssetDetail({
    required String name,
    required String type,
    String? description,
    required bool required,
  }) = _ProtocolAssetDetail;

  factory ProtocolAssetDetail.fromJson(Map<String, dynamic> json) =>
      _$ProtocolAssetDetailFromJson(json);
}
