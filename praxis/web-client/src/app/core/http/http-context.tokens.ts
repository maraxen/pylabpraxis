import { HttpContextToken } from '@angular/common/http';

/**
 * Token to skip global error handling (Snackbar notifications) for a specific request.
 */
export const SKIP_ERROR_HANDLING = new HttpContextToken<boolean>(() => false);
