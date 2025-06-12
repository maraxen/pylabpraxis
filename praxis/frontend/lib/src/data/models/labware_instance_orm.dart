// Corresponds to ResourceInventoryReagentItem in backend
class ResourceInventoryReagentItem {
  final String reagentId;
  final String? reagentName;
  final String? lotNumber;
  final String? expiryDate;
  final String? supplier;
  final String? catalogNumber;
  final String? dateReceived;
  final String? dateOpened;
  final Map<String, dynamic>?
  concentration; // e.g., {"value": 10.0, "unit": "mM"}
  final Map<String, dynamic>
  initialQuantity; // e.g., {"value": 50.0, "unit": "mL"}
  final Map<String, dynamic>
  currentQuantity; // e.g., {"value": 45.5, "unit": "mL"}
  final bool? quantityUnitIsVolume;
  final Map<String, dynamic>? customFields;

  ResourceInventoryReagentItem({
    required this.reagentId,
    this.reagentName,
    this.lotNumber,
    this.expiryDate,
    this.supplier,
    this.catalogNumber,
    this.dateReceived,
    this.dateOpened,
    this.concentration,
    required this.initialQuantity,
    required this.currentQuantity,
    this.quantityUnitIsVolume,
    this.customFields,
  });

  factory ResourceInventoryReagentItem.fromJson(Map<String, dynamic> json) {
    return ResourceInventoryReagentItem(
      reagentId: json['reagent_accession_id'] as String,
      reagentName: json['reagent_name'] as String?,
      lotNumber: json['lot_number'] as String?,
      expiryDate: json['expiry_date'] as String?,
      supplier: json['supplier'] as String?,
      catalogNumber: json['catalog_number'] as String?,
      dateReceived: json['date_received'] as String?,
      dateOpened: json['date_opened'] as String?,
      concentration: json['concentration'] as Map<String, dynamic>?,
      initialQuantity: json['initial_quantity'] as Map<String, dynamic>,
      currentQuantity: json['current_quantity'] as Map<String, dynamic>,
      quantityUnitIsVolume: json['quantity_unit_is_volume'] as bool?,
      customFields: json['custom_fields'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'reagent_accession_id': reagentId,
      'reagent_name': reagentName,
      'lot_number': lotNumber,
      'expiry_date': expiryDate,
      'supplier': supplier,
      'catalog_number': catalogNumber,
      'date_received': dateReceived,
      'date_opened': dateOpened,
      'concentration': concentration,
      'initial_quantity': initialQuantity,
      'current_quantity': currentQuantity,
      'quantity_unit_is_volume': quantityUnitIsVolume,
      'custom_fields': customFields,
    };
  }
}

// Corresponds to ResourceInventoryItemCount in backend
class ResourceInventoryItemCount {
  final String? itemType; // "tip", "tube", "well_used"
  final int? initialMaxItems;
  final int? currentAvailableItems;
  final List<String>? positionsUsed;

  ResourceInventoryItemCount({
    this.itemType,
    this.initialMaxItems,
    this.currentAvailableItems,
    this.positionsUsed,
  });

