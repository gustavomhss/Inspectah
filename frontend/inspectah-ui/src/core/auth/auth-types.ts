export interface AuthUser {
  id: string;
  name?: string;
  email?: string;
  roles?: string[];
}

export interface AuthSession {
  token: string;
  user: AuthUser;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  token?: string;
  access_token?: string;
  user?: {
    id?: string;
    name?: string;
    email?: string;
    roles?: string[];
  };
  user_id?: string;
  email?: string;
  roles?: string[];
}
