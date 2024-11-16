import io
import openai
import requests
from PIL import Image
from io import BytesIO
from PIL.Image import Resampling
from openai import OpenAI
from gradio_client import Client
import os
import requests
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class TooManyRequestsException(Exception):
    pass

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

    def generate_image_flux_hf(self, prompt, max_retries=5):
        """
        Generate an image using the FLUX.1-schnell model via Hugging Face API.
        Includes retry logic for rate limiting.

        Args:
            prompt (str): Text description of the image to generate
            max_retries (int): Maximum number of retry attempts

        Returns:
            str: Path to the generated image
        """
        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=60, max=120),
            retry=retry_if_exception_type(TooManyRequestsException)
        )
        def _generate_with_retry():
            API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

            # Make the API request
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})

            # Handle rate limiting
            if response.status_code == 429:
                print(f"Rate limited. Retrying in a few seconds...")
                raise TooManyRequestsException(response.text)

            # Check if the request was successful
            if response.status_code != 200:
                raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

            try:
                image = Image.open(io.BytesIO(response.content))

                # Create temp directory if it doesn't exist
                os.makedirs("temp", exist_ok=True)

                # Save the image temporarily
                temp_path = os.path.join("temp", f"temp_flux_{hash(prompt)}.png")
                image.save(temp_path)

                return temp_path
            except Exception as e:
                raise Exception(f"Failed to process image: {str(e)}\nAPI Response: {response.text}")

        try:
            return _generate_with_retry()
        except Exception as e:
            raise Exception(f"Failed to generate image after {max_retries} attempts: {str(e)}")

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
        image_path = self.generate_image_flux_hf(prompt)
        # img = self.download_image(image_url)
        # img = self.resize_and_crop(img, target_size)
        # image_path = self.convert_webp_to_jpeg(image_path)
        print(image_path)
        img_url = upload_image_to_imgur(image_path=image_path)
        if img_url:
            os.remove(image_path)
        return img_url


    def generate_facebook_ad_post(self, prompt):
        """
        Generate an image optimized for a Facebook ad post.
        """
        target_size = "1080x1920"
        image_path = self.generate_image_flux_hf(prompt)
        # img = self.download_image(image_url)
        # img = self.resize_and_crop(img, target_size)
        # image_path = self.convert_webp_to_jpeg(image_path)
        print(image_path)
        img_url = upload_image_to_imgur(image_path=image_path)
        if img_url:
            os.remove(image_path)
        return img_url

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
