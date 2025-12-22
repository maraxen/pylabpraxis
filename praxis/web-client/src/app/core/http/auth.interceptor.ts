
import { HttpHandlerFn, HttpInterceptorFn, HttpRequest } from '@angular/common/http';
import { inject } from '@angular/core';
import { AppStore } from '../store/app.store';

/**
 * @deprecated This interceptor is kept for backwards compatibility.
 * The Keycloak interceptor in app.config.ts handles auth tokens.
 */
export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const store = inject(AppStore);
  const auth = store.auth();
  const token = auth.token;

  if (token) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(cloned);
  }

  return next(req);
};
