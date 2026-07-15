import "./../styles/staticPopup.css";

function StaticPopup({ selectedStaticCard, closePopup }) {
  return (
    <div className="static-popup">
      <h2>{selectedStaticCard.title}</h2>

      {selectedStaticCard.type === "static" ? (
        <>
          <p>📍 {selectedStaticCard.content.address}</p>
          <p>📞 {selectedStaticCard.content.phone}</p>
          <p>✉️ {selectedStaticCard.content.email}</p>
          <p>🕒 {selectedStaticCard.content.timing}</p>
        </>
      ) : (
        selectedStaticCard.content.map((member, index) => (
          <div key={index} className="committee-member">
            <h4>{member.name}</h4>

            <p>
              <strong>Role:</strong> {member.role}
            </p>

            <p>
              <strong>Department:</strong> {member.department || "N/A"}
            </p>

            {member.email && <p>✉️ {member.email}</p>}

            {member.phone && <p>📞 {member.phone}</p>}

            <hr />
          </div>
        ))
      )}

      <button onClick={closePopup}>Close</button>
    </div>
  );
}

export default StaticPopup;