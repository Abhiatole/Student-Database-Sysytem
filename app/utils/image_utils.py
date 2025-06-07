from PIL import Image, ImageTk

def load_image(path, size=None):
    """
    Loads an image from the given path and resizes it if size is provided.
    Returns a PhotoImage object for Tkinter.
    """
    try:
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        return None
