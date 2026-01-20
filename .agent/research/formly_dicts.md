# Handling Dictionary (Dict) Arguments in ngx-formly

## Problem Summary
When dealing with protocol arguments or backend configurations that are arbitrary key-value pairs (dictionaries), `ngx-formly` requires a custom approach as there is no native "Object/Dict" field type that maps a dynamic list of keys to a single JS object.

## Research Findings

### 1. Standard Pattern: Repeating Section (Recommended for UX)
The most common "Formly way" to handle arbitrary key-value pairs is using the `repeat` type.

*   **Structure**: A `FormArray` where each element is an object with `{ key: string, value: any }`.
*   **Configuration Example**:
    ```typescript
    {
      key: 'config_list',
      type: 'repeat',
      props: { addText: 'Add Property' },
      fieldArray: {
        fieldGroup: [
          {
            key: 'key',
            type: 'input',
            props: { label: 'Key', required: true },
          },
          {
            key: 'value',
            type: 'input',
            props: { label: 'Value' },
          },
        ],
      },
    }
    ```
*   **Data Transformation**: Since the model will be `[{key: 'a', value: 'b'}]`, you must transform it to `{a: 'b'}` before sending to the backend, and vice versa when loading.

### 2. Expert Pattern: JSON Textarea
For highly complex or deeply nested arbitrary objects, a raw JSON editor is often more practical.

*   **Structure**: A custom field type wrapping a `<textarea>`.
*   **Validation**: Must include a JSON validator.
    ```typescript
    export function jsonValidator(control: AbstractControl) {
      try {
        JSON.parse(control.value);
        return null;
      } catch (e) {
        return { json: true };
      }
    }
    ```
*   **Pros**: Direct mapping to object (if using `JSON.parse` in a value getter/setter), handles any depth.
*   **Cons**: High friction for users, no schema enforcement for values.

### 3. Hybrid Pattern: Custom Object Field Type
You can implement a custom `FieldType` that manages its own `FormArray` internally but presents a unified `Object` to the parent form.

## Recommendations

### Option A: "Add Key/Value" List (Repeat Type)
**Use when**: Keys are mostly flat, and user-friendliness is a priority.
*   **Implementation**: Use the standard `repeat` type.
*   **Transformation**: Use a service or a Formly `extension` to automatically convert the Array to an Object on save.

### Option B: Raw JSON Editor
**Use when**: The data is highly dynamic, nested, or used by technical users/developers.
*   **Implementation**: Create a custom type `json-editor`.
*   **Enhancement**: Use a library like `ngx-monaco-editor` or `ace-editor` instead of a plain textarea for syntax highlighting and linting.

## Decision Guide

| Requirement | Recommended Solution |
| :--- | :--- |
| **Simple KV Pairs** | Repeat Type (Array of Key/Value objects) |
| **Nested Objects** | JSON Editor or Recursive Repeat |
| **Non-Technical Users**| Repeat Type with clear labels |
| **Developer Tools** | Monaco/JSON Editor |

## Next Steps
1.  **If choosing Option A**: Define a standard `kv-repeat` type in the project's Formly configuration.
2.  **If choosing Option B**: Create a `json-textarea` component and register it as a Formly type.
