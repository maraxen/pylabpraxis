import { routes } from './app.routes';

describe('App Routes Configuration', () => {
  it('should have a redirect for /visualizer to /app/workcell', () => {
    const visualizerRoute = routes.find(r => r.path === 'visualizer');
    expect(visualizerRoute).toBeDefined();
    expect(visualizerRoute?.redirectTo).toBe('app/workcell');
  });

  it('should have a redirect for /workcell to /app/workcell', () => {
    const workcellRoute = routes.find(r => r.path === 'workcell');
    expect(workcellRoute).toBeDefined();
    expect(workcellRoute?.redirectTo).toBe('app/workcell');
  });
});