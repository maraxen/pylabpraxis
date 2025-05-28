import 'package:freezed_annotation/freezed_annotation.dart';

part 'run_command_response.freezed.dart';
part 'run_command_response.g.dart';

@freezed
sealed class RunCommandResponse with _$RunCommandResponse {
  const factory RunCommandResponse({required String message}) =
      _RunCommandResponse;

  factory RunCommandResponse.fromJson(Map<String, dynamic> json) =>
      _$RunCommandResponseFromJson(json);
}
