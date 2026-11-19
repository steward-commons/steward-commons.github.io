# Steward Commons (front porch)

This is the public homepage for the [Steward Commons](https://github.com/steward-commons) project: a small, open front porch of free tools.

A retired U.S. Army veteran and his AI built these tools and give them away under the MIT license. The live site is https://steward-commons.github.io, served by GitHub Pages from this repository.

## What's in this folder

- `index.html` and `style.css` — the whole site. No build step, no trackers, no outside fonts or script hosts, and no cookies.
- `llms.txt` — a short, plain summary of the porch for AI visitors. Informational only.
- `favicon.svg` — a tiny porch icon.
- `LICENSE` — MIT, same holder line as the other Commons repos.
- `tests/` — a small standard-library check that repo links are real, the HTML parses, and a privacy scrub is clean.

## Preview

Open `index.html` in a browser. That is the whole site.

## Tests

```
python3 -m unittest discover -s tests
```

## Updating the live site

The site is already live at https://steward-commons.github.io/. Further updates are staged in this folder first. Nothing goes up until a human says so.

To publish a staged change:

1. A human reviews the files in this folder.
2. Push the reviewed files to the default branch (`main`) of the `steward-commons/steward-commons.github.io` repository.
3. GitHub Pages serves the default branch, folder `/` (root), at `https://steward-commons.github.io/`.
