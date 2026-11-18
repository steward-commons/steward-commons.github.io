# Steward Commons (front porch)

This is the public homepage for the [Steward Commons](https://github.com/steward-commons) project: a small, open front porch of free tools.

A retired U.S. Army veteran and his AI built these tools and give them away under the MIT license. The live site, once published, will be served by GitHub Pages from this repository.

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

## Going live

After a human has looked the page over:

1. Create a public repository named `steward-commons.github.io` under the `steward-commons` GitHub organization.
2. Push the files in this folder to the default branch (`main`).
3. In the repository Settings, open Pages and publish from the default branch, folder `/` (root). Organization sites at this name are served at `https://steward-commons.github.io/`.

Nothing goes up until a human says so.
