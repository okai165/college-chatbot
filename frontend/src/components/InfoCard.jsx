import "./../styles/infoCard.css";

function InfoCard({

    title,

    summary,

    type,

    date,

    url

}){

    return(

        <div className="info-card">

            <div className="info-content">

                <h3>{title}</h3>

                {summary && (

                    <p className="summary">

                        {summary.length > 220
                            ? summary.substring(0,220) + "..."
                            : summary}

                    </p>

                )}

                {type &&

                    <span className="badge">

                        {type}

                    </span>

                }

                {date &&

                    <p>

                        📅 {date}

                    </p>

                }

            </div>

            <a

                href={url}

                target="_blank"

                rel="noreferrer"

                className="open-btn"

            >

                Open

            </a>

        </div>

    );

}

export default InfoCard;