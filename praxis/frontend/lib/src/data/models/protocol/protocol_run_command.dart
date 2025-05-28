/// Enum representing control commands for a protocol run.
enum ProtocolRunCommand { PAUSE, RESUME, CANCEL }

/// Helper function to convert [ProtocolRunCommand] enum to a string
/// suitable for API requests.
String protocolRunCommandToString(ProtocolRunCommand command) {
  return command.toString().split('.').last;
}
