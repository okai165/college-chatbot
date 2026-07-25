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
// import HeroSection from "./components/HeroSection";
import FeatureSection from "./components/FeatureSection";
import { cardCategories } from "./data/cards";
// import Admissions from "./pages/Admissions";
import AdmissionsPage from "./pages/AdmissionsPage";
import { useNavigate } from "react-router-dom";
import AdmissionUpdatesPage from "./pages/AdmissionUpdatesPage";
import ActivitySchedulePage from "./pages/ActivitySchedulePage";
import EligibilityPage from "./pages/EligibilityPage";
import FeeStructurePage from "./pages/FeeStructurePage";
import DocumentChecklistPage from "./pages/DocumentChecklistPage";
import AvailableCoursesPage from "./pages/AvailableCoursesPage";
import AdmissionCommitteePage from "./pages/AdmissionCommitteePage";
import LatestNoticesPage from "./pages/LatestNoticesPage";
import AcademicCalendarPage from "./pages/AcademicCalendarPage";
import DocumentLibraryPage from "./pages/DocumentLibraryPage";
import EventsPage from "./pages/EventsPage";
import StaticPopup from "./components/StaticPopup";
import api from "./services/api";
import "./styles/cards.css";
import "./styles/hero.css";
import "./styles/home.css";
function ChatWidget() {

  // =========================
  // STATES
  // =========================

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] =
    useState(false);
  const [input, setInput] = useState("");
  const [chatVisible, setChatVisible] = useState(false);
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
  const messagesEndRef = useRef(null);

  const chatBodyRef = useRef(null);

  const [isAtBottom, setIsAtBottom] = useState(true);

  const [showScrollButton, setShowScrollButton] = useState(false);
  const handleScroll = () => {

    const container = chatBodyRef.current;

    if (!container) return;


    const bottom =
      container.scrollHeight -
      container.scrollTop -
      container.clientHeight < 50;


    setIsAtBottom(bottom);


    if (bottom) {
      setShowScrollButton(false);
    }

  };
  // =========================
  // SAVE TO LOCAL STORAGE
  // =========================
    const navigate = useNavigate();
  const [pendingQuestion, setPendingQuestion] = useState(null);
  const [selectedStaticCard, setSelectedStaticCard] = useState(null);
  const handleCardClick = async (card) => {

      console.log(card);

      switch (card.type) {

          case "page":

              navigate(card.route);

              break;

          case "chat":

              setSidebarOpen(false);

              setChatVisible(true);

              setPendingQuestion(card.question);

              break;

          case "api":

              alert(`${card.title} API will be connected in the next step.`);

              break;
          
            

          case "static":
          case "committee":
              setSelectedStaticCard(card);

              break;

          case "upcoming":

              alert(`${card.title} is coming soon 🚀`);

              break;

          default:

              console.warn("Unknown card type", card);

      }

  };
  useEffect(() => {
    if (chatVisible && pendingQuestion) {
        sendMessage(pendingQuestion);
        setPendingQuestion(null);
    }
}, [chatVisible, pendingQuestion]);
  
  // =========================
  // AUTO SCROLL
  // =========================

  useEffect(() => {

    if (isAtBottom) {

        messagesEndRef.current?.scrollIntoView({
            behavior:"smooth"
        });

    }

  }, [messages]);
    

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

        const { data } = await api.post("/chat", {
            message: userMsg,
            session_id: currentChatId,
        });

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
        body: "#111827",
        border: "#334155"
      }
    : {
        bg: "white",
        panel: "#f8fafc",
        text: "#0f172a",
        body: "#f1f5f9",
        border: "#cbd5e1"
      };

  return (
  <div className="app-layout">
     {selectedStaticCard && (
        <StaticPopup
            selectedStaticCard={selectedStaticCard}
            closePopup={() =>
                setSelectedStaticCard(null)
            }
        />
      )}
    {sidebarOpen ? (

        <aside className="sidebar">

            <div className="sidebar-header">

                <h2>AI Assistant</h2>

                <button className="close-sidebar" onClick={() => setSidebarOpen(false)}>
                    ✕
                </button>

            </div>

            {cardCategories.map((category) => (

                <FeatureSection
                    key={category.title}
                    title={category.title}
                    cards={category.cards}
                    onCardClick={handleCardClick}
                />

            ))}

        </aside>

    ) : (
        <div className="collapsed-sidebar">

          <button
              className="expand-sidebar-btn"
              onClick={() => setSidebarOpen(true)}
          >
              ☰ Click here for more options
          </button>

          <div className="sidebar-preview">

              <h3>Explore AI Assistant</h3>

              {/* <ul>
                  <li>Admission Updates</li>
                  <li>Courses</li>
                  <li>Scholarships</li>
                  <li>Examinations</li>
                  <li>Documents</li>
                  <li>Events</li>
                  <li>FAQ</li>
              </ul> */}

              <p>
                  Open the sidebar to access all student services and AI features.
                  like Admission Updates,Courses,Scholarships,Examinations,Documents,Events,FAQ and more.
              </p>

          </div>
       </div>
    )}
    {chatVisible && (
      <div
       className="chat-container"
      >
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
                  setChatVisible(false)
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
            ref={chatBodyRef}

            onScroll={handleScroll}

            style={{
              flex: 1,

              overflowY:"auto",

              padding:"20px",

              background:colors.body,

              position:"relative"
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
              <div style={{ marginBottom: "20px" }}>
                <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                  <span
                    style={{
                      width: "8px",
                      height: "8px",
                      backgroundColor: colors.text,
                      borderRadius: "50%",
                      animation: "bounce 1.2s infinite"
                    }}
                  ></span>
                  <span
                    style={{
                      width: "8px",
                      height: "8px",
                      backgroundColor: colors.text,
                      borderRadius: "50%",
                      animation: "bounce 1.2s infinite",
                      animationDelay: "0.2s"
                    }}
                  ></span>
                  <span
                    style={{
                      width: "8px",
                      height: "8px",
                      backgroundColor: colors.text,
                      borderRadius: "50%",
                      animation: "bounce 1.2s infinite",
                      animationDelay: "0.4s"
                    }}
                  ></span>
                </div>
              </div>
            )}

            {showScrollButton && (

            <button
              onClick={() => {

                messagesEndRef.current?.scrollIntoView({
                  behavior:"smooth"
                });

                setIsAtBottom(true);
                setShowScrollButton(false);

              }}

              style={{
                position:"absolute",

                bottom:"20px",

                right:"25px",

                padding:"10px 15px",

                borderRadius:"20px",

                border:"none",

                background:"#2563eb",

                color:"white",

                cursor:"pointer",

                fontWeight:"600",

                boxShadow:"0 5px 15px rgba(0,0,0,.2)"
              }}
            >
              ↓ New messages
            </button>

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
    {!chatVisible && (
       <button
        className="chat-fab"
         onClick={() => {
            setSidebarOpen(false);
            setChatVisible(true);
        }}
      >
        <div className="chat-icon">
          <span>G</span>
          <span>C</span>
          <span>W</span>
        </div>

        <div className="chat-content">
          <span className="chat-title">AI Assistant</span>
          <span className="chat-subtitle">Click here to chat</span>
        </div>
      </button>
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
      
      <Route
        path="/admissions"
        element={<AdmissionsPage />}
      />
      <Route
        path="/admission-updates"
        element={<AdmissionUpdatesPage />}
      />

      <Route
        path="/activity-schedule"
        element={<ActivitySchedulePage />}
      />

      <Route
        path="/eligibility"
        element={<EligibilityPage />}
      />

      <Route
        path="/fee-structure"
        element={<FeeStructurePage />}
      />

      <Route
        path="/document-checklist"
        element={<DocumentChecklistPage />}
      />

      <Route
        path="/available-courses"
        element={<AvailableCoursesPage />}
      />

      <Route
        path="/admission-committee"
        element={<AdmissionCommitteePage />}
      />
      <Route
        path="/latest-notices"
        element={<LatestNoticesPage />}
      />
      <Route
          path="/academic-calendar"
          element={<AcademicCalendarPage />}
      />

      <Route
          path="/document-library"
          element={<DocumentLibraryPage />}
      />

      <Route
          path="/events"
          element={<EventsPage />}
      />
    </Routes>

  );
}