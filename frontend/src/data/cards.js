export const cardCategories = [
  {
    title: "Academic Information",
    cards: [
      {
        id: "admission_updates",
        title: "Admission Updates",
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
        id: "examinations",
        title: "Examinations",
        icon: "📝",
        type: "chat",
        question:
          "Tell me about examinations.",
      },
      {
        id: "latest_notices",

        title: "Latest Notices",

        icon: "📢",

        type: "page",

        route: "/latest-notices"
      }
    ],
  },

  {
    title: "College Resources",
    cards: [
      {
        id: "academic_calendar",
        title: "Academic Calendar",
        icon: "📅",
        type: "page",
        route: "/academic-calendar"
      },
      {
        id: "document_library",
        title: "Document Library",
        icon: "📄",
        type: "page",
        route: "/document-library"
      },
    ],
  },

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
      {
        id: "events",
        title: "Events & Workshops",
        icon: "🎤",
        type: "page",
        route: "/events"
      },
    ],
  },

  {
    title: "Student Services",
    cards: [
      {
        id: "faq",
        title: "FAQ",
        icon: "❓",
        type: "chat",
        question:
          "Show me the frequently asked questions about the college.",
      },
      {
        id: "contact_us",
        title: "Contact Us",
        icon: "📞",
        type: "static",
        content: {
          address:
            "Government College for Women, M.A Road Srinagar",
          phone:
            "0194-2479432",
          email:
            "gcwmaroad@gmail.com",
          timing:
            "Monday - Saturday, 10 AM - 4 PM"
        }
      }
      // {
      //   id: "contact_us",
      //   title: "Contact Us",
      //   icon: "📞",
      //   type: "page"
      //   // question:
      //   //   "Provide the official contact details of the college.",
      // },
    ],
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
    ],
  },
];