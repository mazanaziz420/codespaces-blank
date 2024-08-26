from imagekitio import ImageKit
from config import Config

class ImageUploadingService:
    def __init__(self):
        self.imagekit = ImageKit(
            private_key=Config.IMAGEKIT_PRIVATE_KEY,
            public_key=Config.IMAGEKIT_PUBLIC_KEY,
            url_endpoint=Config.IMAGEKIT_URL_ENDPOINT
        )

    def upload_image(self, file, file_name):
        try:
            result = self.imagekit.upload_file(
                file=file,
                file_name=file_name,
            )
            if result and result.url:
                return result.url
            else:
                raise Exception("Image upload failed: URL not found in result")

        
        except Exception as e:
            raise Exception(f"Image upload failed: {str(e)}")
