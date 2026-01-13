import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ParameterViewerComponent } from './parameter-viewer.component';

describe('ParameterViewerComponent', () => {
    let component: ParameterViewerComponent;
    let fixture: ComponentFixture<ParameterViewerComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [ParameterViewerComponent]
        }).compileComponents();

        fixture = TestBed.createComponent(ParameterViewerComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should flatten nested parameters', () => {
        const params = {
            p1: 'v1',
            nested: {
                p2: 123,
                veryNested: {
                    p3: true
                }
            }
        };

        const flattened = component.flattenParameters(params);

        expect(flattened.length).toBe(5); // p1, nested(parent), p2, veryNested(parent), p3
        expect(flattened[0].key).toBe('p1');
        expect(flattened[1].isParent).toBe(true);
        expect(flattened[1].key).toBe('nested');
        expect(flattened[2].level).toBe(1);
        expect(flattened[2].key).toBe('p2');
        expect(flattened[4].level).toBe(2);
        expect(flattened[4].key).toBe('p3');
    });

    it('should format values correctly', () => {
        expect(component.formatValue(null)).toBe('null');
        expect(component.formatValue(true)).toBe('true');
        expect(component.formatValue(123)).toBe('123');
        expect(component.formatValue([1, 2])).toBe('[ 1, 2 ]');
    });

    it('should detect keys presence', () => {
        expect(component.hasKeys({})).toBe(false);
        expect(component.hasKeys({ a: 1 })).toBe(true);
        expect(component.hasKeys(null)).toBe(false);
    });
});
