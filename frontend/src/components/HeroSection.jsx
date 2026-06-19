function HeroSection({ onChatOpen }) {
  return (
    <section className="hero">
      <h1>AI College Information Assistant</h1>

      <p>
        Get instant information about admissions,
        courses, examinations, scholarships and more.
      </p>

      <button onClick={onChatOpen}>
        🤖 Click Here To Chat
      </button>
    </section>
  );
}

export default HeroSection;