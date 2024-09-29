import re
import cv2
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


# Function to convert MM:SS format to seconds
def time_to_seconds(timestamp):
    minutes, seconds = map(int, timestamp.split(':'))
    return minutes * 60 + seconds


# Function to capture frame at a specific timestamp
def capture_frame_at_timestamp(video_path, timestamp, output_dir="frames"):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Convert timestamp to seconds
    target_time_in_seconds = time_to_seconds(timestamp)

    # Load the video using OpenCV
    video = cv2.VideoCapture(video_path)

    # Check if video loaded successfully
    if not video.isOpened():
        raise FileNotFoundError(f"Error: Could not open video file {video_path}")

    # Get the video's frame rate (frames per second)
    fps = video.get(cv2.CAP_PROP_FPS)

    # Calculate the target frame number
    target_frame = int(target_time_in_seconds * fps)

    # Set the video position to the target frame
    video.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

    # Read the frame at that position
    success, frame = video.read()

    # If we successfully retrieved the frame, save it as an image
    if success:
        frame_filename = f'frame_at_{timestamp.replace(":", "_")}.png'
        frame_path = os.path.join(output_dir, frame_filename)

        # Save the frame as an image file
        cv2.imwrite(frame_path, frame)

        # Release the video capture object
        video.release()

        # Return the local file path or generated URL (adjust accordingly)
        return frame_path  # You could return a URL here if hosted online
    else:
        video.release()
        raise ValueError(f"Could not retrieve frame at {timestamp}")


# Function to replace image timestamps in markdown text with URLs to the frames
def replace_image_placeholders(markdown_text, video_path, image_base_url="http://example.com/frames/"):
    # Regex pattern to find placeholders like %image_timestamp=00:37%
    pattern = r"%image_timestamp=(\d{2}:\d{2})%"

    # Function to replace each match with the image URL
    def replace_match(match):
        timestamp = match.group(1)

        try:
            # Capture the frame at the given timestamp
            local_image_path = capture_frame_at_timestamp(video_path, timestamp)

            # Upload the captured frame to Imgur
            image_url = upload_image_to_imgur(local_image_path)

            # delete the local image file
            os.remove(local_image_path)
            # Replace the placeholder with the markdown image link
            return f"![Frame at {timestamp}]({image_url})"
        except Exception as e:
            print(f"Error capturing frame at {timestamp}: {e}")
            return match.group(0)  # Return the original placeholder in case of failure

    # Replace all placeholders in the markdown text
    return re.sub(pattern, replace_match, markdown_text)
