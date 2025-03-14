export interface User {
  username: string;
  display_name?: string;
  is_admin: boolean;
}

export interface UserInfo {
  smtp_username?: string;
  smtp_password?: string;
  [key: string]: any;
}