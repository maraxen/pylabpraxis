import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AssetWizard } from './asset-wizard';

describe('AssetWizard', () => {
  let component: AssetWizard;
  let fixture: ComponentFixture<AssetWizard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AssetWizard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AssetWizard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
