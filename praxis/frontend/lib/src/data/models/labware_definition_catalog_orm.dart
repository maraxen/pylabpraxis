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

class LabwareDefinitionCatalogOrm {
  final String pylabrobotDefinitionName;
  final String pythonFqn;
  final double? sizeXmm;
  final double? sizeYmm;
  final double? sizeZmm;
  final String? plrCategory;
  final String? model;
  final Map<String, dynamic>? rotationJson;
  final String? praxisLabwareTypeName;
  final String? description;
  final bool? isConsumable;
  final double? nominalVolumeUl;
  final String? material;
  final String? manufacturer;
  final Map<String, dynamic>? plrDefinitionDetailsJson;
  final String? createdAt; // DateTime as String
  final String? updatedAt; // DateTime as String

  LabwareDefinitionCatalogOrm({
    required this.pylabrobotDefinitionName,
    required this.pythonFqn,
    this.sizeXmm,
    this.sizeYmm,
    this.sizeZmm,
    this.plrCategory,
    this.model,
    this.rotationJson,
    this.praxisLabwareTypeName,
    this.description,
    this.isConsumable,
    this.nominalVolumeUl,
    this.material,
    this.manufacturer,
    this.plrDefinitionDetailsJson,
    this.createdAt,
    this.updatedAt,
  });

  factory LabwareDefinitionCatalogOrm.fromJson(Map<String, dynamic> json) {
    return LabwareDefinitionCatalogOrm(
      pylabrobotDefinitionName: json['pylabrobot_definition_name'] as String,
      pythonFqn: json['python_fqn'] as String,
      sizeXmm: (json['size_x_mm'] as num?)?.toDouble(),
      sizeYmm: (json['size_y_mm'] as num?)?.toDouble(),
      sizeZmm: (json['size_z_mm'] as num?)?.toDouble(),
      plrCategory: json['plr_category'] as String?,
      model: json['model'] as String?,
      rotationJson: json['rotation_json'] != null
          ? json['rotation_json'] as Map<String, dynamic>
          : null,
      praxisLabwareTypeName: json['praxis_labware_type_name'] as String?,
      description: json['description'] as String?,
      isConsumable: json['is_consumable'] as bool?,
      nominalVolumeUl: (json['nominal_volume_ul'] as num?)?.toDouble(),
      material: json['material'] as String?,
      manufacturer: json['manufacturer'] as String?,
      plrDefinitionDetailsJson: json['plr_definition_details_json'] != null
          ? json['plr_definition_details_json'] as Map<String, dynamic>
          : null,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'pylabrobot_definition_name': pylabrobotDefinitionName,
      'python_fqn': pythonFqn,
      'size_x_mm': sizeXmm,
      'size_y_mm': sizeYmm,
      'size_z_mm': sizeZmm,
      'plr_category': plrCategory,
      'model': model,
      'rotation_json': rotationJson,
      'praxis_labware_type_name': praxisLabwareTypeName,
      'description': description,
      'is_consumable': isConsumable,
      'nominal_volume_ul': nominalVolumeUl,
      'material': material,
      'manufacturer': manufacturer,
      'plr_definition_details_json': plrDefinitionDetailsJson,
      // 'created_at' and 'updated_at' are typically handled by the server
    };
  }
}
