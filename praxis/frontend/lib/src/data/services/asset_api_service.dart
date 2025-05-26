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

import 'package:praxis_data/praxis_data.dart';

import 'dio_client.dart';

/// Abstract class for asset API services.
abstract class AssetApiService {
  /// Devices (Instruments)
  Future<List<ManagedDeviceOrm>> getDevices();
  Future<ManagedDeviceOrm> createDevice(ManagedDeviceOrm device);
  Future<ManagedDeviceOrm> getDeviceById(String deviceId);
  Future<ManagedDeviceOrm> updateDevice(String deviceId, ManagedDeviceOrm device);
  Future<void> deleteDevice(String deviceId);
  Future<void> connectDevice(String deviceId);
  Future<void> initializeDevice(String deviceId);
  Future<void> disconnectDevice(String deviceId);

  /// Labware Definitions (Labware Types)
  Future<List<LabwareDefinitionCatalogOrm>> getLabwareDefinitions();
  Future<LabwareDefinitionCatalogOrm> createLabwareDefinition(
      LabwareDefinitionCatalogOrm labwareDefinition);
  Future<LabwareDefinitionCatalogOrm> updateLabwareDefinition(
      String labwareDefinitionId, LabwareDefinitionCatalogOrm labwareDefinition);
  Future<void> deleteLabwareDefinition(String labwareDefinitionId);

  /// Labware Instances (Physical Labware Items)
  Future<List<LabwareInstanceOrm>> getLabwareInstances();
  Future<LabwareInstanceOrm> createLabwareInstance(
      LabwareInstanceOrm labwareInstance);
  Future<LabwareInstanceOrm> getLabwareInstanceById(String instanceId);
  Future<LabwareInstanceOrm> updateLabwareInstance(
      String instanceId, LabwareInstanceOrm labwareInstance);
  Future<void> deleteLabwareInstance(String instanceId);

  /// Deck Layouts
  Future<List<DeckLayoutOrm>> getDeckLayouts();
  Future<DeckLayoutOrm> createDeckLayout(DeckLayoutOrm deckLayout);
  Future<DeckLayoutOrm> getDeckLayoutById(String deckLayoutId);
  Future<DeckLayoutOrm> updateDeckLayout(
      String deckLayoutId, DeckLayoutOrm deckLayout);
  Future<void> deleteDeckLayout(String deckLayoutId);
}

/// Implementation of [AssetApiService] using Dio.
class AssetApiServiceImpl extends AssetApiService {
  final DioClient _dioClient;

  /// Constructor for [AssetApiServiceImpl].
  AssetApiServiceImpl(this._dioClient);

  /// Devices (Instruments)
  @override
  Future<List<ManagedDeviceOrm>> getDevices() async {
    // TODO(user): Implement actual API call
    return Future.value([]);
  }

  @override
  Future<ManagedDeviceOrm> createDevice(ManagedDeviceOrm device) async {
    // TODO(user): Implement actual API call
    return Future.value(device);
  }

  @override
  Future<ManagedDeviceOrm> getDeviceById(String deviceId) async {
    // TODO(user): Implement actual API call
    return Future.value(ManagedDeviceOrm());
  }

  @override
  Future<ManagedDeviceOrm> updateDevice(
      String deviceId, ManagedDeviceOrm device) async {
    // TODO(user): Implement actual API call
    return Future.value(device);
  }

  @override
  Future<void> deleteDevice(String deviceId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }

  @override
  Future<void> connectDevice(String deviceId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }

  @override
  Future<void> initializeDevice(String deviceId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }

  @override
  Future<void> disconnectDevice(String deviceId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }

  /// Labware Definitions (Labware Types)
  @override
  Future<List<LabwareDefinitionCatalogOrm>> getLabwareDefinitions() async {
    // TODO(user): Implement actual API call
    return Future.value([]);
  }

  @override
  Future<LabwareDefinitionCatalogOrm> createLabwareDefinition(
      LabwareDefinitionCatalogOrm labwareDefinition) async {
    // TODO(user): Implement actual API call
    return Future.value(labwareDefinition);
  }

  @override
  Future<LabwareDefinitionCatalogOrm> updateLabwareDefinition(
      String labwareDefinitionId,
      LabwareDefinitionCatalogOrm labwareDefinition) async {
    // TODO(user): Implement actual API call
    return Future.value(labwareDefinition);
  }

  @override
  Future<void> deleteLabwareDefinition(String labwareDefinitionId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }

  /// Labware Instances (Physical Labware Items)
  @override
  Future<List<LabwareInstanceOrm>> getLabwareInstances() async {
    // TODO(user): Implement actual API call
    return Future.value([]);
  }

  @override
  Future<LabwareInstanceOrm> createLabwareInstance(
      LabwareInstanceOrm labwareInstance) async {
    // TODO(user): Implement actual API call
    return Future.value(labwareInstance);
  }

  @override
  Future<LabwareInstanceOrm> getLabwareInstanceById(String instanceId) async {
    // TODO(user): Implement actual API call
    return Future.value(LabwareInstanceOrm());
  }

  @override
  Future<LabwareInstanceOrm> updateLabwareInstance(
      String instanceId, LabwareInstanceOrm labwareInstance) async {
    // TODO(user): Implement actual API call
    return Future.value(labwareInstance);
  }

  @override
  Future<void> deleteLabwareInstance(String instanceId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }

  /// Deck Layouts
  @override
  Future<List<DeckLayoutOrm>> getDeckLayouts() async {
    // TODO(user): Implement actual API call
    return Future.value([]);
  }

  @override
  Future<DeckLayoutOrm> createDeckLayout(DeckLayoutOrm deckLayout) async {
    // TODO(user): Implement actual API call
    return Future.value(deckLayout);
  }

  @override
  Future<DeckLayoutOrm> getDeckLayoutById(String deckLayoutId) async {
    // TODO(user): Implement actual API call
    return Future.value(DeckLayoutOrm());
  }

  @override
  Future<DeckLayoutOrm> updateDeckLayout(
      String deckLayoutId, DeckLayoutOrm deckLayout) async {
    // TODO(user): Implement actual API call
    return Future.value(deckLayout);
  }

  @override
  Future<void> deleteDeckLayout(String deckLayoutId) async {
    // TODO(user): Implement actual API call
    return Future.value();
  }
}
