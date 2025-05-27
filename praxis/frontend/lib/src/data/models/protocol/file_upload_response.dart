// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may
// obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:freezed_annotation/freezed_annotation.dart';

part 'file_upload_response.freezed.dart';
part 'file_upload_response.g.dart';

@freezed
class FileUploadResponse with _$FileUploadResponse {
  const factory FileUploadResponse({
    required String filename,
    required String path,
  }) = _FileUploadResponse;

  factory FileUploadResponse.fromJson(Map<String, dynamic> json) =>
      _$FileUploadResponseFromJson(json);
}
