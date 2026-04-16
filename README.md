# NovaOps Studio: High-Performance Scalable PyQt6 Template

A production-oriented starter repository for building modern, fast, and highly scalable Qt Widgets desktop applications.

This template is intentionally **domain-neutral**: it is not an inventory app.
It gives you a reusable architecture for ERP/CRM/HR/Operations platforms with a modern UI shell, runtime theming, and a high-performance `QTableView` stack.

---

## 1) Why This Template Exists

`PyQt-Fluent-Widgets` can look good, but in large enterprise apps it may feel heavy depending on widget count, style complexity, and runtime theme behavior.

This repo is optimized for:

- Performance-first rendering
- Fast runtime theme switching
- Low refactor pressure over time
- Predictable modular growth
- Clear separation between UI, theming, and business logic

---

## 2) Deep Research Summary (Actionable)

### Qt-Material

Strengths:
- Mature theme catalog (`dark_*.xml`, `light_*.xml`)
- Runtime theme APIs (`apply_stylesheet`, runtime menu/dock helpers)
- Token-like XML color system + export flow for `.qss`/resources
- Good developer ergonomics for rapid theming

Weaknesses:
- Broad global QSS can become expensive in very large widget trees
- Theming model is tied to material assumptions (not always enterprise-neutral)
- Last significant repository activity is relatively old

Performance implications:
- Full app stylesheet replace triggers re-polish/repaint costs
- Dynamic properties/class-based styling is flexible but can increase style recomputation if overused

Extensibility/Maintainability:
- Easy to start, harder to keep minimal at scale unless you trim selectors

Stealable patterns:
- Theme presets + runtime switch UX
- Extra semantic button variants (`danger/success/warning`)
- Exportable style artifacts

Actionable takeaway:
- Use material-like **token contracts**, but keep your runtime QSS surface small and targeted.

---

### PyQtDarkTheme

Strengths:
- Clear API (`setup_theme`, `load_palette`, `load_stylesheet`)
- Supports dark/light + OS sync concepts
- Explicit split between palette and stylesheet concepts
- Cross-binding support patterns

Weaknesses:
- Project’s latest release cadence is older
- Broad style coverage can still become heavy in very large apps

Performance implications:
- Centralized setup API is good; repeated full-style application should be minimized

Extensibility/Maintainability:
- Good conceptual model (palette + stylesheet layering)

Stealable patterns:
- Hybrid theming API
- Accent customization pathway
- “Complete setup” convenience function

Actionable takeaway:
- Keep a **single theme manager** with cache + explicit mode/accent state.

---

### QDarkStyleSheet (baseline)

Strengths:
- Very complete widget coverage
- SCSS/palette evolution and large ecosystem usage
- Supports both Python and C++ workflows

Weaknesses:
- Large stylesheet surface can be costly
- Legacy compatibility goals can add complexity

Performance implications:
- Great baseline aesthetics, but full global QSS is often too broad for high-scale custom apps

Extensibility/Maintainability:
- Good reference implementation; avoid copying large style payloads blindly

Stealable patterns:
- Structured palette thinking
- Consistent widget state definitions
- Example gallery/checklist mindset

Actionable takeaway:
- Prefer **focused internal design system** over importing massive generic QSS as-is.

---

### qt-modern-style (2026 package profile)

Strengths:
- Clean modern look, one-line apply API
- Built-in icon strategy
- Good for quick visual uplift

Weaknesses:
- Not always opinionated enough for complex modular enterprise architecture
- Needs internal guardrails for long-term scaling

Performance implications:
- Similar to other global-QSS approaches: cheap to start, can become costly with deep customization

Stealable patterns:
- Icon packaging API ergonomics
- Utility-style helper surface (`get_icon`, `list_icons`)

Actionable takeaway:
- Copy API ergonomics, not monolithic styling assumptions.

---

## 3) Qt Performance Rules (Non-Negotiable)

### QPalette vs QSS

Use `QPalette` for:
- Global semantic colors (`Window`, `Base`, `Text`, `Highlight`, `AlternateBase`, disabled roles)
- Fast broad color shifts with lower selector pressure

