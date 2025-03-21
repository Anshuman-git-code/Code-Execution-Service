import React, { useState } from "react";
import axios from "axios";

function App() {
  const [code, setCode] = useState(""); // Store user code
  const [output, setOutput] = useState(""); // Store execution result

  const executeCode = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/execute", {
        code: code,
      });

      setOutput(response.data.output || response.data.error);
    } catch (error) {
      setOutput("Error executing code");
    }
  };

  return (
    <div style={{ width: "50%", margin: "auto", textAlign: "center", padding: "20px" }}>
      <h2>Code Execution Service</h2>
      <textarea
        rows="6"
        cols="50"
        placeholder="Write your code here..."
        value={code}
        onChange={(e) => setCode(e.target.value)}
        style={{ width: "100%", padding: "10px" }}
      />
      <br />
      <button onClick={executeCode} style={{ marginTop: "10px", padding: "10px" }}>Run Code</button>
      <h3>Output:</h3>
      <pre>{output}</pre>
    </div>
  );
}

export default App;