import { Injectable, inject } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute, Data } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { filter } from 'rxjs/operators';

export interface Breadcrumb {
    label: string;
    url: string;
}

@Injectable({
    providedIn: 'root'
})
export class BreadcrumbService {
    private readonly router = inject(Router);
    private readonly activatedRoute = inject(ActivatedRoute);

    private readonly breadcrumbsSubject = new BehaviorSubject<Breadcrumb[]>([]);
    readonly breadcrumbs$ = this.breadcrumbsSubject.asObservable();

    constructor() {
        this.router.events.pipe(
            filter(event => event instanceof NavigationEnd)
        ).subscribe(() => {
            const root = this.router.routerState.snapshot.root;
            const breadcrumbs: Breadcrumb[] = [];
            this.addBreadcrumb(root, [], breadcrumbs);
            this.breadcrumbsSubject.next(breadcrumbs);
        });
    }

    private addBreadcrumb(route: ActivatedRoute['snapshot'], parentUrl: string[], breadcrumbs: Breadcrumb[]) {
        if (route) {
            const routeUrl = parentUrl.concat(route.url.map(url => url.path));

            // Only add breadcrumb if defined in route data
            if (route.data['breadcrumb']) {
                const breadcrumb: Breadcrumb = {
                    label: this.getLabel(route.data),
                    url: '/' + routeUrl.join('/')
                };
                breadcrumbs.push(breadcrumb);
            }

            if (route.firstChild) {
                this.addBreadcrumb(route.firstChild, routeUrl, breadcrumbs);
            }
        }
    }

    private getLabel(data: Data): string {
        return typeof data['breadcrumb'] === 'function' ? data['breadcrumb'](data) : data['breadcrumb'];
    }
}
