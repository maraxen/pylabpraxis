// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'package:mockito/annotations.dart';
import 'package:pylabpraxis_flutter/src/data/services/asset_api_service.dart';
import 'package:pylabpraxis_flutter/src/data/services/workcell_api_service.dart';

// Add other services here as needed for mocking across tests
@GenerateMocks([
  AssetApiService,
  WorkcellApiService,
])
void main() {} // Dummy main function to trigger build_runner for this file.
