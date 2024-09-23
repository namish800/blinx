import openai
import requests
from PIL import Image
from io import BytesIO

from PIL.Image import Resampling
from openai import OpenAI


class SocialMediaImageGenerator:
    def __init__(self):
        """
        Initialize the image generator with your OpenAI API key.
        """
        self.client = OpenAI()

    def generate_image(self, prompt, size=None):
        """
        Generate a square image using DALL·E based on the provided prompt.
        """
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url

    def download_image(self, image_url):
        """
        Download the image from the URL and return a PIL Image object.
        """
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        return img

    def resize_and_crop(self, img, target_size):
        """
        Resize and crop the image to fit the target size while maintaining aspect ratio.
        """
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        # Resize the image
        if img_ratio > target_ratio:
            # Image is wider than target aspect ratio
            new_height = target_size[1]
            new_width = int(new_height * img_ratio)
        else:
            # Image is taller than target aspect ratio
            new_width = target_size[0]
            new_height = int(new_width / img_ratio)

        img = img.resize((new_width, new_height), Resampling.LANCZOS)

        # Crop the image
        left = (new_width - target_size[0]) / 2
        top = (new_height - target_size[1]) / 2
        right = (new_width + target_size[0]) / 2
        bottom = (new_height + target_size[1]) / 2

        img = img.crop((left, top, right, bottom))
        return img

    def generate_instagram_post(self, prompt):
        """
        Generate an image optimized for an Instagram post.
        """
        # Instagram recommends 1080x1080 pixels (square)
        target_size = (1080, 1080)
        image_url = self.generate_image(prompt)
        img = self.download_image(image_url)
        img = img.resize(target_size, Resampling.LANCZOS)
        return img

    def generate_facebook_ad_post(self, prompt):
        """
        Generate an image optimized for a Facebook ad post.
        """
        target_size = "1080x1920"
        image_url = self.generate_image(prompt, target_size)
        # img = self.download_image(image_url)
        # img = self.resize_and_crop(img, target_size)
        return image_url

    def generate_twitter_post(self, prompt):
        """
        Generate an image optimized for a Twitter post.
        """
        # Twitter recommends 1200x675 pixels (16:9 aspect ratio)
        target_size = (1200, 675)
        image_url = self.generate_image(prompt)
        img = self.download_image(image_url)
        img = self.resize_and_crop(img, target_size)
        return img
