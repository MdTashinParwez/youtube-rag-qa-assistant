let currentVideoId = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "YOUTUBE_VIDEO_DETECTED") {
    currentVideoId = message.videoId;

    console.log("YouTube video detected:", currentVideoId);

    // Side panel ko new video ID bhejo
    chrome.runtime.sendMessage({
      type: "VIDEO_ID_UPDATED",
      videoId: currentVideoId,
    }).catch(() => {
      // Side panel open nahi hai, ignore
    });
  }

  if (message.type === "GET_CURRENT_VIDEO") {
    sendResponse({
      videoId: currentVideoId,
    });
  }

  return true;
});