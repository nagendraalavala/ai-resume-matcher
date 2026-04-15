import { useState } from "react";
import UploadPage from "./components/UploadPage";
import ResultsDashboard from "./components/ResultsDashboard";
import type { AnalyzeResponse } from "./types";

function App() {
  const [results, setResults] = useState<AnalyzeResponse | null>(null);

  if (results) {
    return (
      <ResultsDashboard data={results} onBack={() => setResults(null)} />
    );
  }

  return <UploadPage onResults={setResults} />;
}

export default App;
