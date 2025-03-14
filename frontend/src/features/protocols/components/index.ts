// Auto-import all components from subdirectories with proper type assertion
const modules = import.meta.glob("./*/index.ts", { eager: true }) as { [key: string]: any };
const components: { [key: string]: any } = {};

for (const path in modules) {
  // Get folder name (e.g., "./Button/index.ts" -> "Button")
  const componentName = path.split("/")[1];
  components[componentName] = modules[path].default || modules[path];
}

// Export common components
export * from './common';

// Export form components
export * from './form';

// Export asset components
export * from './assets';

export default components;
