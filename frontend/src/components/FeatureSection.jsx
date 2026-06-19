import FeatureCard from "./FeatureCard";

function FeatureSection({
  title,
  cards,
  onCardClick
}) {

  return (
    <section className="section">

      <h2>{title}</h2>

      <div className="cards-grid">

        {cards.map((card) => (

          <FeatureCard
            key={card.title}
            title={card.title}
            icon={card.icon}
            onClick={() =>
              onCardClick(card.title)
            }
          />

        ))}

      </div>

    </section>
  );
}

export default FeatureSection;