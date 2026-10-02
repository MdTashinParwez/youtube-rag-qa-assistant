let currentVideoId = null;
let currentTabId = null;

chrome.runtime.onMessage.addListener(
  (message, sender, sendResponse) => {

    
    if (message.type === "YOUTUBE_VIDEO_DETECTED") {

      currentVideoId = message.videoId;

      // YouTube tab ka ID save karo
      currentTabId = sender.tab?.id;

      console.log(
        "YouTube video detected:",
        currentVideoId
      );

      console.log(
        "YouTube tab:",
        currentTabId
      );

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

    if (message.type === "SEEK_VIDEO") {

      if (currentTabId == null) {
        return;
      }

      chrome.tabs.sendMessage(
        currentTabId,
        {
          type: "SEEK_VIDEO",
          time: message.time,
        }
      ).catch((error) => {
        console.error(
          "Could not seek video:",
          error
        );
      });
    }


    return true;
  }
)