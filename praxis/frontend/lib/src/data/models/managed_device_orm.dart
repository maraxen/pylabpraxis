class ManagedDeviceOrm {
  final String name;
  final String type;
  final Map<String, dynamic> metadata;
  final bool isAvailable;
  final String? description;

  ManagedDeviceOrm({
    required this.name,
    required this.type,
    required this.metadata,
    required this.isAvailable,
    this.description,
  });

  factory ManagedDeviceOrm.fromJson(Map<String, dynamic> json) {
    return ManagedDeviceOrm(
      name: json['name'] as String,
      type: json['type'] as String,
      metadata: json['metadata'] as Map<String, dynamic>,
      isAvailable: json['is_available'] as bool,
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'type': type,
      'metadata': metadata,
      'is_available': isAvailable,
      'description': description,
    };
  }
}
