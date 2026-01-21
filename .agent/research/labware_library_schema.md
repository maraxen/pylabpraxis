# Labware Library Schema

## 1. Proposed JSON Schema

This schema is based on the existing `ResourceDefinitionOrm` model in the Praxis codebase.

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Praxis Labware Definition",
  "description": "A definition for a piece of labware in the Praxis ecosystem.",
  "type": "object",
  "properties": {
    "name": {
      "description": "A unique, human-readable name for the labware.",
      "type": "string"
    },
    "version": {
      "description": "The version of this labware definition.",
      "type": "integer",
      "minimum": 1
    },
    "isConsumable": {
      "description": "Whether this labware is a consumable.",
      "type": "boolean"
    },
    "nominalVolumeUl": {
      "description": "The nominal volume of the labware in microliters.",
      "type": "number"
    },
    "material": {
      "description": "The material the labware is made of.",
      "type": "string"
    },
    "manufacturer": {
      "description": "The manufacturer of the labware.",
      "type": "string"
    },
    "ordering": {
      "description": "Ordering information for the labware.",
      "type": "string"
    },
    "dimensions": {
      "description": "The dimensions of the labware in millimeters.",
      "type": "object",
      "properties": {
        "x": {
          "type": "number"
        },
        "y": {
          "type": "number"
        },
        "z": {
          "type": "number"
        }
      },
      "required": ["x", "y", "z"]
    },
    "model": {
      "description": "The model of the labware.",
      "type": "string"
    },
    "wells": {
      "description": "A list of wells in the labware.",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "description": "The name of the well (e.g., 'A1').",
            "type": "string"
          },
          "x": {
            "description": "The x-coordinate of the well in millimeters.",
            "type": "number"
          },
          "y": {
            "description": "The y-coordinate of the well in millimeters.",
            "type": "number"
          },
          "z": {
            "description": "The z-coordinate of the well in millimeters.",
            "type": "number"
          },
          "depth": {
            "description": "The depth of the well in millimeters.",
            "type": "number"
          },
          "diameter": {
            "description": "The diameter of the well in millimeters.",
            "type": "number"
          },
          "volume": {
            "description": "The volume of the well in microliters.",
            "type": "number"
          }
        },
        "required": ["name", "x", "y", "z", "depth", "volume"]
      }
    }
  },
  "required": ["name", "version", "dimensions"]
}
```

## 2. Comparison with Existing Standards

A search for existing labware standards from Opentrons, Hamilton, and SiLA2 did not yield definitive schema documentation. Therefore, the proposed schema is primarily based on the existing `ResourceDefinitionOrm` model in the Praxis codebase. This approach ensures that the labware definitions are compatible with the existing system.

Based on general knowledge of lab automation, other standards likely include similar fields, such as:

- **Metadata:** Name, version, manufacturer, etc.
- **Physical Dimensions:** Overall dimensions, well spacing, etc.
- **Well Properties:** Shape, depth, volume, etc.
- **Material Properties:** The material the labware is made of.

The proposed schema is designed to be extensible, allowing for the addition of new fields as needed.

## 3. Validation Rules

- **`name`**: Must be a unique string.
- **`version`**: Must be an integer greater than or equal to 1.
- **`dimensions`**: Must be an object with `x`, `y`, and `z` properties, which are all numbers.
- **`wells`**: If present, must be an array of objects, each with the required properties.

## 4. Submission Workflow Recommendation

We recommend a Git-based workflow for submitting new labware definitions:

1. **Fork the repository:** The user forks the Praxis repository on GitHub.
2. **Create a new branch:** The user creates a new branch for their labware definition.
3. **Add the labware definition:** The user adds a new JSON file to a designated `labware` directory.
4. **Submit a pull request:** The user submits a pull request to the main Praxis repository.
5. **Review and merge:** The Praxis team reviews the pull request and merges it if it meets the required standards.

## 5. Example Labware Definitions

### Example 1: 96-well plate

```json
{
  "name": "corning_96_wellplate_360ul_flat",
  "version": 1,
  "isConsumable": true,
  "nominalVolumeUl": 360,
  "material": "polystyrene",
  "manufacturer": "Corning",
  "ordering": "3635",
  "dimensions": {
    "x": 127.76,
    "y": 85.48,
    "z": 14.22
  },
  "model": "96-well plate",
  "wells": [
    {
      "name": "A1",
      "x": 14.38,
      "y": 11.24,
      "z": 10.67,
      "depth": 10.67,
      "diameter": 6.4,
      "volume": 360
    }
  ]
}
```

### Example 2: 1.5ml microcentrifuge tube

```json
{
  "name": "eppendorf_1.5ml_safelock_tube",
  "version": 1,
  "isConsumable": true,
  "nominalVolumeUl": 1500,
  "material": "polypropylene",
  "manufacturer": "Eppendorf",
  "ordering": "022363204",
  "dimensions": {
    "x": 10.8,
    "y": 10.8,
    "z": 38.4
  },
  "model": "1.5ml tube"
}
```
