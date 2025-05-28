import 'package:mockito/annotations.dart';
import 'package:praxis_lab_management/src/data/services/asset_api_service.dart';
import 'package:praxis_lab_management/src/data/services/workcell_api_service.dart';

// Add other services here as needed for mocking across tests
@GenerateMocks([AssetApiService, WorkcellApiService])
void main() {} // Dummy main function to trigger build_runner for this file.
