// dart format width=80
// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'user_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$UserProfile {

@JsonKey(name: 'sub') String get id;// Map 'sub' JSON key to 'id' field
@JsonKey(name: 'preferred_username') String? get username;// Map 'preferred_username' to 'username'
 String? get email;@JsonKey(name: 'email_verified') bool? get emailVerified; String? get name;@JsonKey(name: 'given_name') String? get givenName;@JsonKey(name: 'family_name') String? get familyName; List<String> get roles;
/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$UserProfileCopyWith<UserProfile> get copyWith => _$UserProfileCopyWithImpl<UserProfile>(this as UserProfile, _$identity);

  /// Serializes this UserProfile to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is UserProfile&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.email, email) || other.email == email)&&(identical(other.emailVerified, emailVerified) || other.emailVerified == emailVerified)&&(identical(other.name, name) || other.name == name)&&(identical(other.givenName, givenName) || other.givenName == givenName)&&(identical(other.familyName, familyName) || other.familyName == familyName)&&const DeepCollectionEquality().equals(other.roles, roles));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,email,emailVerified,name,givenName,familyName,const DeepCollectionEquality().hash(roles));

@override
String toString() {
  return 'UserProfile(id: $id, username: $username, email: $email, emailVerified: $emailVerified, name: $name, givenName: $givenName, familyName: $familyName, roles: $roles)';
}


}

/// @nodoc
abstract mixin class $UserProfileCopyWith<$Res>  {
  factory $UserProfileCopyWith(UserProfile value, $Res Function(UserProfile) _then) = _$UserProfileCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'sub') String id,@JsonKey(name: 'preferred_username') String? username, String? email,@JsonKey(name: 'email_verified') bool? emailVerified, String? name,@JsonKey(name: 'given_name') String? givenName,@JsonKey(name: 'family_name') String? familyName, List<String> roles
});




}
/// @nodoc
class _$UserProfileCopyWithImpl<$Res>
    implements $UserProfileCopyWith<$Res> {
  _$UserProfileCopyWithImpl(this._self, this._then);

  final UserProfile _self;
  final $Res Function(UserProfile) _then;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? username = freezed,Object? email = freezed,Object? emailVerified = freezed,Object? name = freezed,Object? givenName = freezed,Object? familyName = freezed,Object? roles = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,username: freezed == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String?,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,emailVerified: freezed == emailVerified ? _self.emailVerified : emailVerified // ignore: cast_nullable_to_non_nullable
as bool?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,givenName: freezed == givenName ? _self.givenName : givenName // ignore: cast_nullable_to_non_nullable
as String?,familyName: freezed == familyName ? _self.familyName : familyName // ignore: cast_nullable_to_non_nullable
as String?,roles: null == roles ? _self.roles : roles // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// @nodoc
@JsonSerializable()

class _UserProfile implements UserProfile {
  const _UserProfile({@JsonKey(name: 'sub') required this.id, @JsonKey(name: 'preferred_username') this.username, this.email, @JsonKey(name: 'email_verified') this.emailVerified, this.name, @JsonKey(name: 'given_name') this.givenName, @JsonKey(name: 'family_name') this.familyName, final  List<String> roles = const []}): _roles = roles;
  factory _UserProfile.fromJson(Map<String, dynamic> json) => _$UserProfileFromJson(json);

@override@JsonKey(name: 'sub') final  String id;
// Map 'sub' JSON key to 'id' field
@override@JsonKey(name: 'preferred_username') final  String? username;
// Map 'preferred_username' to 'username'
@override final  String? email;
@override@JsonKey(name: 'email_verified') final  bool? emailVerified;
@override final  String? name;
@override@JsonKey(name: 'given_name') final  String? givenName;
@override@JsonKey(name: 'family_name') final  String? familyName;
 final  List<String> _roles;
@override@JsonKey() List<String> get roles {
  if (_roles is EqualUnmodifiableListView) return _roles;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_roles);
}


/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$UserProfileCopyWith<_UserProfile> get copyWith => __$UserProfileCopyWithImpl<_UserProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$UserProfileToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _UserProfile&&(identical(other.id, id) || other.id == id)&&(identical(other.username, username) || other.username == username)&&(identical(other.email, email) || other.email == email)&&(identical(other.emailVerified, emailVerified) || other.emailVerified == emailVerified)&&(identical(other.name, name) || other.name == name)&&(identical(other.givenName, givenName) || other.givenName == givenName)&&(identical(other.familyName, familyName) || other.familyName == familyName)&&const DeepCollectionEquality().equals(other._roles, _roles));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,username,email,emailVerified,name,givenName,familyName,const DeepCollectionEquality().hash(_roles));

@override
String toString() {
  return 'UserProfile(id: $id, username: $username, email: $email, emailVerified: $emailVerified, name: $name, givenName: $givenName, familyName: $familyName, roles: $roles)';
}


}

/// @nodoc
abstract mixin class _$UserProfileCopyWith<$Res> implements $UserProfileCopyWith<$Res> {
  factory _$UserProfileCopyWith(_UserProfile value, $Res Function(_UserProfile) _then) = __$UserProfileCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'sub') String id,@JsonKey(name: 'preferred_username') String? username, String? email,@JsonKey(name: 'email_verified') bool? emailVerified, String? name,@JsonKey(name: 'given_name') String? givenName,@JsonKey(name: 'family_name') String? familyName, List<String> roles
});




}
/// @nodoc
class __$UserProfileCopyWithImpl<$Res>
    implements _$UserProfileCopyWith<$Res> {
  __$UserProfileCopyWithImpl(this._self, this._then);

  final _UserProfile _self;
  final $Res Function(_UserProfile) _then;

/// Create a copy of UserProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? username = freezed,Object? email = freezed,Object? emailVerified = freezed,Object? name = freezed,Object? givenName = freezed,Object? familyName = freezed,Object? roles = null,}) {
  return _then(_UserProfile(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,username: freezed == username ? _self.username : username // ignore: cast_nullable_to_non_nullable
as String?,email: freezed == email ? _self.email : email // ignore: cast_nullable_to_non_nullable
as String?,emailVerified: freezed == emailVerified ? _self.emailVerified : emailVerified // ignore: cast_nullable_to_non_nullable
as bool?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,givenName: freezed == givenName ? _self.givenName : givenName // ignore: cast_nullable_to_non_nullable
as String?,familyName: freezed == familyName ? _self.familyName : familyName // ignore: cast_nullable_to_non_nullable
as String?,roles: null == roles ? _self._roles : roles // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