Use QSS for:
- Structural/visual details palette cannot express (border radius, control-specific states, subcontrols)
- Small, controlled set of selectors

Rule:
- `QPalette` as base theme layer, **QSS as thin enhancement layer**.

---

### QSS selector cost control

Do:
- Prefer type selectors and small property selectors (`QPushButton[primary="true"]`)
- Keep selector depth shallow
- Group similar controls in one rule block where reasonable

Avoid:
- Deep descendant chains (`A B C D E`)
- Excessive `#objectName` targeting across many widgets
- Frequent dynamic property churn on large widget trees
- Giant all-in-one QSS files without modular separation

---

### Runtime theme switching

Do:
- Keep one `ThemeManager`
- Cache stylesheet strings by `(mode, accent)` key
- Skip apply if mode/accent unchanged

Avoid:
- Rebuilding style strings every user action
- Reapplying the whole stylesheet on irrelevant state changes

---

### Large-data UI rules

Use:
- `QTableView + QAbstractTableModel`
- `QSortFilterProxyModel` for filtering/sorting
- User sort role (e.g., `SORT_ROLE`) for numeric accuracy
- Incremental loading (`canFetchMore`/`fetchMore`) for huge datasets

Avoid:
- `QTableWidget` for large production data grids
- Expensive delegates/effects unless required
- Frequent full model resets when targeted updates are possible

---

## 4) Architecture (Reusable Across Projects)

```text
mystock/
  app/
    bootstrap.py
  core/
    app_context.py
    config.py
    constants.py
    event_bus.py
    logging.py
    settings.py
    table_model.py
  data/
    fake_records.py
  docs/
    screenshots/
      main_dark.png
      main_light.png
  i18n/
    __init__.py
  modules/
    base.py
    registry.py
    dashboard/
      page.py
    datagrid/
      model.py
      proxy.py
      page.py
    settings/
      page.py
  resources/
    icons/
      *.svg
  services/
    icons.py
  themes/
    tokens.py
    palettes.py
    qss_builder.py
    manager.py
  ui/
    shell/
      main_window.py
  widgets/
    cards.py
    controls.py
  run.py
  requirements.txt
```

---

## 5) Dependency Boundaries

Rules:
- `core` must not import `ui` or `modules`
- `themes` can depend on `core/constants`, never on feature modules
- `modules/*` can use `core`, `themes`, `widgets`, `services`, `data`
- `ui/shell` coordinates modules; module internals should stay module-local
- `services` holds reusable cross-module helpers (icons, APIs, adapters)

Recommended import direction:
- outward UI depends on inward core; not the inverse

---

## 6) How Theme Engine Works

Pipeline:
1. `themes/tokens.py`: builds semantic tokens from `(mode, accent)`
2. `themes/palettes.py`: maps tokens to `QPalette` roles
3. `themes/qss_builder.py`: emits compact QSS for shape/state/subcontrol styling
4. `themes/manager.py`: applies palette + cached QSS at runtime

Caching strategy:
- key = `"{mode}:{accent}"`
- if stylesheet exists in cache, reuse it
- only rebuild when mode/accent changes

---

## 7) How Generic Data Grid Works

Files:
- `core/table_model.py`: generic schema-based model (`TableColumn`, `DynamicTableModel`)
- `modules/datagrid/model.py`: declarative column schema for demo rows
- `modules/datagrid/proxy.py`: reusable filter/sort proxy behavior
- `modules/datagrid/page.py`: UI controls + table wiring

Why this is scalable:
- No static `if column == ...` chains
- Columns are configuration, not hardcoded branching
- New modules can reuse the same model base and define only schema + formatting

---

## 8) Run Instructions

Install:

```bash
pip install -r requirements.txt
```

Run app:

```bash
python3 run.py
```

Optional runtime args:

```bash
python3 run.py --theme dark
python3 run.py --theme light --accent "#0B9AAE"
python3 run.py --rtl
```

Generate screenshot and exit:

