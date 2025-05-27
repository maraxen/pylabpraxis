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

import 'dart:convert';

// Corresponds to DeckConfigurationSlotItemOrm in backend
class DeckConfigurationSlotItemOrm {
  final int? id;
  final int deckConfigurationId;
  final String slotName;
  final int labwareInstanceId; // FK to LabwareInstanceOrm.id
  final String? expectedLabwareDefinitionName; // FK to LabwareDefinitionCatalogOrm.pylabrobot_definition_name

  DeckConfigurationSlotItemOrm({
    this.id,
    required this.deckConfigurationId,
    required this.slotName,
    required this.labwareInstanceId,
    this.expectedLabwareDefinitionName,
  });

  factory DeckConfigurationSlotItemOrm.fromJson(Map<String, dynamic> json) {
    return DeckConfigurationSlotItemOrm(
      id: json['id'] as int?,
      deckConfigurationId: json['deck_configuration_id'] as int,
      slotName: json['slot_name'] as String,
      labwareInstanceId: json['labware_instance_id'] as int,
      expectedLabwareDefinitionName: json['expected_labware_definition_name'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'deck_configuration_id': deckConfigurationId,
      'slot_name': slotName,
      'labware_instance_id': labwareInstanceId,
      'expected_labware_definition_name': expectedLabwareDefinitionName,
    };
  }
}

// Corresponds to DeckConfigurationOrm in backend
class DeckLayoutOrm {
  final int? id; // praxis_deck_config_id
  final String layoutName;
  final int deckDeviceId; // FK to ManagedDeviceOrm.id (the deck device itself)
  final String? description;
  final List<DeckConfigurationSlotItemOrm>? slotItems;
  final String? createdAt; // DateTime as String
  final String? updatedAt; // DateTime as String
  // workspaceId is required by the frontend's praxis_data DeckLayoutOrm, but not in backend ORM.
  // Adding it here to satisfy the interface.
  final String workspaceId;


  DeckLayoutOrm({
    this.id,
    required this.layoutName,
    required this.deckDeviceId,
    this.description,
    this.slotItems,
    this.createdAt,
    this.updatedAt,
    required this.workspaceId,
  });

  factory DeckLayoutOrm.fromJson(Map<String, dynamic> json) {
    var itemsList = json['slot_items'] as List<dynamic>?;
    List<DeckConfigurationSlotItemOrm>? slotItems;
    if (itemsList != null) {
      slotItems = itemsList
          .map((i) => DeckConfigurationSlotItemOrm.fromJson(i as Map<String, dynamic>))
          .toList();
    }

    return DeckLayoutOrm(
      id: json['id'] as int?,
      layoutName: json['layout_name'] as String,
      deckDeviceId: json['deck_device_id'] as int,
      description: json['description'] as String?,
      slotItems: slotItems,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
      workspaceId: json['workspace_id'] as String? ?? json['workspaceId'] as String? ?? '', // Ensure workspaceId is present
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'layout_name': layoutName,
      'deck_device_id': deckDeviceId,
      'description': description,
      'slot_items': slotItems?.map((item) => item.toJson()).toList(),
      'workspace_id': workspaceId,
      // 'created_at' and 'updated_at' are typically handled by the server
    };
  }
}
