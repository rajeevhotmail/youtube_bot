import random
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery

# Set the scopes required for accessing the YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Load the OAuth 2.0 client credentials file
CLIENT_SECRET_FILE = "credential.json"

# Authenticate and get credentials
def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

# Authenticate and build the YouTube API client
credentials = get_credentials()
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

# Function to get live chat ID from a video ID
def get_live_chat_id(video_id):
    response = youtube.videos().list(
        part="liveStreamingDetails",
        id=video_id
    ).execute()

    if "items" in response and response["items"]:
        live_chat_id = response["items"][0].get("liveStreamingDetails", {}).get("activeLiveChatId")
        if live_chat_id:
            return live_chat_id
        else:
            raise Exception("No active live chat found for this video.")
    else:
        raise Exception("Video not found or does not have live chat.")

# Function to fetch live chat messages
def fetch_live_chat_messages(live_chat_id):
    response = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails"
    ).execute()
    return response.get("items", [])

# Function to post a message to live chat
def post_message(live_chat_id, message):
    request = youtube.liveChatMessages().insert(
        part="snippet",
        body={
            "snippet": {
                "liveChatId": live_chat_id,
                "type": "textMessageEvent",
                "textMessageDetails": {"messageText": message},
            }
        },
    )
    response = request.execute()
    print("Message posted:", message)

# List of abusive words (extend this list as needed)
abusive_words = ["abuse1", "abuse2", "offensiveWord"]

# Check for abuse in the chat messages
def detect_and_warn_abuse(live_chat_id, messages):
    for message in messages:
        text = message["snippet"]["textMessageDetails"]["messageText"]
        author_name = message["authorDetails"]["displayName"]

        # Check for abusive words
        if any(word in text.lower() for word in abusive_words):
            warning_message = f"@{author_name}, please maintain respect in the chat!"
            post_message(live_chat_id, warning_message)
            print(f"Warning sent to {author_name} for message: {text}")

# Specify the video ID of the live stream
video_id = "YOUR_VIDEO_ID_HERE"  # Replace with the actual video ID

# Main loop
try:
    # Get the live chat ID
    live_chat_id = get_live_chat_id(video_id)
    print("Live Chat ID:", live_chat_id)

    while True:
        # Fetch live chat messages
        messages = fetch_live_chat_messages(live_chat_id)

        # Detect and warn abusive messages
        detect_and_warn_abuse(live_chat_id, messages)

        # Wait for a few seconds before fetching new messages
        time.sleep(10)

except Exception as e:
    print("Error:", e)
