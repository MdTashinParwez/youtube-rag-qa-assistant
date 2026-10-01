let lastVideoId = null;

function getVideoId() {
  const url = new URL(window.location.href);
  return url.searchParams.get("v");
}

function sendVideoId() {
  const videoId = getVideoId();

  if (!videoId || videoId === lastVideoId) {
    return;
  }

  lastVideoId = videoId;

  chrome.runtime.sendMessage({
    type: "YOUTUBE_VIDEO_DETECTED",
    videoId
  });
}

sendVideoId();

setInterval(sendVideoId, 2000);