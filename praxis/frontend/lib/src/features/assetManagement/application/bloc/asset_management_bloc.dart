import 'package:bloc/bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/services/asset_api_service.dart';
import 'package:praxis_lab_management/src/data/models/deck_layout_orm.dart';
import 'package:praxis_lab_management/src/data/models/labware_definition_catalog_orm.dart';
import 'package:praxis_lab_management/src/data/models/labware_instance_orm.dart';
import 'package:praxis_lab_management/src/data/models/managed_device_orm.dart';

part 'asset_management_bloc.freezed.dart';

class AssetManagementBloc
    extends Bloc<AssetManagementEvent, AssetManagementState> {
  final AssetApiService _assetApiService;

  AssetManagementBloc(this._assetApiService)
    : super(const AssetManagementInitial()) {
    on<AssetManagementLoadStarted>(_onLoadStarted);
    on<AddDeviceStarted>(_onAddDeviceStarted);
    on<UpdateDeviceStarted>(_onUpdateDeviceStarted);
    on<DeleteDeviceStarted>(_onDeleteDeviceStarted);
    on<ConnectDeviceStarted>(_onConnectDeviceStarted);
    on<InitializeDeviceStarted>(_onInitializeDeviceStarted);
    on<DisconnectDeviceStarted>(_onDisconnectDeviceStarted);
    on<AddLabwareDefinitionStarted>(_onAddLabwareDefinitionStarted);
    on<UpdateLabwareDefinitionStarted>(_onUpdateLabwareDefinitionStarted);
    on<DeleteLabwareDefinitionStarted>(_onDeleteLabwareDefinitionStarted);
    on<AddLabwareInstanceStarted>(_onAddLabwareInstanceStarted);
    on<UpdateLabwareInstanceStarted>(_onUpdateLabwareInstanceStarted);
    on<DeleteLabwareInstanceStarted>(_onDeleteLabwareInstanceStarted);
    on<AddDeckLayoutStarted>(_onAddDeckLayoutStarted);
    on<UpdateDeckLayoutStarted>(_onUpdateDeckLayoutStarted);
    on<DeleteDeckLayoutStarted>(_onDeleteDeckLayoutStarted);
  }

  Future<void> _onLoadStarted(
    AssetManagementLoadStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementLoadInProgress());
    try {
      // TODO(user): Replace with actual API calls when available
      final devices = await _assetApiService.getDevices();
      final labwareDefinitions = await _assetApiService.getLabwareDefinitions();
      final labwareInstances = await _assetApiService.getLabwareInstances();
      final deckLayouts = await _assetApiService.getDeckLayouts();
      emit(
        AssetManagementLoadSuccess(
          devices: devices,
          labwareDefinitions: labwareDefinitions,
          labwareInstances: labwareInstances,
          deckLayouts: deckLayouts,
        ),
      );
    } catch (e) {
      emit(AssetManagementLoadFailure(e.toString()));
    }
  }

  Future<void> _onAddDeviceStarted(
    AddDeviceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.createDevice(event.device);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onUpdateDeviceStarted(
    UpdateDeviceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.updateDevice(event.deviceId, event.device);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDeleteDeviceStarted(
    DeleteDeviceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.deleteDevice(event.deviceId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onConnectDeviceStarted(
    ConnectDeviceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.connectDevice(event.deviceId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onInitializeDeviceStarted(
    InitializeDeviceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.initializeDevice(event.deviceId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDisconnectDeviceStarted(
    DisconnectDeviceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.disconnectDevice(event.deviceId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onAddLabwareDefinitionStarted(
    AddLabwareDefinitionStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.createLabwareDefinition(event.labwareDefinition);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onUpdateLabwareDefinitionStarted(
    UpdateLabwareDefinitionStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.updateLabwareDefinition(
        event.labwareDefinitionId,
        event.labwareDefinition,
      );
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDeleteLabwareDefinitionStarted(
    DeleteLabwareDefinitionStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.deleteLabwareDefinition(event.labwareDefinitionId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onAddLabwareInstanceStarted(
    AddLabwareInstanceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.createLabwareInstance(event.labwareInstance);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onUpdateLabwareInstanceStarted(
    UpdateLabwareInstanceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.updateLabwareInstance(
        event.instanceId,
        event.labwareInstance,
      );
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDeleteLabwareInstanceStarted(
    DeleteLabwareInstanceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.deleteLabwareInstance(event.instanceId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onAddDeckLayoutStarted(
    AddDeckLayoutStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.createDeckLayout(event.deckLayout);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onUpdateDeckLayoutStarted(
    UpdateDeckLayoutStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.updateDeckLayout(
        event.deckLayoutId,
        event.deckLayout,
      );
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDeleteDeckLayoutStarted(
    DeleteDeckLayoutStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.deleteDeckLayout(event.deckLayoutId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }
}

/// Events for AssetManagementBloc
@freezed
sealed class AssetManagementEvent with _$AssetManagementEvent {
  const factory AssetManagementEvent.loadStarted() = AssetManagementLoadStarted;
  const factory AssetManagementEvent.addDeviceStarted(ManagedDeviceOrm device) =
      AddDeviceStarted;
  const factory AssetManagementEvent.updateDeviceStarted(
    String deviceId,
    ManagedDeviceOrm device,
  ) = UpdateDeviceStarted;
  const factory AssetManagementEvent.deleteDeviceStarted(String deviceId) =
      DeleteDeviceStarted;
  const factory AssetManagementEvent.connectDeviceStarted(String deviceId) =
      ConnectDeviceStarted;
  const factory AssetManagementEvent.initializeDeviceStarted(String deviceId) =
      InitializeDeviceStarted;
  const factory AssetManagementEvent.disconnectDeviceStarted(String deviceId) =
      DisconnectDeviceStarted;
  const factory AssetManagementEvent.addLabwareDefinitionStarted(
    LabwareDefinitionCatalogOrm labwareDefinition,
  ) = AddLabwareDefinitionStarted;
  const factory AssetManagementEvent.updateLabwareDefinitionStarted(
    String labwareDefinitionId,
    LabwareDefinitionCatalogOrm labwareDefinition,
  ) = UpdateLabwareDefinitionStarted;
  const factory AssetManagementEvent.deleteLabwareDefinitionStarted(
    String labwareDefinitionId,
  ) = DeleteLabwareDefinitionStarted;
  const factory AssetManagementEvent.addLabwareInstanceStarted(
    LabwareInstanceOrm labwareInstance,
  ) = AddLabwareInstanceStarted;
  const factory AssetManagementEvent.updateLabwareInstanceStarted(
    String instanceId,
    LabwareInstanceOrm labwareInstance,
  ) = UpdateLabwareInstanceStarted;
  const factory AssetManagementEvent.deleteLabwareInstanceStarted(
    String instanceId,
  ) = DeleteLabwareInstanceStarted;
  const factory AssetManagementEvent.addDeckLayoutStarted(
    DeckLayoutOrm deckLayout,
  ) = AddDeckLayoutStarted;
  const factory AssetManagementEvent.updateDeckLayoutStarted(
    String deckLayoutId,
    DeckLayoutOrm deckLayout,
  ) = UpdateDeckLayoutStarted;
  const factory AssetManagementEvent.deleteDeckLayoutStarted(
    String deckLayoutId,
  ) = DeleteDeckLayoutStarted;
}

/// States for AssetManagementBloc
@freezed
sealed class AssetManagementState with _$AssetManagementState {
  const factory AssetManagementState.initial() = AssetManagementInitial;
  const factory AssetManagementState.loadInProgress() =
      AssetManagementLoadInProgress;
  const factory AssetManagementState.loadSuccess({
    required List<ManagedDeviceOrm> devices,
    required List<LabwareDefinitionCatalogOrm> labwareDefinitions,
    required List<LabwareInstanceOrm> labwareInstances,
    required List<DeckLayoutOrm> deckLayouts,
  }) = AssetManagementLoadSuccess;
  const factory AssetManagementState.loadFailure(String error) =
      AssetManagementLoadFailure;
  const factory AssetManagementState.updateInProgress() =
      AssetManagementUpdateInProgress;
  const factory AssetManagementState.updateSuccess() =
      AssetManagementUpdateSuccess;
  const factory AssetManagementState.updateFailure(String error) =
      AssetManagementUpdateFailure;
}
