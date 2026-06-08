import {
  useState,
  useEffect,
  useRef
} from "react";
import "./App.css";
import {
  Routes,
  Route
} from "react-router-dom";

import ReactMarkdown from "react-markdown";

import AdminLogin from "./pages/AdminLogin";
import AdminHome from "./pages/AdminHome";
import Dashboard from "./pages/Dashboard";
import FacultyManager from "./pages/FacultyManager";
import UploadDocuments from "./pages/UploadDocuments";

function ChatWidget() {

  // =========================
  // STATES
  // =========================

  const [open, setOpen] = useState(false);

  // const [sidebarOpen, setSidebarOpen] =
  //   useState(window.innerWidth > 768);

  const [darkMode, setDarkMode] =
    useState(false);

  const [input, setInput] = useState("");

  const [messages, setMessages] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [typingText, setTypingText] =
    useState("");

  const [recentChats, setRecentChats] =
    useState(() => {

      const saved =
        localStorage.getItem(
          "recentChats"
        );

      return saved
        ? JSON.parse(saved)
        : [
            {
              id: "chat1",
              title: "New Chat"
            }
          ];
    });

  const [allChats, setAllChats] =
    useState(() => {

      const saved =
        localStorage.getItem(
          "allChats"
        );

      return saved
        ? JSON.parse(saved)
        : {
            chat1: []
          };
    });

  const [currentChatId, setCurrentChatId] =
    useState("chat1");

  const messagesEndRef =
    useRef(null);

  // =========================
  // SAVE TO LOCAL STORAGE
  // =========================

  useEffect(() => {

    localStorage.setItem(
      "recentChats",
      JSON.stringify(recentChats)
    );

  }, [recentChats]);

  useEffect(() => {

    localStorage.setItem(
      "allChats",
      JSON.stringify(allChats)
    );

  }, [allChats]);

  // =========================
  // AUTO SCROLL
  // =========================

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });

  }, [messages, typingText]);

  // =========================
  // LOAD CHAT
  // =========================

  useEffect(() => {

    setMessages(
      allChats[currentChatId] || []
    );

  }, [
    currentChatId,
    allChats
  ]);

  // =========================
  // TYPING EFFECT
  // =========================

  const typeMessage = (
    fullText,
    callback
  ) => {

    let index = 0;

    setTypingText("");

    const interval =
      setInterval(() => {

        index++;

        setTypingText(
          fullText.slice(0, index)
        );

        if (
          index >= fullText.length
        ) {

          clearInterval(interval);

          setTypingText("");

          callback(fullText);
        }

      }, 15);
  };

  // =========================
  // SEND MESSAGE
  // =========================

  const sendMessage =
    async (
      predefinedText = null
    ) => {

      const userMsg =
        predefinedText || input;

      if (!userMsg.trim()) return;

      setInput("");

      const updatedUserMessages = [
        ...(allChats[
          currentChatId
        ] || []),

        {
          role: "user",
          text: userMsg
        }
      ];

      setMessages(
        updatedUserMessages
      );

      setAllChats((prev) => ({
        ...prev,
        [currentChatId]:
          updatedUserMessages
      }));

      // AUTO TITLE

      setRecentChats((prev) =>
        prev.map((chat) => {

          if (
            chat.id ===
              currentChatId &&
            chat.title ===
              "New Chat"
          ) {

            return {
              ...chat,
              title:
                userMsg.slice(
                  0,
                  25
                ) +
                (userMsg.length >
                25
                  ? "..."
                  : "")
            };
          }

          return chat;
        })
      );

      setLoading(true);

      try {

        const res =
          await fetch(
            "http://127.0.0.1:8000/chat",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body: JSON.stringify({
                message: userMsg,
                session_id:
                  currentChatId
              })
            }
          );

        const data =
          await res.json();

        const aiText =
          data.response ||
          "No response received";

        typeMessage(
          aiText,
          (finalText) => {

            const updatedMessages =
              [
                ...updatedUserMessages,

                {
                  role:
                    "assistant",

                  text:
                    finalText
                }
              ];

            setMessages(
              updatedMessages
            );

            setAllChats(
              (prev) => ({
                ...prev,

                [currentChatId]:
                  updatedMessages
              })
            );
          }
        );

      } catch (err) {

        console.log(err);

        const errorText =
          "AI service is temporarily busy. Please try again.";

        typeMessage(
          errorText,
          (finalText) => {

            const updatedMessages =
              [
                ...updatedUserMessages,

                {
                  role:
                    "assistant",

                  text:
                    finalText
                }
              ];

            setMessages(
              updatedMessages
            );

            setAllChats(
              (prev) => ({
                ...prev,

                [currentChatId]:
                  updatedMessages
              })
            );
          }
        );

      } finally {

        setLoading(false);
      }
    };

  // =========================
  // NEW CHAT
  // =========================

  const createNewChat = () => {

  const newId = `chat_${Date.now()}`;

  const newChat = {
    id: newId,
    title: "New Chat"
  };

  // remove old chat history
  setRecentChats([newChat]);

  setAllChats({
    [newId]: []
  });

  setCurrentChatId(newId);

  setMessages([]);

  setInput("");

  localStorage.setItem(
    "recentChats",
    JSON.stringify([newChat])
  );

  localStorage.setItem(
    "allChats",
    JSON.stringify({
      [newId]: []
    })
  );
};

  // =========================
  // DELETE CHAT
  // =========================

  const deleteChat = (
    id,
    e
  ) => {

    e.stopPropagation();

    const filtered =
      recentChats.filter(
        (chat) =>
          chat.id !== id
      );

    setRecentChats(filtered);

    const updatedChats = {
      ...allChats
    };

    delete updatedChats[id];

    setAllChats(
      updatedChats
    );

    if (
      currentChatId === id
    ) {

      if (
        filtered.length > 0
      ) {

        setCurrentChatId(
          filtered[0].id
        );

      } else {

        createNewChat();
      }
    }
  };

  // =========================
  // RENAME CHAT
  // =========================

  const renameChat = (
    id,
    e
  ) => {

    e.stopPropagation();

    const newName =
      prompt(
        "Rename chat:"
      );

    if (!newName) return;

    setRecentChats((prev) =>
      prev.map((chat) =>
        chat.id === id
          ? {
              ...chat,
              title: newName
            }
          : chat
      )
    );
  };

  // =========================
  // VOICE INPUT
  // =========================

  // const startVoiceInput =
  //   () => {

  //     const SpeechRecognition =
  //       window.SpeechRecognition ||
  //       window.webkitSpeechRecognition;

  //     if (
  //       !SpeechRecognition
  //     ) {

  //       alert(
  //         "Voice recognition not supported"
  //       );

  //       return;
  //     }

  //     const recognition =
  //       new SpeechRecognition();

  //     recognition.lang =
  //       "en-US";

  //     recognition.start();

  //     recognition.onresult =
  //       (event) => {

  //         setInput(
  //           event.results[0][0]
  //             .transcript
  //         );
  //       };
  //   };

  // =========================
  // COLORS
  // =========================

  const colors = darkMode
    ? {
        bg: "#0f172a",
        panel: "#1e293b",
        text: "white",
        body: "#111827"
      }
    : {
        bg: "white",
        panel: "#f8fafc",
        text: "#0f172a",
        body: "#f1f5f9"
      };

  return (
  <div>
  {/* Landing Content */}
   {!open && (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        padding: "40px 20px",
        maxWidth: "900px",
        margin: "0 auto"
      }}    
    > 
    
  {/* College Logo */}
  {/* <img
    src="/college-logo.png"   // replace with your logo
    alt="GCW M.A Road"
    style={{
      width: "120px",
      height: "120px",
      objectFit: "contain",
      marginBottom: "15px"
    }}
  /> */}

  <h1
    style={{
      fontSize: "27px",
      fontWeight: "700",
      marginBottom: "12px"
    }}
  >
    Government College for Women M.A. Road Srinagar
  </h1>

  <p
    style={{
      fontSize: "22px",
      color: "#ced7e4",
      maxWidth: "700px",
      margin: "0 auto 30px"
    }}
  >
    Welcome to the College AI Assistant.
    
  </p>

  {/* Feature Cards */}
  <div className="feature-section">
    <h2 className="feature-title">You can explore</h2>

    <ul className="feature-list">
      <li>Faculty information and profiles</li>
      <li>Admission process and eligibility details</li>
      <li>Exam schedules and updates</li>
      <li>Campus facilities and announcements</li>
    </ul>
 </div>
</div>
)}
    {/* FLOAT BUTTON */}
    {!open && (
     <div className={`chat-fab ${open ? "active" : ""}`} onClick={() => setOpen(!open)}>
      <span>Click Here To Chat</span>
     </div>
    )}

    {/* CHAT WINDOW */}

    {open && (

      <div
        style={{
         position: "fixed",
          top: 0,
          left: 0,
          width: "100vw",
          height: "100vh",
          zIndex: 9999,
          display: "flex",
          flexDirection: "column",
          background: colors.bg,
          overflow: "hidden"
        }}
      >

        {/* SIDEBAR */}

      

        {/* MAIN AREA */}

        <div
          style={{
            height:
              "100%",

            display: "flex",

            flexDirection:
              "column",

            background:
              colors.panel
          }}
        >

          {/* HEADER */}

          <div
            style={{
              background:
                "linear-gradient(to right,#2563eb,#1d4ed8)",

              color: "white",

              padding: "18px",

              display: "flex",

              justifyContent:
                "space-between",

              alignItems:
                "center"
            }}
          >

            <div>

              <div
                style={{
                  fontWeight:
                    "700"
                }}
              >
                AI Assistant
              </div>

              <div
                style={{
                  fontSize:
                    "13px"
                }}
              >
                Online
              </div>

            </div>
            {/* <button
              onClick={createNewChat}
              style={{
                background: "#f1f5f9",
                color: "#1e293b",
                border: "1px solid #cbd5e1",
                borderRadius: "8px",
                padding: "8px 14px",
                cursor: "pointer",
                fontSize: "14px",
                fontWeight: "600",
                transition: "all 0.2s ease"
              }}
              onMouseEnter={(e) => {
                  e.target.style.background = "#e2e8f0";
              }}
                onMouseLeave={(e) => {
                  e.target.style.background = "#f1f5f9";
                }}
            >
              New chat 
            </button> */}
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px"

              }}
            >

              <button title="Change theme" 
                onClick={() =>
                  setDarkMode(
                    !darkMode
                  )
                }
                style={{
                  background:
                    "transparent",

                  border:
                    "none",

                  color:
                    "white",

                  cursor:
                    "pointer",
                  fontSize:
                    "25px"

                }}
              >
                {darkMode
                  ? "☀️"
                  : "🌙"}
              </button>
              <button
                onClick={createNewChat}
                style={{
                 background: "#eaf0f5",
                 color: "#1e293b",
                 border: "2px solid #50060d",
                 borderRadius: "6px",
                 padding: "6px 12px",
                 height: "34px",
                 cursor: "pointer",
                 fontSize: "13px",
                 fontWeight: "500",
                 display: "flex",
                 alignItems: "center",
                 justifyContent: "center"
                }}
              >
                New Chat
              </button>
              <button title="minimize"
                onClick={() =>
                  setOpen(false)
                }
                style={{
                  background:
                    "transparent",

                  border:
                    "none",

                  color:
                    "white",

                  cursor:
                    "pointer",
                  fontSize:
                    "60px"
                }}
              >
                -
              </button>

            </div>

          </div>

          {/* CHAT BODY */}

          <div
            style={{
              flex: 1,

              overflowY:
                "auto",

              padding: "20px",

              background:
                colors.body
            }}
          >

            {messages.map(
              (msg, i) => (

                <div
                  key={i}

                  style={{
                    display:
                      "flex",

                    justifyContent:
                      msg.role ===
                      "user"
                        ? "flex-end"
                        : "flex-start",

                    marginBottom:
                      "18px"
                  }}
                >

                  <div
                    style={{
                      padding:
                        "14px 18px",

                      borderRadius:
                        "16px",

                      maxWidth:
                        "85%",

                      background:
                        msg.role ===
                        "user"
                          ? "#2563eb"
                          : darkMode
                          ? "#1e293b"
                          : "white",

                      color:
                        msg.role ===
                        "user"
                          ? "white"
                          : colors.text
                    }}
                  >

                    <ReactMarkdown>
                      {msg.text}
                    </ReactMarkdown>

                  </div>

                </div>
              )
            )}

            {/* TYPING */}

            {typingText && (

              <div
                style={{
                  marginBottom:
                    "18px"
                }}
              >

                <div
                  style={{
                    padding:
                      "14px 18px",

                    borderRadius:
                      "16px",

                    background:
                      darkMode
                        ? "#1e293b"
                        : "white",

                    color:
                      colors.text,

                    maxWidth:
                      "85%"
                  }}
                >

                  <ReactMarkdown>
                    {typingText}
                  </ReactMarkdown>

                </div>

              </div>

            )}

            {/* LOADING */}

            {loading && (

              <div
                style={{
                  marginBottom:
                    "20px"
                }}
              >

                <div
                  style={{
                    width:
                      "40px",

                    height:
                      "40px",

                    border:
                      "4px solid #cbd5e1",

                    borderTop:
                      "4px solid #2563eb",

                    borderRadius:
                      "50%",

                    animation:
                      "spin 1s linear infinite"
                  }}
                />

              </div>

            )}

            <div
              ref={
                messagesEndRef
              }
            />

          </div>

          {/* INPUT */}

          <div
            style={{
              padding: "12px",

              background:
                colors.bg,

              borderTop:
                `1px solid ${colors.border}`,

              display: "flex",

              alignItems:
                "center",

              gap: "10px"
            }}
          >
            
            {/* INPUT */}

            <input
              className="chat-input"

              value={input}

              onChange={(e) =>
                setInput(
                  e.target.value
                )
              }

              onKeyDown={(e) => {

                if (
                  e.key ===
                  "Enter"
                ) {

                  sendMessage();
                }

              }}

              placeholder="Ask something..."

              style={{
                 flex: 1,
                 padding: "10px 14px",
                 borderRadius: "10px",
                 border: "1px solid #cbd5e1",
                 background: darkMode ? "#1e293b" : "#ffffff",
                 color: colors.text,
                 fontSize: "14px",
                 outline: "none"
              }}
            />

            {/* SEND BUTTON */}

            <button
              onClick={() =>
                sendMessage()
              }
              style={{
                padding: "10px 16px",
                background: "#2563eb",
                color: "white",
                border: "none",
                borderRadius: "10px",
                cursor: "pointer",
                fontWeight: "600",
                fontSize: "14px"       
              }}
            >
              Send
            </button>

          </div>

        </div>

      </div>

    )}

    {/* SPINNER STYLE */}

    <style>
      {`
        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }

          100% {
            transform: rotate(360deg);
          }
        }
      `}
    </style>

  </div>
);
}

export default function App() {

  return (

    <Routes>

      <Route
        path="/"
        element={<ChatWidget />}
      />

      <Route
        path="/admin"
        element={<AdminLogin />}
      />

      <Route
        path="/admin/home"
        element={<AdminHome />}
      />

      <Route
        path="/admin/dashboard"
        element={<Dashboard />}
      />

      <Route
        path="/admin/faculty"
        element={<FacultyManager />}
      />

      <Route
        path="/admin/upload"
        element={<UploadDocuments />}
      />

    </Routes>

  );
}