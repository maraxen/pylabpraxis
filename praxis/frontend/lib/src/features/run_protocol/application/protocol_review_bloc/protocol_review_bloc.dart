import 'dart:convert';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:pylabpraxis_flutter/src/data/models/protocol/protocol_prepare_request.dart';
import 'package:pylabpraxis_flutter/src/data/repositories/protocol_repository.dart';
import 'package:pylabpraxis_flutter/src/features/run_protocol/domain/review_data_bundle.dart';
// import 'package:file_picker/file_picker.dart';

part 'protocol_review_event.dart';
part 'protocol_review_state.dart';
part 'protocol_review_bloc.freezed.dart';

class ProtocolReviewBloc
    extends Bloc<ProtocolReviewEvent, ProtocolReviewState> {
  final ProtocolRepository _protocolRepository;
  ReviewDataBundle? _lastLoadedData; // To hold data during preparation

  ProtocolReviewBloc({required ProtocolRepository protocolRepository})
    : _protocolRepository = protocolRepository,
      super(const ProtocolReviewState.initial()) {
    on<LoadReviewData>(_onLoadReviewData);
    on<PrepareProtocolRequested>(_onPrepareProtocolRequested);
    on<ResetReview>(_onResetReview);
  }

  void _onLoadReviewData(
    LoadReviewData event,
    Emitter<ProtocolReviewState> emit,
  ) {
    _lastLoadedData = event.reviewData;
    emit(ProtocolReviewState.ready(displayData: event.reviewData));
  }

  Future<void> _onPrepareProtocolRequested(
    PrepareProtocolRequested event,
    Emitter<ProtocolReviewState> emit,
  ) async {
    ReviewDataBundle? dataToPrepare = _lastLoadedData;

    // Fallback if _lastLoadedData is null (e.g. BLoC restarted, direct event)
    if (dataToPrepare == null && state is ProtocolReviewReady) {
      dataToPrepare = (state as ProtocolReviewReady).displayData;
    }

    if (dataToPrepare == null) {
      emit(
        const ProtocolReviewState.preparationFailure(
          error: 'Cannot prepare protocol: Review data not available.',
          displayData: null, // No data was available to attempt preparation
        ),
      );
      return;
    }

    emit(ProtocolReviewState.preparationInProgress(reviewData: dataToPrepare));

    try {
      Map<String, dynamic>? deckLayoutContent;
      if (dataToPrepare.uploadedDeckFile?.path != null ||
          dataToPrepare.uploadedDeckFile?.bytes != null) {
        if (dataToPrepare.uploadedDeckFile!.bytes != null) {
          deckLayoutContent =
              jsonDecode(utf8.decode(dataToPrepare.uploadedDeckFile!.bytes!))
                  as Map<String, dynamic>;
        } else if (dataToPrepare.uploadedDeckFile!.path != null) {
          // Placeholder for actual file reading from path for non-web platforms
          // This requires platform-specific code or a file reading utility.
          // For now, this path will likely lead to an error if bytes are not available.
          // In a real app, ensure file content is read here.
          // TODO: Implement file reading from path for non-web platforms and delete print
          print(
            "Warning: Deck file content reading from path not fully implemented for prepare request. Backend might need to handle file by name/reference if content is not passed.",
          );
          // As a fallback, if backend supports it, send filename and let backend fetch it.
          // For now, we assume content must be passed or it's an error.
          // deckLayoutContent = {'file_path_reference': dataToPrepare.uploadedDeckFile!.path!}; // Example if backend supports path
          throw Exception(
            "File content reading from path is not implemented for this mock.",
          );
        }
      }

      // Updated to use 'params' as per your observation of the ProtocolPrepareRequest model.
      // This assumes the ProtocolPrepareRequest factory constructor in your Dart model
      // expects a named parameter 'params'.
      final request = ProtocolPrepareRequest(
        protocolId: dataToPrepare.selectedProtocolInfo.name,
        // parameters: dataToPrepare.configuredParameters, // Previous
        params: dataToPrepare.configuredParameters, // Changed to 'params'
        assets: dataToPrepare.assignedAssets,
        deckLayoutName: dataToPrepare.deckLayoutName,
        deckLayoutContent: deckLayoutContent,
      );

      final preparedConfig = await _protocolRepository.prepareProtocol(
        request: request,
      );

      emit(
        ProtocolReviewState.preparationSuccess(
          preparedConfig: preparedConfig,
          reviewedData:
              dataToPrepare, // Pass the data that was successfully prepared
        ),
      );
    } catch (e) {
      emit(
        ProtocolReviewState.preparationFailure(
          error: 'Failed to prepare protocol: ${e.toString()}',
          displayData: dataToPrepare, // Pass the data that was attempted
        ),
      );
    }
  }

  void _onResetReview(ResetReview event, Emitter<ProtocolReviewState> emit) {
    _lastLoadedData = null;
    emit(const ProtocolReviewState.initial());
  }
}
