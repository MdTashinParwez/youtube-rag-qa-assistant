import { useEffect, useState } from "react";
import { Send, Sparkles, Play } from "lucide-react";
import "./App.css";

function App() {
  const [videoId, setVideoId] = useState(null);

useEffect(() => {
  // Panel open hote hi current video ID lo
  chrome.runtime.sendMessage(
    { type: "GET_CURRENT_VIDEO" },
    (response) => {
      if (response?.videoId) {
        setVideoId(response.videoId);
      }
    }
  );

  // Future video changes listen karo
  const handleMessage = (message) => {
    if (message.type === "VIDEO_ID_UPDATED") {
      setVideoId(message.videoId);
    }
  };

  chrome.runtime.onMessage.addListener(handleMessage);

  return () => {
    chrome.runtime.onMessage.removeListener(handleMessage);
  };
}, []);

  return (
    <div className="app">

      <header className="header">
        <div className="brand">
          <div className="logo">
            <Sparkles size={18} />
          </div>

          <div>
            <h1>VideoMind</h1>
            <p>AI YouTube Assistant</p>
          </div>
        </div>
      </header>

      <main className="content">

        <div className="video-card">
          <div className="video-icon">
            <Play size={18} />
          </div>

          <div>
            <p className="label">CURRENT VIDEO</p>

            <h2>
              {videoId || "No video detected"}
            </h2>

            <span>
              {videoId
                ? "Video detected successfully"
                : "Open a YouTube video to get started"}
            </span>
          </div>
        </div>

        <div className="welcome">
          <Sparkles size={28} />

          <h2>Ask anything about this video</h2>

          <p>
            I can explain concepts, summarize the video,
            find important points and answer questions
            using the video's content.
          </p>
        </div>

        <div className="suggestions">

          <button>
            Summarize this video
          </button>

          <button>
            What are the main concepts?
          </button>

          <button>
            Explain this like I'm a beginner
          </button>

        </div>

      </main>

      <footer className="input-area">

        <textarea
          placeholder="Ask about this video..."
          rows="2"
        />

        <button className="send">
          <Send size={18} />
        </button>

      </footer>

    </div>
  );
}

export default App;