import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Assistant from "./pages/Assistant";
import Cases from "./pages/Cases";
import Dashboard from "./pages/Dashboard";
import Evidence from "./pages/Evidence";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/assistant" replace />} />
        <Route path="/assistant" element={<Assistant />} />
        <Route path="/cases" element={<Cases />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/evidence" element={<Evidence />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;