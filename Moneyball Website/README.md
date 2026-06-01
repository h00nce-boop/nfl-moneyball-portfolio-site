# NFL Moneyball Combined Portfolio Site - V5

This version combines the dramatic visual style from the first HTML portfolio with the interactive model lab from the newer site.

## What changed in V5

- Linked Hannah's resume as `Hannah_Levy_Resume.pdf`.
- Restored the preferred About section copy and hoverable skill tags.
- Added a public findings section with readable, less technical takeaways.
- Added the stock-market-style ticker from the original portfolio concept.
- Added animated statistics/signal text in the hero background.
- Kept the Streamlit dashboard embedded, but wrapped it in a dark command-center shell so it visually matches the site.
- Renamed buttons with cleaner title case: `Open Interactive Model Lab`, `Stress Test the Signal`, and `View GitHub`.
- Upgraded the Cost vs Performance Map so hovering or clicking points shows a plain-English data preview.
- Kept the private update workflow out of the public page. The exporter remains in `tools/`.

## Files

- `index.html` - public website
- `site-data.js` - generated model data used by the interactive charts/cards
- `Hannah_Levy_Resume.pdf` - linked resume file
- `tools/build_site_data.py` - optional data exporter for future model updates

## Resume link

The contact section reads the resume URL from `site-data.js`:

```js
"resumeUrl": "Hannah_Levy_Resume.pdf"
```

Keep the PDF filename exactly the same unless you also update `site-data.js`.

## Preview locally

Open `index.html` in a browser, or run:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## Streamlit dark embed note

The portfolio iframe now requests Streamlit's dark embed option:

```text
?embed=true&embed_options=dark_theme
```

For the most consistent dark appearance, copy `STREAMLIT_DARK_THEME_CONFIG.toml` into your Streamlit app repository as `.streamlit/config.toml` and redeploy the Streamlit app.
