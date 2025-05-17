// Defines a model for user profile information.
//
// This class is used to represent user-specific data, typically fetched
// after successful authentication (e.g., from an OIDC userinfo endpoint).

import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_profile.freezed.dart';
part 'user_profile.g.dart';

/// Represents user profile information.
///
/// Fields typically include user ID, name, email, and other relevant details.
@freezed
abstract class UserProfile with _$UserProfile {
  /// Default constructor for [UserProfile].
  ///
  /// Parameters:
  ///   [id] - The unique identifier for the user (e.g., subject from ID token).
  ///   [username] - The username, often `preferred_username` from OIDC.
  ///   [email] - The user's email address.
  ///   [emailVerified] - Whether the user's email address has been verified.
  ///   [name] - The user's full name.
  ///   [givenName] - The user's given (first) name.
  ///   [familyName] - The user's family (last) name.
  ///   [roles] - A list of roles assigned to the user.
  const factory UserProfile({
    required String id,
    String? username,
    String? email,
    @JsonKey(name: 'email_verified') bool? emailVerified,
    String? name,
    @JsonKey(name: 'given_name') String? givenName,
    @JsonKey(name: 'family_name') String? familyName,
    @Default([]) List<String> roles,
    // Add any other fields you expect from your OIDC userinfo endpoint
  }) = _UserProfile;

  /// Creates a [UserProfile] instance from a JSON map.
  factory UserProfile.fromJson(Map<String, dynamic> json) =>
      _$UserProfileFromJson(json);
}
