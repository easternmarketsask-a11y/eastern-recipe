# Recipe favourites and ingredient cart implementation plan

Goal: heart immediately before share on both detail variants; primary purchase action adds published, delivery-eligible required ingredients to the existing cart.
Architecture: recipe site links to group-order with recipe ID and unique request ID; authenticated website loads trusted recipe data and resolves exact ingredient codes through the existing public product API. Cart transaction records the request ID atomically with the merged items. No order is submitted.

- [x] Test ingredient resolution: required only, exact codes, unavailable/missing products skipped, duplicate IDs collapsed, network errors fail without writes.
- [x] Implement resolver, import status/retry UI and idempotent cart mutation. Preserve login return URL and existing cart.
- [x] Replace wide favourite controls with accessible SVG heart before share; persist favourites across SPA and static pages; generate static pages and bump assets.
- [x] Verify unit tests, TypeScript/build, browser desktop/mobile and duplicate-request behavior. Review only scoped changes. Commit locally; push requires explicit approval following the prior automatic review rejection.

Quantity: user chose recipe-based conversion. Convert grams/kg/lb/jin to pounds for weighed products; round packages up from recipe weight and unambiguous product package size. Explicit package counts take priority. Unknown sizes default to one with a visible notice.

Validation: 28 recipe unit tests, 7 resolver/transaction tests; Chrome 390px and 1280px checks for static and SPA detail, toggle persistence, purchase URL and repeat-click token. Cross-origin recipe JSON fetch verified from production store origin (200, 126 recipes). TypeScript and production build passed. Existing GroupOrder ESLint findings are outside this change; new modules and modified cart hook pass. No live member cart writes performed. Independent review found repeat-purchase token reuse; reproduced with a failing browser regression and fixed with a fresh token for later activations and bfcache returns. Immediate double clicks retain the same token. All four browser scenarios pass after the fix.
