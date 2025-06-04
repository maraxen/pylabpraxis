import 'package:bloc/bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:praxis_lab_management/src/data/services/asset_api_service.dart';
import 'package:praxis_lab_management/src/data/models/deck_layout_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_definition_catalog_orm.dart';
import 'package:praxis_lab_management/src/data/models/resource_instance_orm.dart';
import 'package:praxis_lab_management/src/data/models/managed_machine_orm.dart';

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
    on<AddResourceDefinitionStarted>(_onAddResourceDefinitionStarted);
    on<UpdateResourceDefinitionStarted>(_onUpdateResourceDefinitionStarted);
    on<DeleteResourceDefinitionStarted>(_onDeleteResourceDefinitionStarted);
    on<AddResourceInstanceStarted>(_onAddResourceInstanceStarted);
    on<UpdateResourceInstanceStarted>(_onUpdateResourceInstanceStarted);
    on<DeleteResourceInstanceStarted>(_onDeleteResourceInstanceStarted);
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
      final machines = await _assetApiService.getDevices();
      final resourceDefinitions =
          await _assetApiService.getResourceDefinitions();
      final resourceInstances = await _assetApiService.getResourceInstances();
      final deckLayouts = await _assetApiService.getDeckLayouts();
      emit(
        AssetManagementLoadSuccess(
          machines: machines,
          resourceDefinitions: resourceDefinitions,
          resourceInstances: resourceInstances,
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
      await _assetApiService.createDevice(event.machine);
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
      await _assetApiService.updateDevice(event.machineId, event.machine);
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
      await _assetApiService.deleteDevice(event.machineId);
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
      await _assetApiService.connectDevice(event.machineId);
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
      await _assetApiService.initializeDevice(event.machineId);
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
      await _assetApiService.disconnectDevice(event.machineId);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onAddResourceDefinitionStarted(
    AddResourceDefinitionStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.createResourceDefinition(event.resourceDefinition);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onUpdateResourceDefinitionStarted(
    UpdateResourceDefinitionStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.updateResourceDefinition(
        event.resourceDefinitionId,
        event.resourceDefinition,
      );
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDeleteResourceDefinitionStarted(
    DeleteResourceDefinitionStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.deleteResourceDefinition(
        event.resourceDefinitionId,
      );
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onAddResourceInstanceStarted(
    AddResourceInstanceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.createResourceInstance(event.resourceInstance);
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onUpdateResourceInstanceStarted(
    UpdateResourceInstanceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.updateResourceInstance(
        event.instanceId,
        event.resourceInstance,
      );
      emit(const AssetManagementUpdateSuccess());
      add(const AssetManagementLoadStarted()); // Reload data
    } catch (e) {
      emit(AssetManagementUpdateFailure(e.toString()));
    }
  }

  Future<void> _onDeleteResourceInstanceStarted(
    DeleteResourceInstanceStarted event,
    Emitter<AssetManagementState> emit,
  ) async {
    emit(const AssetManagementUpdateInProgress());
    try {
      await _assetApiService.deleteResourceInstance(event.instanceId);
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
abstract class AssetManagementEvent with _$AssetManagementEvent {
  const factory AssetManagementEvent.loadStarted() = AssetManagementLoadStarted;
  const factory AssetManagementEvent.addDeviceStarted(
    ManagedDeviceOrm machine,
  ) = AddDeviceStarted;
  const factory AssetManagementEvent.updateDeviceStarted(
    String machineId,
    ManagedDeviceOrm machine,
  ) = UpdateDeviceStarted;
  const factory AssetManagementEvent.deleteDeviceStarted(String machineId) =
      DeleteDeviceStarted;
  const factory AssetManagementEvent.connectDeviceStarted(String machineId) =
      ConnectDeviceStarted;
  const factory AssetManagementEvent.initializeDeviceStarted(String machineId) =
      InitializeDeviceStarted;
  const factory AssetManagementEvent.disconnectDeviceStarted(String machineId) =
      DisconnectDeviceStarted;
  const factory AssetManagementEvent.addResourceDefinitionStarted(
    ResourceDefinitionCatalogOrm resourceDefinition,
  ) = AddResourceDefinitionStarted;
  const factory AssetManagementEvent.updateResourceDefinitionStarted(
    String resourceDefinitionId,
    ResourceDefinitionCatalogOrm resourceDefinition,
  ) = UpdateResourceDefinitionStarted;
  const factory AssetManagementEvent.deleteResourceDefinitionStarted(
    String resourceDefinitionId,
  ) = DeleteResourceDefinitionStarted;
  const factory AssetManagementEvent.addResourceInstanceStarted(
    ResourceInstanceOrm resourceInstance,
  ) = AddResourceInstanceStarted;
  const factory AssetManagementEvent.updateResourceInstanceStarted(
    String instanceId,
    ResourceInstanceOrm resourceInstance,
  ) = UpdateResourceInstanceStarted;
  const factory AssetManagementEvent.deleteResourceInstanceStarted(
    String instanceId,
  ) = DeleteResourceInstanceStarted;
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
abstract class AssetManagementState with _$AssetManagementState {
  const factory AssetManagementState.initial() = AssetManagementInitial;
  const factory AssetManagementState.loadInProgress() =
      AssetManagementLoadInProgress;
  const factory AssetManagementState.loadSuccess({
    required List<ManagedDeviceOrm> machines,
    required List<ResourceDefinitionCatalogOrm> resourceDefinitions,
    required List<ResourceInstanceOrm> resourceInstances,
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
