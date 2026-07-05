import "./../styles/cards.css";

function FeatureCard({ title, icon, onClick }) {
  return (
    <div className="feature-card" onClick={onClick}>

        <div className="left">

            <span className="card-icon">
                {icon}
            </span>

            <span>{title}</span>

        </div>

        <span>›</span>

    </div>
  );
}

export default FeatureCard;