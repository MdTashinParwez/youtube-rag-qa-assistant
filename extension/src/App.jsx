import { useEffect, useState } from "react";

import { Send, Sparkles, Play } from "lucide-react";

import ReactMarkdown from "react-markdown";

import "./App.css";

function App() {
  const [videoId, setVideoId] = useState(null);

  const [status, setStatus] = useState("idle");

  const [question, setQuestion] = useState("");

  const [messages, setMessages] = useState([]);

  const [chatLoading, setChatLoading] = useState(false);

  // Format seconds into MM:SS
  const formatTime = (seconds) => {
    const totalSeconds = Math.floor(seconds);
    const minutes = Math.floor(totalSeconds / 60);
    const remainingSeconds = totalSeconds % 60;

    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  };

  const analyzeVideo = async (id) => {
    try {
      setStatus("analyzing");

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/video/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            videoId: id,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.message || "Video analysis failed"
        );
      }

      console.log("Video analyzed:", data);

      setStatus("ready");
    } catch (error) {
      console.error("Analysis failed:", error);

      setStatus("error");
    }
  };

  // --------------------------------
  // Ask Question
  // --------------------------------

  const askQuestion = async (text) => {
    const userQuestion = text.trim();

    if (
      !userQuestion ||
      !videoId ||
      chatLoading ||
      status !== "ready"
    ) {
      return;
    }

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setQuestion("");

    setChatLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/video/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            videoId,
            question: userQuestion,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.message || "Could not get an answer"
        );
      }

      // Add AI response
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (error) {
      console.error("Chat failed:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't answer that right now.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // --------------------------------
  // Video Detection
  // --------------------------------

  useEffect(() => {
    // Panel open hote hi current video ID lo
    chrome.runtime.sendMessage(
      {
        type: "GET_CURRENT_VIDEO",
      },
      (response) => {
        if (response?.videoId) {
          setVideoId(response.videoId);

          setMessages([]);

          analyzeVideo(response.videoId);
        }
      }
    );

    // Future video changes listen karo
    const handleMessage = (message) => {
      if (message.type === "VIDEO_ID_UPDATED") {
        setVideoId(message.videoId);

        // New video ke liye old chat clear
        setMessages([]);

        setQuestion("");

        analyzeVideo(message.videoId);
      }
    };

    chrome.runtime.onMessage.addListener(handleMessage);

    return () => {
      chrome.runtime.onMessage.removeListener(handleMessage);
    };
  }, []);

  // --------------------------------
  // UI
  // --------------------------------

  return (
    <div className="app">

      {/* Header */}

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

      {/* Main Content */}

      <main className="content">

        {/* Current Video */}

        <div className="video-card">

          <div className="video-icon">
            <Play size={18} />
          </div>

          <div>

            <p className="label">
              CURRENT VIDEO
            </p>

            <h2>
              {videoId || "No video detected"}
            </h2>

            <span>

              {!videoId &&
                "Open a YouTube video to get started"}

              {videoId &&
                status === "analyzing" &&
                "Preparing video..."}

              {videoId &&
                status === "ready" &&
                "Video ready"}

              {videoId &&
                status === "error" &&
                "Could not analyze video"}

            </span>

          </div>

        </div>

        {/* No Messages */}

        {messages.length === 0 ? (

          <>

            <div className="welcome">

              <Sparkles size={28} />

              <h2>
                Ask anything about this video
              </h2>

              <p>
                I can explain concepts, summarize
                the video, find important points and
                answer questions using the video's
                content.
              </p>

            </div>

            {/* Example Questions */}

            <div className="suggestions">

              <button
                onClick={() =>
                  askQuestion(
                    "Summarize this video"
                  )
                }
                disabled={
                  !videoId ||
                  status !== "ready" ||
                  chatLoading
                }
              >
                Summarize this video
              </button>

              <button
                onClick={() =>
                  askQuestion(
                    "What are the main concepts?"
                  )
                }
                disabled={
                  !videoId ||
                  status !== "ready" ||
                  chatLoading
                }
              >
                What are the main concepts?
              </button>

              <button
                onClick={() =>
                  askQuestion(
                    "Explain this video like I'm a beginner"
                  )
                }
                disabled={
                  !videoId ||
                  status !== "ready" ||
                  chatLoading
                }
              >
                Explain this like I'm a beginner
              </button>

            </div>

          </>

        ) : (

          /* Chat */

          <div className="chat">

            {messages.map((message, index) => (

              <div
                key={index}
                className={`message ${message.role}`}
              >

                <div className="message-content">

                  {message.role === "assistant" ? (

                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>

                  ) : (

                    message.content

                  )}

                </div>

                {/* Sources */}

                {message.sources &&
                  message.sources.length > 0 && (

                    <div className="sources">

                      <span>
                        Sources
                      </span>

                      {message.sources.map(
                        (source, sourceIndex) => (

                          <button
                            key={sourceIndex}
                            title={`${source.start_time}s - ${source.end_time}s`}
                            onClick={() => {
                              chrome.runtime.sendMessage({
                                type: "SEEK_VIDEO",
                                time: source.start_time,
                              });
                            }}
                          >
                            {formatTime(source.start_time)}
                          </button>

                        )
                      )}

                    </div>

                  )}

              </div>

            ))}

            {/* AI Loading */}

            {chatLoading && (

              <div className="message assistant">

                <div className="message-content thinking">
                  Thinking...
                </div>

              </div>

            )}

          </div>

        )}

      </main>

      {/* Input */}

      <footer className="input-area">

        <textarea
          value={question}
          onChange={(e) =>
            setQuestion(e.target.value)
          }
          onKeyDown={(e) => {

            if (
              e.key === "Enter" &&
              !e.shiftKey
            ) {

              e.preventDefault();

              askQuestion(question);

            }

          }}
          placeholder={
            videoId
              ? "Ask about this video..."
              : "Open a YouTube video first..."
          }
          rows="2"
          disabled={
            !videoId ||
            status !== "ready" ||
            chatLoading
          }
        />

        <button
          className="send"
          onClick={() =>
            askQuestion(question)
          }
          disabled={
            !question.trim() ||
            !videoId ||
            status !== "ready" ||
            chatLoading
          }
        >
          <Send size={18} />
        </button>

      </footer>

    </div>
  );
}

export default App;