from PIL import Image
import io

def concatenate_bmp_images(image_paths):
    """
    Concatenates a list of BMP images into a single image.

    Args:
        image_paths: list
            A list containing paths to BMP images.

    Returns:
        PIL.Image
            The concatenated image.
    """
    images = []
    for path in image_paths:
        with open(path, 'rb') as f:
            img_data = io.BytesIO(f.read())
            img = Image.open(img_data)
            images.append(img)

    # Assuming all images have the same width
    total_width = images[0].width
    total_height = sum(img.height for img in images)

    concatenated_image = Image.new('RGB', (total_width, total_height))

    y_offset = 0
    for img in images:
        concatenated_image.paste(img, (0, y_offset))
        y_offset += img.height

    return concatenated_image
