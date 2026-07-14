import "./../styles/staticPopup.css";

function StaticPopup({ selectedStaticCard, closePopup }) {

    return (

        <div className="static-popup">

            <h2>
                {selectedStaticCard.title}
            </h2>


            <p>
                📍 {selectedStaticCard.content.address}
            </p>


            <p>
                📞 {selectedStaticCard.content.phone}
            </p>


            <p>
                ✉️ {selectedStaticCard.content.email}
            </p>


            <p>
                🕒 {selectedStaticCard.content.timing}
            </p>


            <button onClick={closePopup}>
                Close
            </button>

        </div>

    );
}


export default StaticPopup;