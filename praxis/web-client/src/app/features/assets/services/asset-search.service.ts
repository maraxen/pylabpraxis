import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, forkJoin, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { AssetService } from './asset.service';
import { Command } from '../../../core/services/command-registry.service';
import { Machine, Resource } from '../models/asset.models';

@Injectable({
    providedIn: 'root'
})
export class AssetSearchService {
    private assetService = inject(AssetService);
    private router = inject(Router);

    search(query: string): Observable<Command[]> {
        if (!query || query.length < 2) {
            return of([]);
        }

        const normalizedQuery = query.toLowerCase();

        return forkJoin({
            machines: this.assetService.getMachines().pipe(catchError(() => of([]))),
            resources: this.assetService.getResources().pipe(catchError(() => of([])))
        }).pipe(
            map(({ machines, resources }) => {
                const commands: Command[] = [];

                // Map Machines
                machines.forEach(machine => {
                    if (this.matches(machine, normalizedQuery)) {
                        commands.push({
                            id: `machine-${machine.accession_id}`,
                            label: machine.name,
                            description: `Machine • ${machine.status} • ${machine.status_details || 'No details'}`,
                            category: 'Asset',
                            icon: 'precision_manufacturing',
                            action: () => {
                                this.router.navigate(['/app/assets'], {
                                    queryParams: { type: 'machine' }
                                    // Future: Add ?highlight=machine.accession_id
                                });
                            }
                        });
                    }
                });

                // Map Resources
                resources.forEach(resource => {
                    if (this.matches(resource, normalizedQuery)) {
                        commands.push({
                            id: `resource-${resource.accession_id}`,
                            label: resource.name,
                            description: `Resource • ${resource.status} • ${resource.status_details || 'No details'}`,
                            category: 'Asset',
                            icon: 'science',
                            action: () => {
                                this.router.navigate(['/app/assets'], {
                                    queryParams: { type: 'resource' }
                                });
                            }
                        });
                    }
                });

                return commands;
            })
        );
    }

    private matches(item: Machine | Resource, query: string): boolean {
        if (this.isMachine(item)) {
            return (
                item.name.toLowerCase().includes(query) ||
                (item.description || '').toLowerCase().includes(query) ||
                (item.manufacturer || '').toLowerCase().includes(query) ||
                (item.model || '').toLowerCase().includes(query)
            );
        }
        return item.name.toLowerCase().includes(query);
    }

    private isMachine(item: Machine | Resource): item is Machine {
        return (item as any).model !== undefined || (item as any).manufacturer !== undefined;
    }
}
