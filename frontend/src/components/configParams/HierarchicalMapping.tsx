import React, { useState, useRef } from 'react';
import { VStack, Box, Button, IconButton, SimpleGrid, Heading } from '@chakra-ui/react';
import { AutoComplete, AutoCompleteInput, AutoCompleteItem, AutoCompleteList, AutoCompleteCreatable } from "@choc-ui/chakra-autocomplete";
import { LuX } from "react-icons/lu";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { StringInput } from '../configParams/strings';
import { NumberInput } from '../configParams/numbers';
import { BooleanInput } from '../configParams/booleans';
import { ArrayInput } from '../configParams/arrays';

interface SubvariableConfig {
  type: string;
  default?: any;
  constraints: Record<string, any>;
  // Add other config properties as needed
}

interface SubvariablesData {
  [key: string]: any;
  values: string[];
}

interface HierarchicalMappingProps {
  name: string;
  value: Record<string, string[] | SubvariablesData>;
  config: {
    constraints: {
      parent: string;
      creatable?: boolean;
      key_param?: boolean;
      value_param?: boolean;
      key_array?: string[];
      value_array?: string[];
      subvariables?: Record<string, SubvariableConfig>;
      key_type?: string;
      value_type?: string;
      value_array_len?: number;
    };
  };
  onChange: (value: Record<string, string[] | SubvariablesData>) => void;
}

interface SortableItemProps {
  id: string;
  value: string;
  onValueChange: (newValue: string) => void;
  type: string;
}

const SortableItem: React.FC<SortableItemProps> = ({ id, value, onValueChange, type }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const renderInput = () => {
    switch (type) {
      case 'string':
        return <StringInput name={id} value={value} config={{ type }} onChange={(name, newValue) => onValueChange(newValue)} />;
      case 'number':
      case 'integer':
      case 'float':
        return <NumberInput name={id} value={value} config={{ type }} onChange={(name, newValue) => onValueChange(newValue)} />;
      case 'boolean':
        return <BooleanInput name={id} value={value} config={{ type }} onChange={(name, newValue) => onValueChange(newValue)} />;
      case 'array':
        return <ArrayInput name={id} value={value} config={{ type }} onChange={(name, newValue) => onValueChange(newValue)} />;
      default:
        return <Box>{`Unsupported type: ${type}`}</Box>;
    }
  };

  return (
    <Box ref={setNodeRef} style={style} display="flex" alignItems="center" gap={2} p={2} borderWidth="1px" borderRadius="md">
      <Box cursor="grab" {...attributes} {...listeners}>
        ☰
      </Box>
      {renderInput()}
    </Box>
  );
};

