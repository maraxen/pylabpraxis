import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_asset.dart';

part 'protocol_assets_event.dart';
part 'protocol_assets_state.dart';
part 'protocol_assets_bloc.freezed.dart';

class ProtocolAssetsBloc
    extends Bloc<ProtocolAssetsEvent, ProtocolAssetsState> {
  ProtocolAssetsBloc() : super(const ProtocolAssetsState.initial()) {
    on<LoadRequiredAssets>(_onLoadRequiredAssets);
    on<AssetAssignmentChanged>(_onAssetAssignmentChanged);
  }

  void _onLoadRequiredAssets(
    LoadRequiredAssets event,
    Emitter<ProtocolAssetsState> emit,
  ) {
    final initialAssignments = <String, String>{};
    if (event.existingAssignments != null) {
      initialAssignments.addAll(event.existingAssignments!);
    }
    // Ensure all required assets have an entry, even if empty from existing or default
    for (var asset in event.assetsFromProtocolDetails) {
      if (!initialAssignments.containsKey(asset.name)) {
        initialAssignments[asset.name] = '';
      }
    }

    emit(
      ProtocolAssetsState.loaded(
        requiredAssets: event.assetsFromProtocolDetails,
        currentAssignments: initialAssignments,
        isValid: _checkAssignmentsValidity(
          event.assetsFromProtocolDetails,
          initialAssignments,
        ),
      ),
    );
  }

  void _onAssetAssignmentChanged(
    AssetAssignmentChanged event,
    Emitter<ProtocolAssetsState> emit,
  ) {
    if (state is ProtocolAssetsLoaded) {
      final loadedState = state as ProtocolAssetsLoaded;

      final newAssignments = Map<String, String>.from(
        loadedState.currentAssignments,
      );
      newAssignments[event.assetName] = event.assignedValue;

      emit(
        loadedState.copyWith(
          currentAssignments: newAssignments,
          isValid: _checkAssignmentsValidity(
            loadedState.requiredAssets,
            newAssignments,
          ),
        ),
      );
    }
  }

  bool _checkAssignmentsValidity(
    List<ProtocolAsset> requiredAssets,
    Map<String, String> assignments,
  ) {
    for (var asset in requiredAssets) {
      if (asset.required == true) {
        final assignedValue = assignments[asset.name];
        if (assignedValue == null || assignedValue.trim().isEmpty) {
          return false;
        }
      }
    }
    return true;
  }
}
