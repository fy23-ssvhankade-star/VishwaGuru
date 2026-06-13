## 2025-05-18 - [Correct Image Orientation & EXIF Stripping]
**Learning:** `PIL.Image.new()` followed by `.paste()` to strip EXIF data is extremely inefficient (allocates full image copy). Also, simply stripping EXIF without handling orientation (`exif_transpose`) results in incorrectly rotated images if the original had an orientation tag.
**Action:** Use `ImageOps.exif_transpose(img)` first to bake in orientation, then simply `del img.info['exif']` to strip metadata in-place before saving. This is faster, uses less memory, and is correct.
