/**
 * Unified Repository Interface
 *
 * Defines the contract for both Synchronous (Legacy) and Asynchronous (OPFS) repositories.
 * Allows consumers to be agnostic of the underlying implementation during migration.
 */

import { Observable } from 'rxjs';
import { BaseEntity, QueryCriteria, QueryOptions } from './base-sqlite-repository';

/**
 * Universal Repository Interface
 * Supports both Observable (Async) and direct T[] (Sync) returns via method overloading or union types.
 *
 * NOTE: For strict typing, consumers should prefer specialized interfaces or
 * use the specific Async/Sync repository classes until migration is complete.
 */
export interface IRepository<T extends BaseEntity> {
    findAll(options?: QueryOptions<T>): T[] | Observable<T[]>;
    findById(id: string): T | null | Observable<T | null>;
    findBy(criteria: QueryCriteria<T>, options?: QueryOptions<T>): T[] | Observable<T[]>;
    findOneBy(criteria: QueryCriteria<T>): T | null | Observable<T | null>;
    count(): number | Observable<number>;
    create(entity: Omit<T, 'created_at' | 'updated_at'>): T | Observable<T>;
    update(id: string, updates: Partial<T>): T | null | Observable<T | null>;
    delete(id: string): boolean | Observable<boolean>;
}

/**
 * Type guard to check if a result is an Observable
 */
export function isObservable<T>(result: any): result is Observable<T> {
    return result instanceof Observable;
}

/**
 * Helper type for Async Repositories
 */
export type AsyncRepository<T extends BaseEntity> = {
    [K in keyof IRepository<T>]: (...args: Parameters<IRepository<T>[K]>) => Observable<ExtractObservableType<ReturnType<IRepository<T>[K]>>>;
};

type ExtractObservableType<T> = T extends Observable<infer U> ? U : T;
