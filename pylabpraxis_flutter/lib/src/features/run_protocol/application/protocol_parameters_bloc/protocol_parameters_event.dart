part of 'protocol_parameters_bloc.dart';

@freezed
sealed class ProtocolParametersEvent with _$ProtocolParametersEvent {
  const factory ProtocolParametersEvent.loadProtocolParameters({
    required ProtocolDetails protocolDetails,
    Map<String, dynamic>? existingConfiguredParameters, // Added for editing
  }) = LoadProtocolParameters;

  const factory ProtocolParametersEvent.parameterValueChanged({
    required String parameterPath,
    required dynamic value,
    int? itemIndex,
    String? subKeyOrDictItemKey,
  }) = ParameterValueChanged;

  const factory ProtocolParametersEvent.addArrayItem({
    required String parameterPath,
  }) = AddArrayItem;

  const factory ProtocolParametersEvent.addArrayItemWithValue({
    required String parameterPath,
    required dynamic value,
  }) = AddArrayItemWithValue;

  const factory ProtocolParametersEvent.removeArrayItem({
    required String parameterPath,
    required int index,
  }) = RemoveArrayItem;

  const factory ProtocolParametersEvent.reorderArrayItem({
    required String parameterPath,
    required int oldIndex,
    required int newIndex,
  }) = ReorderArrayItem;

  const factory ProtocolParametersEvent.addDictionaryPair({
    required String parameterPath,
  }) = AddDictionaryPair;

  const factory ProtocolParametersEvent.addDictionaryPairWithKey({
    required String parameterPath,
    required String key,
  }) = AddDictionaryPairWithKey;

  const factory ProtocolParametersEvent.removeDictionaryPair({
    required String parameterPath,
    required String keyToRemove,
  }) = RemoveDictionaryPair;

  const factory ProtocolParametersEvent.updateDictionaryKey({
    required String parameterPath,
    required String oldKey,
    required String newKey,
  }) = UpdateDictionaryKey;

  const factory ProtocolParametersEvent.updateDictionaryValue({
    required String parameterPath,
    required String key,
    required dynamic newValue,
  }) = UpdateDictionaryValue;

  const factory ProtocolParametersEvent.assignValueToDictionaryKey({
    required String dictParameterPath,
    required String targetKey,
    required dynamic draggableValue,
  }) = AssignValueToDictionaryKey;

  const factory ProtocolParametersEvent.validateParameterValue({
    required String parameterPath,
    required dynamic value,
  }) = ValidateParameterValue;
}
