from PIL import Image, ImageTk

def load_image(path, size=None):
    """
    Loads an image from the given path and resizes it if size is provided.
    Returns a PhotoImage object for Tkinter.
    """
    try:
        img = Image.open(path)
        if size:
            # Use LANCZOS for Pillow >= 10.0.0, fallback for older versions
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            img = img.resize(size, resample)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None
