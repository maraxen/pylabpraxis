const modules = import.meta.glob("./*/index.ts", { eager: true }) as { [key: string]: any };
const components: { [key: string]: any } = {};

for (const path in modules) {
  // Get folder name (e.g., "./Form/index.ts" -> "Form")
  const componentName = path.split("/")[1];
  components[componentName] = modules[path].default || modules[path];
}

export default components;
