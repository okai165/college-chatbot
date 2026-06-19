import "./../styles/cards.css";

function FeatureCard({ title, icon, onClick }) {
  return (
    <div className="feature-card" onClick={onClick}>
      <div className="card-icon">{icon}</div>
      <h3>{title}</h3>
    </div>
  );
}

export default FeatureCard;