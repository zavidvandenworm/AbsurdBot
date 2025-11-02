from wand.exceptions import WandException
from wand.image import Image

from modules.logger import create_logger

logger = create_logger(__name__)

def adjust_image(image_path: str, out_path: str, brightness: float = 0, contrast: float = 0, sharpness: float = 0) -> bool:
    try:
        image = Image(file=image_path)
        image.brightness_contrast(brightness=brightness, contrast=contrast)

        if sharpness != 0:
            image.sharpen(sigma=sharpness)

        image.save(file=out_path)
        return True

    except WandException as error:
        logger.error(error)
        return False