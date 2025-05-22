/// Represents the different steps in the "Run New Protocol" workflow.
enum WorkflowStep {
  /// Initial step: User selects a protocol.
  protocolSelection,

  /// User configures the parameters for the selected protocol.
  parameterConfiguration,

  /// User assigns assets required by the protocol.
  assetAssignment,

  /// User configures the deck layout.
  deckConfiguration,

  /// User reviews all collected information and prepares the protocol.
  reviewAndPrepare,

  /// User is ready to start the prepared protocol.
  startProtocol,

  /// Workflow completed or exited.
  workflowComplete,
}
