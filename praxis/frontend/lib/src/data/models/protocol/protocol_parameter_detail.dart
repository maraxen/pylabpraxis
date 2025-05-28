import 'package:freezed_annotation/freezed_annotation.dart';

part 'protocol_parameter_detail.freezed.dart';
part 'protocol_parameter_detail.g.dart';

@freezed
@JsonSerializable()
sealed class ProtocolParameterDetail with _$ProtocolParameterDetail {
  const factory ProtocolParameterDetail({
    required String paramType,
    required bool isRequired,
    dynamic defaultValue, // 'default' is a reserved keyword in Dart
    String? description,
    Map<String, dynamic>? constraints,
  }) = _ProtocolParameterDetail;

  factory ProtocolParameterDetail.fromJson(Map<String, dynamic> json) {
    // Handle 'default' keyword conflict
    final Map<String, dynamic> updatedJson = Map.from(json);
    if (json.containsKey('default')) {
      updatedJson['defaultValue'] = json['default'];
      updatedJson.remove('default');
    }
    return _$ProtocolParameterDetailFromJson(updatedJson);
  }
}