  factory ResourceInventoryItemCount.fromJson(Map<String, dynamic> json) {
    return ResourceInventoryItemCount(
      itemType: json['item_type'] as String?,
      initialMaxItems: json['initial_max_items'] as int?,
      currentAvailableItems: json['current_available_items'] as int?,
      positionsUsed:
          (json['positions_used'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'item_type': itemType,
      'initial_max_items': initialMaxItems,
      'current_available_items': currentAvailableItems,
      'positions_used': positionsUsed,
    };
  }
}

// Corresponds to ResourceInventoryDataIn / ResourceInventoryDataOut in backend
class ResourceInventoryData {
  final String? praxisInventorySchemaVersion;
  final List<ResourceInventoryReagentItem>? reagents;
  final ResourceInventoryItemCount? itemCount;
  final String?
  consumableState; // "new", "used", "partially_used", "empty", "contaminated"
  final String? lastUpdatedBy; // User ID or name
  final String? inventoryNotes;
  final String? lastUpdatedAt; // DateTime as String, set by server

  ResourceInventoryData({
    this.praxisInventorySchemaVersion,
    this.reagents,
    this.itemCount,
    this.consumableState,
    this.lastUpdatedBy,
    this.inventoryNotes,
    this.lastUpdatedAt,
  });

  factory ResourceInventoryData.fromJson(Map<String, dynamic> json) {
    return ResourceInventoryData(
      praxisInventorySchemaVersion:
          json['praxis_inventory_schema_version'] as String?,
      reagents:
          (json['reagents'] as List<dynamic>?)
              ?.map(
                (e) => ResourceInventoryReagentItem.fromJson(
                  e as Map<String, dynamic>,
                ),
              )
              .toList(),
      itemCount:
          json['item_count'] != null
              ? ResourceInventoryItemCount.fromJson(
                json['item_count'] as Map<String, dynamic>,
              )
              : null,
      consumableState: json['consumable_state'] as String?,
      lastUpdatedBy: json['last_updated_by'] as String?,
      inventoryNotes: json['inventory_notes'] as String?,
      lastUpdatedAt: json['last_updated_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'praxis_inventory_schema_version': praxisInventorySchemaVersion,
      'reagents': reagents?.map((e) => e.toJson()).toList(),
      'item_count': itemCount?.toJson(),
      'consumable_state': consumableState,
      'last_updated_by': lastUpdatedBy,
      'inventory_notes': inventoryNotes,
      // 'last_updated_at' is typically set by the server on PUT
    };
  }
}

// Corresponds to ResourceInstanceOrm in backend database model
class ResourceInstanceOrm {
  final int? id; // praxis_resource_instance_accession_id
  final String userAssignedName;
  final String pylabrobotDefinitionName; // FK to ResourceDefinitionCatalogOrm
  final String? lotNumber;
  final String? expiryDate; // DateTime as String
  final String? dateAddedToInventory; // DateTime as String
  final String? currentStatus; // ResourceInstanceStatusEnum as String
  final String? statusDetails;
  final String? currentDeckSlotName;
  final int? locationDeviceId; // FK to ManagedDeviceOrm
  final String? physicalLocationDescription;
  final bool? isPermanentFixture;
  final String? currentProtocolRunGuid; // FK to ProtocolRunOrm
  final String? createdAt; // DateTime as String
  final String? updatedAt; // DateTime as String

  // Nested inventory data, maps to properties_json in backend ORM
  // and ResourceInventoryDataIn/Out in API
  final ResourceInventoryData? inventoryData;

  // Workspace ID is a common requirement in frontend models, though not explicitly in backend ORM shown
  // Adding it here for consistency with other ORM classes in the frontend if needed.
  // If not needed, it can be removed.
  final String? workspaceId;

  ResourceInstanceOrm({
    this.accession_id,
    required this.userAssignedName,
    required this.pylabrobotDefinitionName,
    this.lotNumber,
    this.expiryDate,
    this.dateAddedToInventory,
    this.currentStatus,
    this.statusDetails,
    this.currentDeckSlotName,
    this.locationDeviceId,
    this.physicalLocationDescription,
    this.inventoryData, // This was properties_json in the backend ORM
    this.isPermanentFixture,
    this.currentProtocolRunGuid,
    this.createdAt,
    this.updatedAt,
    this.workspaceId, // Added for frontend consistency
  });

  factory ResourceInstanceOrm.fromJson(Map<String, dynamic> json) {
    return ResourceInstanceOrm(
      id: json['id'] as int?,
      userAssignedName: json['user_assigned_name'] as String,
      pylabrobotDefinitionName: json['name'] as String,
      lotNumber: json['lot_number'] as String?,
      expiryDate: json['expiry_date'] as String?,
      dateAddedToInventory: json['date_added_to_inventory'] as String?,
      currentStatus: json['current_status'] as String?,
      statusDetails: json['status_details'] as String?,
      currentDeckSlotName: json['current_deck_slot_name'] as String?,
      locationDeviceId: json['location_machine_accession_id'] as int?,
      physicalLocationDescription:
          json['physical_location_description'] as String?,
      // properties_json from backend ORM maps to inventoryData here
      inventoryData:
          json['properties_json'] != null
              ? ResourceInventoryData.fromJson(
                json['properties_json'] as Map<String, dynamic>,
              )
              : ( // If properties_json is not present, check if inventory fields are top-level (e.g. from inventory specific endpoints)
              json.containsKey('praxis_inventory_schema_version') ||
                  json.containsKey('reagents') ||
                  json.containsKey('item_count'))
              ? ResourceInventoryData.fromJson(
                json,
              ) // Assume flat structure from inventory endpoint
              : null,
      isPermanentFixture: json['is_permanent_fixture'] as bool?,
      currentProtocolRunGuid:
          json['current_protocol_run_accession_id'] as String?,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
      workspaceId:
          json['workspaceId'] as String? ??
          json['workspace_accession_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      'id': id,
      'user_assigned_name': userAssignedName,
      'name': pylabrobotDefinitionName,
      'lot_number': lotNumber,
      'expiry_date': expiryDate,
      // 'date_added_to_inventory': dateAddedToInventory, // Usually server-set
      'current_status': currentStatus,
      'status_details': statusDetails,
      'current_deck_slot_name': currentDeckSlotName,
      'location_machine_accession_id': locationDeviceId,
      'physical_location_description': physicalLocationDescription,
      // inventoryData maps to properties_json for general instance creation/update
      // For specific inventory updates, inventoryData.toJson() will be sent directly.
      'properties_json': inventoryData?.toJson(),
      'is_permanent_fixture': isPermanentFixture,
      'current_protocol_run_accession_id': currentProtocolRunGuid,
      // 'created_at': createdAt, // Usually server-set
      // 'updated_at': updatedAt, // Usually server-set
    };
    if (workspaceId != null) {
      data['workspace_accession_id'] = workspaceId;
    }
    return data;
  }
}
