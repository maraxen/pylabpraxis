# References

External references, best practices, and technical resources for Praxis development.

---

## Structure

```
references/
├── README.md           # This file
├── testing/            # Testing strategies, pytest/Vitest patterns
├── backend/            # FastAPI, SQLAlchemy, PyLabRobot patterns
├── frontend/           # Angular, RxJS, browser mode patterns
└── architecture/       # System design decisions
```

---

## Adding References

Use [templates/reference_document.md](../templates/reference_document.md) to document:

1. **Source and metadata** - URL, date added, category
2. **Summary** - Key points from the reference
3. **Takeaways** - Specific insights and recommendations
4. **Implementation notes** - How it applies to Praxis
5. **Related items** - Links to backlog items or other references

---

## When to Add a Reference

Add a reference document when:

- You discover a valuable external resource that influences design decisions
- A best practices guide is referenced multiple times in conversations
- External documentation clarifies a complex technical concept
- A performance optimization technique should be standardized

---

## Current References

| Reference | Category | Added |
|:----------|:---------|:------|
| [hardware_matrix.md](hardware_matrix.md) | Hardware | Pre-existing |