```bash
python3 run.py --screenshot docs/screenshots/main_dark.png --theme dark
python3 run.py --screenshot docs/screenshots/main_light.png --theme light
```

---

## 9) Screenshots

- Dark UI: `docs/screenshots/main_dark.png`
- Light UI: `docs/screenshots/main_light.png`

---

## 10) How to Add a New Module

1. Create `modules/<module_name>/page.py`
2. Build page as `QWidget` subclass
3. Register in `modules/registry.py` as `ModuleSpec`
4. Provide icon name in `resources/icons`
5. Done (shell loads module lazily)

---

## 11) How to Add a Reusable Widget

1. Add component in `widgets/`
2. Keep style semantic (use properties like `primary`, `danger`, `muted`)
3. Avoid inline style unless truly local
4. Export via `widgets/__init__.py`

---

## 12) How to Create a New Theme Variant

1. Extend token calculation in `themes/tokens.py`
2. Keep role semantics stable (`text_primary`, `surface`, `border`, etc.)
3. Ensure `accent_contrast` remains readable
4. Validate both dark/light contrast states

---

## 13) Common Mistakes to Avoid

- Treating QSS as business logic storage
- Overusing objectName selectors
- Resetting model too often for tiny updates
- Styling every widget instance separately
- Ignoring disabled/selected/hover state contrast
- Calling model APIs from worker threads directly

---

## 14) Why This Is Future-Proof

- Domain-neutral naming (`DataGrid` not `Inventory`)
- Declarative table schema
- Single source of truth for theme state
- Layered architecture with strict boundaries
- Snapshot-ready UI for rapid visual iteration

---

## 15) Improved Prompt (Arabic + English, optimized)

Use this prompt when you want to regenerate/extend this architecture in a new repository:

```text
أريدك أن تبني لي مستودع Qt Widgets احترافي عالي الأداء وقابل للتوسع السريع، مناسب لأي نظام كبير (ERP/CRM/HR/Inventory...) وليس مخصصًا لمجال واحد.

المتطلبات الأساسية:
1) اعمل بحث عميق جدًا على:
   - Qt-Material
   - PyQtDarkTheme
   - qt-modern-style
   - QDarkStyleSheet (baseline)
   - أفضل ممارسات Qt الرسمية حول QSS/QPalette وModel/View performance

2) استخرج من البحث:
   - نقاط القوة والضعف
   - الأثر على الأداء
   - القابلية للتوسعة والصيانة
   - الأفكار القابلة للاقتباس (tokens, palette, icon pipeline, runtime switching)

3) ابنِ بنية مشروع عامة reusable بهذا التقسيم:
   - core, themes, ui/shell, widgets, modules, services, data, resources, i18n, docs
   - ضع boundaries واضحة بين الطبقات

4) نفّذ Demo runnable حقيقي (UI-only):
   - MainWindow: Sidebar + Topbar + Stacked Pages
   - Pages generic: Dashboard / DataGrid / Settings
   - Runtime Theme Switching: Dark/Light + Accent
   - DataGrid: QTableView + QAbstractTableModel + QSortFilterProxyModel + fake data كبير

5) قواعد الأداء (إلزامية):
   - متى نستخدم QPalette ومتى QSS
   - تقليل تكلفة selectors وإعادة polish
   - caching للـQSS
   - lazy loading للصفحات الثقيلة
   - قواعد واضحة للجداول الكبيرة

6) أضف screenshots تلقائية من التطبيق.

7) اكتب README عميق جدًا يتضمن:
   - فلسفة التصميم
   - كيفية التشغيل
   - كيفية إضافة module/page/widget/theme
   - Performance checklist + anti-patterns

8) الكود يجب أن يكون production-like، نظيف، منظم، وسهل النسخ لمشاريع أخرى.

9) إذا توقفت قبل الإكمال، اسألني حرفيًا:
   "Do you want me to continue? (Yes/No)"
```

---

## 16) Next Recommended Step

Copy this repository as your internal base template and start each new product by adding module folders only, while keeping `core/themes/ui-shell` stable.
