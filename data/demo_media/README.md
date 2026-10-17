# Bundled demonstration media

This directory contains the **44 assets referenced by `data/legacy_seed.json` and four video caption sidecars**. They were copied from the original LearningSystem demo assets, preserving filenames and media content. Caption text is unchanged; its line endings are normalized to LF for Git. Unreferenced files and later user uploads are excluded.

`Uploads/` retains the layout expected by `import_legacy_demo --media-source`. The command copies these files into `backend/private_media/legacy/`. This source bundle is versioned so a fresh GitHub clone can reproduce the complete demo without the original ASP.NET application.

Do not upload live/private user files here. Runtime uploads remain under ignored `backend/private_media/`. No new third-party license is asserted by bundling these existing project assets.
