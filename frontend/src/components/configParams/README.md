# Configuration Parameters Components

## Component Architecture

This module provides drag-and-drop enabled components for managing parameter configurations.

### Core Components

- **SortableValueItem**: The primary component for displaying and manipulating values. Supports both draggable and sortable modes.
- **GroupItem**: A container component for groups of values with a title and actions.
- **droppableGroup**: A lower-level droppable container for generic use.

### Migration Notice

The following components are deprecated and should be replaced with SortableValueItem:

- ❌ SortableValue (use SortableValueItem instead)
- ❌ SortableItem (use SortableValueItem instead)
- ❌ draggableValue (use SortableValueItem with dragMode="draggable" instead)

### Component Hierarchy

```
Component Hierarchy:
├── SortableValueItem (preferred value component - supports both drag modes)
│   └── ValueDisplay (for displaying and editing values)
│
├── GroupItem (complete group with title and values)
│   ├── SortableValueItem (for each group value)
│   └── ValueDisplay (for displaying values)
│
└── droppableGroup (generic droppable container)
    └── [children] (custom content)
```

## Usage Examples

### SortableValueItem

```tsx
// Use as a sortable item (default)
<SortableValueItem
  id="item-1"
  value="My Value"
  onDelete={() => handleDelete('item-1')}
  onEdit={() => handleEdit('item-1')}
/>

// Use as a draggable item
<SortableValueItem
  id="item-2"
  value="Drag Me"
  dragMode="draggable"
/>
```

### GroupItem

```tsx
<GroupItem
  groupId="group-1"
  group={{
    id: "group-1",
    name: "My Group",
    values: [
      { id: "val-1", value: "Value 1" },
      { id: "val-2", value: "Value 2" }
    ],
    isEditable: true
  }}
  onDelete={() => handleDeleteGroup('group-1')}
/>
```
