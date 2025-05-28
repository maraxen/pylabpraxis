import 'package:freezed_annotation/freezed_annotation.dart';

part 'file_upload_response.freezed.dart';
part 'file_upload_response.g.dart';

@freezed
sealed class FileUploadResponse with _$FileUploadResponse {
  const factory FileUploadResponse({
    required String filename,
    required String path,
  }) = _FileUploadResponse;

  factory FileUploadResponse.fromJson(Map<String, dynamic> json) =>
      _$FileUploadResponseFromJson(json);
}
