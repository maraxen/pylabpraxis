// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_profile.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UserProfile _$UserProfileFromJson(Map<String, dynamic> json) => _UserProfile(
  id: json['sub'] as String,
  username: json['preferred_username'] as String?,
  email: json['email'] as String?,
  emailVerified: json['email_verified'] as bool?,
  name: json['name'] as String?,
  givenName: json['given_name'] as String?,
  familyName: json['family_name'] as String?,
  roles:
      (json['roles'] as List<dynamic>?)?.map((e) => e as String).toList() ??
      const [],
);

Map<String, dynamic> _$UserProfileToJson(_UserProfile instance) =>
    <String, dynamic>{
      'sub': instance.id,
      'preferred_username': instance.username,
      'email': instance.email,
      'email_verified': instance.emailVerified,
      'name': instance.name,
      'given_name': instance.givenName,
      'family_name': instance.familyName,
      'roles': instance.roles,
    };
