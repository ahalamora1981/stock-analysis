import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import StockList from "./pages/StockList";
import Sectors from "./pages/Sectors";
import Positions from "./pages/Positions";
import Suggestions from "./pages/Suggestions";
import Settings from "./pages/Settings";
import "./styles/bmw-m-theme.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="stocks" element={<StockList />} />
          <Route path="stocks/:code" element={<StockList />} />
          <Route path="sectors" element={<Sectors />} />
          <Route path="positions" element={<Positions />} />
          <Route path="suggestions" element={<Suggestions />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
