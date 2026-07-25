export const cardCategories = [
  {
    title: "Academic Information",
    cards: [
      {
        id: "admission_updates",
        title: "General notices",
        icon: "📢",
        type: "page",
        route: "/admission-updates",
      },
      // {
      //   id: "activity_schedule",
      //   title: "Activity Schedule",
      //   icon: "📅",
      //   type: "page",
      //   route: "/activity-schedule",
      // },
      // {
      //   id: "eligibility_criteria",
      //   title: "Eligibility Criteria",
      //   icon: "✅",
      //   type: "page",
      //   route: "/eligibility",
      // },
      {
        id: "fee_structure",
        title: "Fee Structure",
        icon: "💰",
        type: "page",
        route: "/fee-structure",
      },
      {
        id: "available_courses",
        title: "Available Courses",
        icon: "📚",
        type: "page",
        route: "/available-courses",
      },
      // {
      //   id: "admission_committee",
      //   title: "Admission Committee",
      //   icon: "👨‍🏫",
      //   type: "page",
      //   route: "/admission-committee",
      // },
      {
        id: "scholarships",
        title: "Scholarships",
        icon: "🏆",
        type: "chat",
        question:
          "Tell me about scholarships available in Government College for Women, M.A. Road Srinagar.",
      },
      {
        id: "examination ",
        title: "Examination cell",
        icon: "📝",
        type: "chat",
        question:
          "Examination cell details.",
      },
      // {
      //   id: "latest_notices",

      //   title: "Latest Notices",

      //   icon: "📢",

      //   type: "page",

      //   route: "/latest-notices"
      // }
    ],
  },

  // {
  //   title: "College Resources",
  //   cards: [
  //     {
  //       id: "academic_calendar",
  //       title: "Academic Calendar",
  //       icon: "📅",
  //       type: "page",
  //       route: "/academic-calendar"
  //     },
  //     {
  //       id: "document_library",
  //       title: "Document Library",
  //       icon: "📄",
  //       type: "page",
  //       route: "/document-library"
  //     },
  //   ],
  // },

  {
    title: "Campus Information",
    cards: [
      {
        id: "campus_facilities",
        title: "Campus Facilities",
        icon: "🏫",
        type: "chat",
        question:
          "Tell me about the campus facilities available in the college.",
      },
      // {
      //   id: "events",
      //   title: "Events & Workshops",
      //   icon: "🎤",
      //   type: "page",
      //   route: "/events"
      // },
    ],
  },

  {
    title: "Student Services",
    cards: [
      {
        id: "student_support_committee",
        title: "Student Support Committee",
        icon: "🤝",
        type: "committee",
        content: [
          {
            name: "Dr. Shakeel Ahmad",
            role: "Convener",
            department: "Computer Science",
            email: "shakeelulrehman2009@gmail.com",
            phone: "9906672263"
          },
          {
            name: "Prof. Majida Maqbool",
            role: "Co Convener",
            department: "Chemistry",
            email: "majidamaqbool72@gmail.com",
            phone: "9622818105"
          },
          {
            name: "Dr. Suzana Bashir",
            role: "Member Secretary",
            department: "Botany",
            email: "suzanabashir336@gmail.com",
            phone: "9419429475"
          },
          {
            name: "Dr. Abina Habib",
            role: "Member",
            department: "English",
            email: "abinahabib@gmail.com",
            phone: ""
          },
          {
            name: "Dr. Saleem Farooq",
            role: "Member Secretary",
            department: "Botany",
            email: "saleemiiim@gmail.com",
            phone: "8825095939"
          },
          {
            name: "Prof. Durafshan",
            role: "Member",
            department: "Computer Science",
            email: "durafshanmalik13@gmail.com",
            phone: ""
          },
          {
            name: "Dr. Tahira Sadiq",
            role: "Member",
            department: "Home Science",
            email: "tahirasidiq86@gmail.com",
            phone: ""
          },
          {
            name: "Dr. Shabir Ahmad Mir",
            role: "Member",
            department: "Food Science and Technology",
            email: "shabirahmir@gmail.com",
            phone: "7006973727"
          },
          {
            name: "Prof. Shahla Ayoub",
            role: "Member",
            department: "Economics",
            email: "shahla.ayoub05@gmail.com",
            phone: ""
          },
          {
            name: "Prof. Oveesa Farooq",
            role: "Member",
            department: "Functional English",
            email: "farooqoveesa@gmail.com",
            phone: ""
          },
          {
            name: "Prof. Syed Hamid Firdose",
            role: "Member",
            department: "Education",
            email: "syedhamidfirdose@gmail.com",
            phone: "6005811288"
          },
          {
            name: "Prof. Zahoor Ahmad Ganie",
            role: "Member",
            department: "Social Work",
            email: "zahoor1204@gmail.com",
            phone: "9906793223"
          },
          {
            name: "Prof. Mohd. Muzamil Bhat",
            role: "Member",
            department: "",
            email: "mmuzamilbhat@gmail.com",
            phone: ""
          }
        ]
      },
      {
        id: "contact_us",
        title: "Contact Us",
        icon: "📞",
        type: "static",
        content: {
          address: "Government College for Women, M.A Road Srinagar",
          phone: "0194-2479432",
          email: "gcwmaroad@gmail.com",
          timing: "Monday - Saturday, 10 AM - 4 PM"
        }
      }
    ]
  },

  {
  title: "Upcoming AI Features",
    cards: [
      {
        id: "voice_assistant",
        title: "Voice Assistant",
        icon: "🎙️",
        type: "upcoming",
        description:
          "Voice interaction with the AI assistant. Coming soon.",
      },
      {
        id: "multilingual_support",
        title: "Multilingual Support",
        icon: "🌐",
        type: "upcoming",
        description:
          "Chat with the assistant in multiple languages for improved accessibility. Coming soon.",
      },
      {
        id: "personalized_recommendations",
        title: "Personalized Recommendations",
        icon: "🎯",
        type: "upcoming",
        description:
          "Receive personalized suggestions based on your interests and academic needs. Coming soon.",
      },
      {
        id: "smart_document_search",
        title: "Smart Document Search",
        icon: "🔍",
        type: "upcoming",
        description:
          "Search notices, PDFs, and documents using natural language queries. Coming soon.",
      },
      {
        id: "AI Study Assistant",
        title: "AI Study Assistant",
        icon: "🤖",
        type: "upcoming",
        description:
          "Get AI-powered study guidance, summaries, and exam preparation assistance. Coming soon.",
      },
    ],
  }
];