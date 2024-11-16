import openai
import requests
from PIL import Image
from io import BytesIO

from PIL.Image import Resampling
from openai import OpenAI
from gradio_client import Client
import os
import requests


# Function to upload image to Imgur
def upload_image_to_imgur(image_path):
    client_id = os.getenv('IMGUR_CLIENT_ID')
    headers = {"Authorization": f"Client-ID {client_id}"}
    url = "https://api.imgur.com/3/image"

    with open(image_path, 'rb') as img:
        response = requests.post(url, headers=headers, files={'image': img})

    # Check if the upload was successful
    if response.status_code == 200:
        data = response.json()
        return data['data']['link']  # Return the URL of the uploaded image
    else:
        raise Exception(f"Failed to upload image to Imgur: {response.status_code}, {response.text}")


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

    def generate_image_flux(self, prompt):

        client = Client("black-forest-labs/FLUX.1-schnell")
        result = client.predict(
            prompt=prompt,
            seed=0,
            randomize_seed=True,
            width=1024,
            height=1024,
            num_inference_steps=4,
            api_name="/infer"
        )
        return result[0]

    def convert_webp_to_jpeg(self, input_path, output_path=None):
        """
        Convert a WebP image to JPEG format.

        Args:
            input_path (str): Path to the input WebP image
            output_path (str, optional): Path for the output JPEG image. If not provided,
                                       will replace .webp extension with .jpg

        Returns:
            str: Path to the converted JPEG image
        """
        # If no output path is specified, replace .webp with .jpg
        if output_path is None:
            output_path = input_path.rsplit('.', 1)[0] + '.jpg'

        # Open and convert the image
        img = Image.open(input_path)
        # Convert to RGB mode if necessary (in case of RGBA images)
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background

        # Save as JPEG
        img.save(output_path, 'JPEG', quality=95)
        return output_path

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
        image_path = self.generate_image(prompt)
        # img = self.download_image(image_url)
        # img = img.resize(target_size, Resampling.LANCZOS)
        image_path = self.convert_webp_to_jpeg(image_path)
        return upload_image_to_imgur(image_path=image_path)

    def generate_facebook_ad_post(self, prompt):
        """
        Generate an image optimized for a Facebook ad post.
        """
        target_size = "1080x1920"
        image_path = self.generate_image_flux(prompt)
        # img = self.download_image(image_url)
        # img = self.resize_and_crop(img, target_size)
        image_path = self.convert_webp_to_jpeg(image_path)
        print(image_path)
        return upload_image_to_imgur(image_path=image_path)

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
