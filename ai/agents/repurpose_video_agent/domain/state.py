from typing import TypedDict


class VideoAnalyzerState(TypedDict):
    video_file_name: str
    summary: str
    key_points: str
    target_audience: str
    outline: str
    introduction: str
    blog_post: str
    keywords: str
    video_file_path: str
    seo_metadata: str


class OutputState(TypedDict):
    blog_post: str
    seo_metadata: str
