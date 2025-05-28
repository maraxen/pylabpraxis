import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_parameter_detail.freezed.dart';
part 'protocol_parameter_detail.g.dart';

@freezed
sealed class ProtocolParameterDetail with _$ProtocolParameterDetail {
  const factory ProtocolParameterDetail({
    required String paramType,
    required bool isRequired,
    @JsonKey(name: 'default') dynamic defaultValue,
    String? description,
    Map<String, dynamic>? constraints,
    String? displayName,
    String? unit,
  }) = _ProtocolParameterDetail;

  factory ProtocolParameterDetail.fromJson(Map<String, dynamic> json) =>
      _$ProtocolParameterDetailFromJson(json);
}
