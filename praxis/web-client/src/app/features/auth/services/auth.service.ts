import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthenticationService } from '@api/services/AuthenticationService';
import { ApiWrapperService } from '@core/services/api-wrapper.service';
import { ApiConfigService } from '@core/services/api-config.service';
import { tap } from 'rxjs/operators';
import { LoginRequest } from '../models/auth.models';
import { LoginResponse } from '@api/models/LoginResponse';
import { UserRead } from '@api/models/UserRead';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiWrapper = inject(ApiWrapperService);
  private apiConfigService = inject(ApiConfigService);

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.apiWrapper.wrap(AuthenticationService.loginApiV1AuthLoginPost(credentials)).pipe(
      tap((response: LoginResponse) => {
        if (response.access_token) {
          this.apiConfigService.setToken(response.access_token);
        }
      })
    );
  }

  logout(): Observable<Record<string, string>> {
    return this.apiWrapper.wrap(AuthenticationService.logoutApiV1AuthLogoutPost()).pipe(
      tap(() => {
        this.apiConfigService.setToken(undefined);
      })
    );
  }

  getCurrentUser(): Observable<UserRead> {
    return this.apiWrapper.wrap(AuthenticationService.getCurrentUserInfoApiV1AuthMeGet());
  }
}
