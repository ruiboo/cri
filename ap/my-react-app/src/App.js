import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [planId, setPlanId] = useState("");
  const [year, setYear] = useState("");
  const [planData, setPlanData] = useState({});
  const [problematicClauses, setProblematicClauses] = useState([]);
  const [priceScore, setPriceScore] = useState(null);
  const [issuerRating, setIssuerRating] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/test", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ plan_id: planId, year: year }),
      });
      const data = await response.json();
      console.log(data);
      setPlanData(data);
      setProblematicClauses(data.problematic_clauses || []);
      setPriceScore(data.price_score);
      setIssuerRating(data.issuer_rating);
    } catch (error) {
      console.error("Error fetching data: ", error);
    }
  };

  const handleBack = () => {
    setPlanData({});
    setPlanId("");
    setYear("");
  };

  useEffect(() => {
    console.log("planData updated:", planData);
  }, [planData]);
  console.log(planData.grade);

  const getCircleColor = (grade) => {
    if (grade >= 80) {
      return "#4CAF50"; // Green for grades 80 and above
    } else if (grade >= 60) {
      return "#FFEB3B"; // Yellow for grades 60 to 79
    } else {
      return "#F44336"; // Red for grades below 60
    }
  };

  return (
    <div className="App">
      {planData && Object.keys(planData).length === 0 ? (
        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-group">
            <label>
              Plan ID:
              <input
                type="text"
                value={planId}
                onChange={(e) => setPlanId(e.target.value)}
              />
            </label>
          </div>
          <div className="input-group">
            <label>
              Year:
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
              />
            </label>
          </div>
          <button type="submit" className="submit-button">
            Submit
          </button>
        </form>
      ) : (
        <div>
          <div className="flex-container">
            {planData.plan_name && (
              <div className="plan-name-container">
                <div className="header">Plan Name:</div>
                <div>{planData.plan_name}</div>
              </div>
            )}
          </div>
          <div className="flex-container">
            {/* Grade Section */}
            {planData.grade !== undefined && (
              <div className="grade-container">
                <div className="header">Grade:</div>
                <div
                  className="grade-circle"
                  style={{ backgroundColor: getCircleColor(planData.grade) }}
                >
                  {planData.grade}
                </div>
              </div>
            )}

            <div className="flex-container">
              {/* Problematic Clauses Section */}
              <div className="problematic-container card left-align">
                <div className="sub-header">Problematic Clauses Detected:</div>
                {problematicClauses.length > 0 ? (
                  <ul>
                    {problematicClauses.map((clause, index) => (
                      <li key={index}>
                        <strong>Phrase:</strong> {clause.phrase} <br />
                        <strong>Location:</strong> {clause.path.join(" > ")}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No problematic clauses detected.</p>
                )}
                {priceScore !== null && (
                  <div>
                    <div className="sub-header">Price Score:</div>
                    <div>{priceScore}</div>
                  </div>
                )}

                {issuerRating !== null && (
                  <div>
                    <div className="sub-header">Issuer Rating:</div>
                    <div>{issuerRating}</div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <button onClick={handleBack} className="back-button">
            Back
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
