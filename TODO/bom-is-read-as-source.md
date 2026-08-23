# A UTF-8 BOM is censused as a line of code

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
```

## Objective

A UTF-8 BOM is censused as a line of code.

## Tasks

- [ ] `census.py` reads with `encoding='utf-8'` where it needs `utf-8-sig`.
      `'\ufeff'.strip()` is truthy, so `code_lines` keeps the BOM as a phantom
      code line.
- [ ] MEASURED on a BOM'd `.c`: the census emits `@b0 interval ('\ufeff')` and
      `@c0 trailing-comment ('\ufeff')`, THREE `b` places for two real code lines,
      and `record.py --seed` hands block-context `{'anchor': '\ufeff'}`. The
      copyright header becomes a trailing comment BESIDE code.
- [ ] ! BOM is the Visual Studio and Windows PowerShell default for `.c`, `.cs`,
      `.cpp` and `.ps1`, so this is the common case on Roy's own platform.
