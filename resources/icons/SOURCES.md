# Icon Sources and Licenses

This project includes multiple open-source SVG icon packs.

## Included Packs

- Tabler Icons (outline): `resources/icons/tabler`
- Tabler Icons (filled): `resources/icons/tabler-filled`
- Lucide Icons: `resources/icons/lucide`
- Bootstrap Icons: `resources/icons/bootstrap`
- Heroicons (legacy flat copy): `resources/icons/heroicons/*.svg`
- Heroicons (split by style/size):
  - `resources/icons/heroicons/24-outline`
  - `resources/icons/heroicons/24-solid`
  - `resources/icons/heroicons/20-solid`
  - `resources/icons/heroicons/16-solid`

## Upstream Repositories

- Tabler Icons: https://github.com/tabler/tabler-icons
- Lucide: https://github.com/lucide-icons/lucide
- Bootstrap Icons: https://github.com/twbs/icons
- Heroicons: https://github.com/tailwindlabs/heroicons

## Licenses

- Tabler Icons: MIT
- Lucide: ISC
- Bootstrap Icons: MIT
- Heroicons: MIT

Please verify and keep upstream license files when redistributing this repository.

## Notes

- SVG files are stored as direct assets for easy Qt usage.
- For namespaced access in code, use folder-prefixed names when needed.
  - Example: `icon("tabler/device-mobile")`
  - Example: `icon("lucide/wifi-high")`
  - Example: `icon("heroicons/24-solid/home")`
