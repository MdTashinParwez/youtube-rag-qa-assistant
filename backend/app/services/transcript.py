from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id: str):
    try:
        ytt_api = YouTubeTranscriptApi()

        transcript = ytt_api.fetch(
            video_id,
            # languages=["en"]
        )

        transcript_data = []

        for snippet in transcript:
            transcript_data.append({
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration
            })

        return transcript_data

    except Exception as e:
        raise Exception(
            f"Could not fetch transcript: {str(e)}"
        )