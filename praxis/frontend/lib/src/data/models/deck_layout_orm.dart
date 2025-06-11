// Corresponds to DeckInstanceSlotItemOrm in backend
class DeckInstanceSlotItemOrm {
  final int? id;
  final int deckConfigurationId;
  final String slotName;
  final int resourceInstanceId; // FK to ResourceInstanceOrm.id
  final String?
  expectedResourceDefinitionName; // FK to ResourceDefinitionCatalogOrm.name

  DeckInstanceSlotItemOrm({
    this.id,
    required this.deckConfigurationId,
    required this.slotName,
    required this.resourceInstanceId,
    this.expectedResourceDefinitionName,
  });

  factory DeckInstanceSlotItemOrm.fromJson(Map<String, dynamic> json) {
    return DeckInstanceSlotItemOrm(
      id: json['id'] as int?,
      deckConfigurationId: json['deck_instance_id'] as int,
      slotName: json['slot_name'] as String,
      resourceInstanceId: json['resource_instance_id'] as int,
      expectedResourceDefinitionName:
          json['expected_resource_definition_name'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'deck_instance_id': deckConfigurationId,
      'slot_name': slotName,
      'resource_instance_id': resourceInstanceId,
      'expected_resource_definition_name': expectedResourceDefinitionName,
    };
  }
}

// Corresponds to DeckInstanceOrm in backend
class DeckLayoutOrm {
  final int? id; // praxis_deck_config_id
  final String layoutName;
  final int deckDeviceId; // FK to ManagedDeviceOrm.id (the deck itself)
  final String? description;
  final List<DeckInstanceSlotItemOrm>? slotItems;
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
    List<DeckInstanceSlotItemOrm>? slotItems;
    if (itemsList != null) {
      slotItems =
          itemsList
              .map(
                (i) =>
                    DeckInstanceSlotItemOrm.fromJson(i as Map<String, dynamic>),
              )
              .toList();
    }

    return DeckLayoutOrm(
      id: json['id'] as int?,
      layoutName: json['layout_name'] as String,
      deckDeviceId: json['deck_machine_id'] as int,
      description: json['description'] as String?,
      slotItems: slotItems,
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
      workspaceId:
          json['workspace_id'] as String? ??
          json['workspaceId'] as String? ??
          '', // Ensure workspaceId is present
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'layout_name': layoutName,
      'deck_machine_id': deckDeviceId,
      'description': description,
      'slot_items': slotItems?.map((item) => item.toJson()).toList(),
      'workspace_id': workspaceId,
      // 'created_at' and 'updated_at' are typically handled by the server
    };
  }
}
