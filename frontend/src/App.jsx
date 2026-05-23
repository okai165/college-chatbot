import {
  useState,
  useEffect,
  useRef
} from "react";

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

  const [sidebarOpen, setSidebarOpen] =
    useState(window.innerWidth > 768);

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

    const newId =
      `chat_${Date.now()}`;

    const newChat = {
      id: newId,
      title: "New Chat"
    };

    setRecentChats((prev) => [
      newChat,
      ...prev
    ]);

    setAllChats((prev) => ({
      ...prev,
      [newId]: []
    }));

    setCurrentChatId(newId);

    setMessages([]);
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

  const startVoiceInput =
    () => {

      const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

      if (
        !SpeechRecognition
      ) {

        alert(
          "Voice recognition not supported"
        );

        return;
      }

      const recognition =
        new SpeechRecognition();

      recognition.lang =
        "en-US";

      recognition.start();

      recognition.onresult =
        (event) => {

          setInput(
            event.results[0][0]
              .transcript
          );
        };
    };

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

    {/* FLOAT BUTTON */}

    <div
      onClick={() => setOpen(!open)}
      style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        width: "65px",
        height: "65px",
        borderRadius: "50%",
        background: "#2563eb",
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "30px",
        cursor: "pointer",
        zIndex: 1000
      }}
    >
      💬
    </div>

    {/* CHAT WINDOW */}

    {open && (

      <div
        style={{
          position: "fixed",
          bottom:
            window.innerWidth < 768
              ? "0"
              : "90px",

          right:
            window.innerWidth < 768
              ? "0"
              : "20px",

          width:
            window.innerWidth < 768
              ? "100vw"
              : "900px",

          height:
            window.innerWidth < 768
              ? "100vh"
              : "493px",

          background: colors.bg,

          borderRadius:
            window.innerWidth < 768
              ? "0"
              : "14px",

          display: "flex",

          overflow: "hidden",

          zIndex: 1000
        }}
      >

        {/* SIDEBAR */}

        <div
          style={{
            width:
              sidebarOpen
                ? "280px"
                : "75px",

            background:
              darkMode
                ? "#020617"
                : "#0f172a",

            color: "white",

            display: "flex",

            flexDirection:
              "column"
          }}
        >

          {/* HEADER */}

          <div
            style={{
              padding: "20px",

              display: "flex",

              justifyContent:
                "space-between",

              alignItems:
                "center"
            }}
          >

            {sidebarOpen && (
              <span>
                Recent Chats
              </span>
            )}

            <button
              onClick={() =>
                setSidebarOpen(
                  !sidebarOpen
                )
              }
              style={{
                background:
                  "transparent",

                border: "none",

                color: "white",

                cursor:
                  "pointer",

                fontSize: "22px"
              }}
            >
              {sidebarOpen
                ? "✖"
                : "☰"}
            </button>

          </div>

          {/* NEW CHAT */}

          {sidebarOpen && (

            <button
              onClick={
                createNewChat
              }
              style={{
                margin:
                  "10px",

                padding:
                  "12px",

                background:
                  "#2563eb",

                border:
                  "none",

                color:
                  "white",

                borderRadius:
                  "10px",

                cursor:
                  "pointer"
              }}
            >
              + New Chat
            </button>

          )}

          {/* CHAT LIST */}

          <div
            style={{
              flex: 1,
              overflowY:
                "auto"
            }}
          >

            {recentChats.map(
              (chat) => (

                <div
                  key={chat.id}

                  onClick={() =>
                    setCurrentChatId(
                      chat.id
                    )
                  }

                  style={{
                    padding:
                      "14px",

                    cursor:
                      "pointer",

                    background:
                      currentChatId ===
                      chat.id
                        ? "#1e293b"
                        : "transparent",

                    display:
                      "flex",

                    alignItems:
                      "center",

                    justifyContent:
                      "space-between"
                  }}
                >

                  <span>
                    💬{" "}

                    {sidebarOpen &&
                      chat.title}
                  </span>

                  {sidebarOpen && (

                    <div
                      style={{
                        display:
                          "flex",

                        gap: "8px"
                      }}
                    >

                      <span
                        onClick={(
                          e
                        ) =>
                          renameChat(
                            chat.id,
                            e
                          )
                        }
                        style={{
                          cursor:
                            "pointer"
                        }}
                      >
                        ✏️
                      </span>

                      <span
                        onClick={(
                          e
                        ) =>
                          deleteChat(
                            chat.id,
                            e
                          )
                        }
                        style={{
                          cursor:
                            "pointer"
                        }}
                      >
                        🗑️
                      </span>

                    </div>

                  )}

                </div>
              )
            )}

          </div>

        </div>

        {/* MAIN AREA */}

        <div
          style={{
            flex: 1,

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

            <div
              style={{
                display:
                  "flex",

                gap: "15px"
              }}
            >

              <button
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
                    "pointer"
                }}
              >
                {darkMode
                  ? "☀️"
                  : "🌙"}
              </button>

              <button
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
                    "pointer"
                }}
              >
                ✖
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
              padding: "18px",

              background:
                colors.bg,

              borderTop:
                `1px solid ${colors.border}`,

              display: "flex",

              alignItems:
                "center",

              gap: "12px"
            }}
          >

            {/* MIC BUTTON */}

            <button
              onClick={
                startVoiceInput
              }
              style={{
                width: "52px",

                height: "52px",

                border: "none",

                borderRadius:
                  "12px",

                cursor:
                  "pointer",

                fontSize: "22px",

                background:
                  darkMode
                    ? "#3f3f46"
                    : "#e2e8f0",

                color:
                  darkMode
                    ? "white"
                    : "#0f172a",

                display: "flex",

                alignItems:
                  "center",

                justifyContent:
                  "center"
              }}
            >
              🎤
            </button>

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

                padding:
                  "15px 18px",

                borderRadius:
                  "12px",

                border:
                  `1px solid ${colors.border}`,

                background:
                  darkMode
                    ? "#3f3f46"
                    : "#f8fafc",

                color:
                  darkMode
                    ? "white"
                    : "#0f172a",

                outline:
                  "none",

                fontSize:
                  "15px"
              }}
            />

            {/* SEND BUTTON */}

            <button
              onClick={() =>
                sendMessage()
              }
              style={{
                padding:
                  "15px 22px",

                background:
                  "#2563eb",

                color:
                  "white",

                border:
                  "none",

                borderRadius:
                  "12px",

                cursor:
                  "pointer",

                fontWeight:
                  "700",

                fontSize:
                  "15px"
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