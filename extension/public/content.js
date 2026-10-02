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

chrome.runtime.onMessage.addListener((message) => {

  if (message.type === "SEEK_VIDEO") {

    const video = document.querySelector("video");

    if (!video) {
      return;
    }

    video.currentTime = message.time;

    video.play().catch(() => {});
  }

});

sendVideoId();

setInterval(sendVideoId, 2000);