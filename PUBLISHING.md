# How to Publish `chronicle-ai` to PyPI

Since you are new to publishing, here is a step-by-step guide to getting your library on PyPI (The Python Package Index).

## Prerequisites

1.  **PyPI Account**: Go to [pypi.org](https://pypi.org/) and create an account if you haven't already.
2.  **API Token**:
    *   Log in to PyPI.
    *   Go to **Account settings**.
    *   Scroll to **API tokens** and select **Add API token**.
    *   Token name: `chronicle-publisher` (or similar).
    *   Scope: "Entire account" (for the first publish).
    *   **Copy this token**. You will need it (it starts with `pypi-`).

## Step 1: Install Publishing Tools

You need `twine` to upload packages securely.

```bash
pip install twine
```

## Step 2: Build the Package

We have already configured `pyproject.toml` and `setup.py`. converting your source code into a detailed "wheel" and "source distribution" that PyPI understands.

Run this command from the project root:

```bash
# Clean old builds first (optional but recommended)
rm -rf dist/ build/ *.egg-info

# Build
python3 setup.py sdist bdist_wheel
```

You should now see a `dist/` folder containing `.whl` and `.tar.gz` files.

## Step 3: Check the Package (Recommended)

Twine can check if your package description will render correctly on PyPI.

```bash
twine check dist/*
```

## Step 4: Upload to TestPyPI (Optional but Safe)

If you want to try it out before the real deal, you can use TestPyPI.
1.  Register at [test.pypi.org](https://test.pypi.org/).
2.  Upload:
    ```bash
    twine upload --repository testpypi dist/*
    ```

## Step 5: Publish to Real PyPI 🚀

When you are ready to show the world:

```bash
twine upload dist/*
```

*   **Username**: `__token__` (literally type this string)
*   **Password**: Your PyPI API token (beginning with `pypi-...`)

## Success!

Once uploaded, anyone in the world can install your library:

```bash
pip install chronicle-ai
```

(Note: If the name `chronicle-ai` is taken, you will get an error. You might need to change the `name` in `setup.py` to something unique like `chronicle-py` or `chronicle-memory`.)