const NestedMapping: React.FC<HierarchicalMappingProps> = ({
  name,
  value,
  config,
  onChange,
}) => {
  console.log("HierarchicalMapping: name, value, config", name, value, config); // ADDED
  const { constraints } = config;
  const isParentKey = constraints.parent === 'key';
  const creatableKey = !!(constraints.creatable || (constraints.key_param && !constraints.key_array));
  const creatableValue = !!(constraints.creatable || (constraints.value_param && !constraints.value_array));
  const parentOptions = isParentKey ? constraints.key_array : constraints.value_array;
  const childOptions = isParentKey ? constraints.value_array : constraints.key_array;
  const subvariables = constraints.subvariables || {};
  const keyType = constraints.key_type || 'string';
  const valueType = constraints.value_type || 'string';

  console.log("HierarchicalMapping: subvariables", subvariables); // ADDED

  const [newParentKey, setNewParentKey] = useState<string | null>(null);
  const [newValue, setNewValue] = useState<string | null>(null);
  const autoCompleteRef = useRef<any>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: any, parentVal: string) => {
    const { active, over } = event;

    if (active.id !== over.id) {
      const currentData = value[parentVal];
      const currentValues = Array.isArray(currentData) ? currentData : (currentData as SubvariablesData).values;
      const oldIndex = currentValues.indexOf(active.id);
      const newIndex = currentValues.indexOf(over.id);

      const newValues = arrayMove(currentValues, oldIndex, newIndex);

      onChange({
        ...value,
        [parentVal]: Object.keys(subvariables).length > 0
          ? { ...(currentData as SubvariablesData), values: newValues }
          : newValues
      });
    }
  };

  const handleRemoveGroup = (parentVal: string) => {
    const newValue = { ...value };
    delete newValue[parentVal];
    onChange(newValue);
  };

  const handleRemoveChild = (parentVal: string, childToRemove: string) => {
    const currentData = value[parentVal];
    const currentValues = Array.isArray(currentData) ? currentData : (currentData as SubvariablesData).values;
    const newValues = currentValues.filter(child => child !== childToRemove);

    onChange({
      ...value,
      [parentVal]: Object.keys(subvariables).length > 0
        ? { ...(currentData as SubvariablesData), values: newValues }
        : newValues
    });
  };

  const handleAddGroup = () => {
    setNewParentKey(''); // Clear any previous new key
    setNewParentKey('new'); // Set a temporary key to trigger the new input
    setTimeout(() => {
      autoCompleteRef.current?.focus();
    }, 0);
  };

  const handleAddValue = () => {
    setNewValue(''); // Clear any previous new value
    setNewValue('new'); // Set a temporary value to trigger the new input
    setTimeout(() => {
      autoCompleteRef.current?.focus();
    }, 0);
  };

  const handleEditChild = (parentVal: string, oldChild: string, newChild: string) => {
    const currentData = value[parentVal];
    const currentValues = Array.isArray(currentData) ? currentData : (currentData as SubvariablesData).values;
    const newValues = currentValues.map((child: string) => (child === oldChild ? newChild : child));

    onChange({
      ...value,
      [parentVal]: Object.keys(subvariables).length > 0
        ? { ...(currentData as SubvariablesData), values: newValues }
        : newValues
    });
  };

  const handleSelectNewParent = (item: any) => {
    const newParentVal = item.value;
    onChange({
      ...value,
      [newParentVal]: [],
    });
    setNewParentKey(null); // Reset newParentKey after selection
  };

  const handleSelectParent = (item: any, parentVal: string) => {
    const newParentVal = item.value;
    const currentData = value[parentVal];
    const currentValues = Array.isArray(currentData) ? currentData : (currentData as SubvariablesData).values;
    const newValue = { ...value };
    delete newValue[parentVal];

    newValue[newParentVal] = Object.keys(subvariables).length > 0
      ? { ...(currentData as SubvariablesData), values: currentValues }
      : currentValues;

    onChange(newValue);
  };

  const handleSelectNewValue = (item: any) => {
    const newValueVal = item.value;
    onChange({
      ...value,
      [newValueVal]: [],
    });
    setNewValue(null); // Reset newValue after selection
  };

  const renderSubvariableInput = (subVarName: string, subVarConfig: any, parentVal: string) => {
    console.log("HierarchicalMapping: renderSubvariableInput", subVarName, subVarConfig, parentVal); // ADDED
    const subVarValue = (value[parentVal] as any)?.[subVarName] ?? subVarConfig.default;

    const handleSubvariableChange = (newValue: any) => {
      onChange({
        ...value,
        [parentVal]: {
          ...(value[parentVal] as any),
          [subVarName]: newValue,
        },
      });
    };

    switch (subVarConfig.type) {
      case 'string':
        return <StringInput name={subVarName} value={subVarValue} config={subVarConfig} onChange={handleSubvariableChange} />;
      case 'number':
      case 'integer':
      case 'float':
        return <NumberInput name={subVarName} value={subVarValue} config={subVarConfig} onChange={handleSubvariableChange} />;
      case 'boolean':
        return <BooleanInput name={subVarName} value={subVarValue} config={subVarConfig} onChange={handleSubvariableChange} />;
      case 'array':
        return <ArrayInput name={subVarName} value={subVarValue} config={subVarConfig} onChange={handleSubvariableChange} />;
      default:
        return <Box>{`Unsupported type: ${subVarConfig.type}`}</Box>;
    }
  };

  return (
    <Box width="100%">
      <SimpleGrid columns={2} gap={4} width="100%">
        {/* Keys/Groups Section */}
        <Box borderWidth={1} borderRadius="md" p={4}>
          <Heading size="sm" mb={4}>Groups</Heading>
          <VStack gap={2}>
            {Object.entries(value).map(([parentVal, parentData]) => {
              const children = Array.isArray(parentData)
                ? parentData
                : (parentData?.values || []);

              return (
                <Box key={parentVal} width="100%" p={4} borderWidth={1} borderRadius="md">
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <AutoComplete
                      value={parentVal}
                      openOnFocus
                      suggestWhenEmpty
                      creatable={creatableKey}
                      onSelectOption={(item) => handleSelectParent(item, parentVal)}
                    >
                      <AutoCompleteInput placeholder="Select parent..." />
                      <AutoCompleteList>
                        {parentOptions?.map((opt: any) => (
                          <AutoCompleteItem key={opt} value={opt}>
                            {opt}
                          </AutoCompleteItem>
                        ))}
                        {creatableKey && (
                          <AutoCompleteCreatable>
                            {({ value }) => `Add "${value}"`}
                          </AutoCompleteCreatable>
                        )}
                      </AutoCompleteList>
                    </AutoComplete>
                    <IconButton
                      aria-label="Remove Group"
                      size="sm"
                      onClick={() => handleRemoveGroup(parentVal)}
                    >
                      <LuX />
                    </IconButton>
                  </Box>

                  {/* Values Container */}
                  <Box mt={2} borderWidth={1} borderRadius="md" p={2} bg="gray.50">
                    <DndContext
                      sensors={sensors}
                      collisionDetection={closestCenter}
                      onDragEnd={(event) => handleDragEnd(event, parentVal)}
                    >
                      <SortableContext
                        items={children}
                        strategy={verticalListSortingStrategy}
                      >
                        <VStack gap={2} minHeight="100px">
                          {children.map((child) => (
                            <Box key={child} display="flex" alignItems="center" gap={2} p={2} borderWidth="1px" borderRadius="md" bg="white">
                              <SortableItem
                                id={child}
                                value={child}
                                type={valueType}
                                onValueChange={(newChild) => handleEditChild(parentVal, child, newChild)}
                              />
                              <IconButton
                                aria-label="Remove Child"
                                size="sm"
                                onClick={() => handleRemoveChild(parentVal, child)}
                              >
                                <LuX />
                              </IconButton>
                            </Box>
                          ))}
                        </VStack>
                      </SortableContext>
                    </DndContext>

                    {/* Value Selection */}
                    <Box mt={2}>
                      <AutoComplete
                        multiple
                        value={children}
                        maxSelections={constraints.value_array_len}
                        openOnFocus
                        suggestWhenEmpty
                        creatable={creatableValue}
                        onSelectOption={({ item }) => {
                          if (children.includes(item.value)) return;
                          const newChildren = [...children, item.value];
                          if (!constraints.value_array_len ||
                            newChildren.length <= constraints.value_array_len) {
                            onChange({
                              ...value,
                              [parentVal]: newChildren
                            });
                          }
                        }}
                      >
                        <AutoCompleteInput
                          placeholder={`Add values (max ${constraints.value_array_len || '∞'})`}
                        />
                        <AutoCompleteList>
                          {childOptions?.map((opt: any) => (
                            <AutoCompleteItem key={opt} value={opt}>
                              {opt}
                            </AutoCompleteItem>
                          ))}
                          {creatableValue && (
                            <AutoCompleteCreatable>
                              {({ value }) => `Add "${value}"`}
                            </AutoCompleteCreatable>
                          )}
                        </AutoCompleteList>
                      </AutoComplete>
                    </Box>

                    {/* Subvariables */}
                    {Object.entries(subvariables).map(([subVarName, subVarConfig]) => (
                      <Box key={subVarName} mt={4}>
                        <Heading size="xs" mb={2}>{subVarName}</Heading>
                        {renderSubvariableInput(subVarName, subVarConfig, parentVal)}
                      </Box>
                    ))}
                  </Box>
                </Box>
              );
            })}
          </VStack>

          {/* Add New Group Button */}
          {(!parentOptions || creatableKey) && (
            <Button onClick={handleAddGroup} disabled={newParentKey !== null} mt={4}>
              Add New Group
            </Button>
          )}
        </Box>

        {/* Available Values Section */}
        <Box borderWidth={1} borderRadius="md" p={4}>
          <Heading size="sm" mb={4}>Available Values</Heading>
          <VStack gap={2}>
            {childOptions?.filter((opt: any) =>
              !Object.values(value).some(children =>
                children.includes(String(opt))
              )
            ).map((opt: React.Key | null | undefined) => (
              <Box
                key={opt}
                p={2}
                borderWidth={1}
                borderRadius="md"
                width="100%"
                cursor="grab"
              >
                {String(opt)}
              </Box>
            ))}
          </VStack>

          {/* Add New Value Button */}
          {creatableValue && (
            <Button onClick={handleAddValue} disabled={newValue !== null} mt={4}>
              Add New Value
            </Button>
          )}
        </Box>
      </SimpleGrid>

      {/* New Group Input */}
      {newParentKey !== null && (
        <Box width="100%" p={4} borderWidth={1} borderRadius="md">
          <AutoComplete
            ref={autoCompleteRef}
            openOnFocus
            suggestWhenEmpty
            creatable={creatableKey}
            onSelectOption={handleSelectNewParent}
          >
            <AutoCompleteInput
              onBlur={() => setNewParentKey(null)}
              placeholder="Enter new group name..." />
            <AutoCompleteList>
              {parentOptions?.map((opt: any) => (
                <AutoCompleteItem key={opt} value={opt}>
                  {opt}
                </AutoCompleteItem>
              ))}
              {creatableKey && (
                <AutoCompleteCreatable>
                  {({ value }) => `Add "${value}"`}
                </AutoCompleteCreatable>
              )}
            </AutoCompleteList>
          </AutoComplete>
        </Box>
      )}

      {/* New Value Input */}
      {newValue !== null && (
        <Box width="100%" p={4} borderWidth={1} borderRadius="md">
          <AutoComplete
            ref={autoCompleteRef}
            openOnFocus
            suggestWhenEmpty
            creatable={creatableValue}
            onSelectOption={handleSelectNewValue}
          >
            <AutoCompleteInput
              onBlur={() => setNewValue(null)}
              placeholder="Enter new value..." />
            <AutoCompleteList>
              {childOptions?.map((opt: any) => (
                <AutoCompleteItem key={opt} value={opt}>
                  {opt}
                </AutoCompleteItem>
              ))}
              {creatableValue && (
                <AutoCompleteCreatable>
                  {({ value }) => `Add "${value}"`}
                </AutoCompleteCreatable>
              )}
            </AutoCompleteList>
          </AutoComplete>
        </Box>
      )}
    </Box>
  );
};

export const HierarchicalMapping: React.FC<HierarchicalMappingProps> = ({
  name,
  value,
  config,
  onChange,
}) => {
  return (
    <NestedMapping
      name={name}
      value={value}
      config={config}
      onChange={onChange}
    />
  );
};
