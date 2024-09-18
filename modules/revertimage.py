"""
The issue you're encountering stems from how the bytes are being interpreted and stored
when converting the file into an image and then back. Specifically, when storing binary
data in an image, it can be affected by pixel alignment or format conversion in ways that
alter the original byte sequence, causing issues when you try to revert it.

To achieve what you want, we need to:

Ensure no changes are made to the byte content when encoding it as pixel data in the image.
Carefully manage padding and pixel formats to preserve the exact original bytes.
Solution:
We need to ensure the exact number of bytes in the original file is tracked, avoid any
pixel format conversions, and carefully map bytes into the image's pixel data.
"""
