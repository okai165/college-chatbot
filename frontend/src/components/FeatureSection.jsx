import FeatureCard from "./FeatureCard";

function FeatureSection({ title, cards, onCardClick }) {
  return (
    <div style={{ marginBottom: "20px", padding: "0 16px" }}>
      <h3
        style={{
          marginBottom: "12px",
          color: "#1e293b",
          fontSize: "18px",
          borderBottom: "1px solid #334155",
          paddingBottom: "6px",
        }}
      >
        {title}
      </h3>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        {cards.map((card) => (
          <FeatureCard
            key={card.id}
            title={card.title}
            icon={card.icon}
            onClick={() => onCardClick(card)}
          />
        ))}
      </div>
    </div>
  );
}

export default FeatureSection;