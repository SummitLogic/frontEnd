# Assets Folder

This folder contains static assets for the GateFlow Dashboard.

## Contents

- `logo.png` - Primary dashboard logo
- `logo2.png` - Alternative logo

## Usage

These images are used in the Streamlit application UI. The application references them via relative paths:

```python
assets/logo.png
assets/logo2.png
```

## Guidelines

- Keep images optimized for web (recommended: 400x80px for logos)
- Use PNG format for logos with transparency
- Avoid committing unnecessarily large files

## Note

User-generated data (like `users.json`) has been moved to the `data/` folder for better security and organization.

