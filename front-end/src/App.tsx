import { Grid } from "@mui/material";
import "./App.css";
import { HashRouter as Router, Routes, Route } from "react-router-dom";

import { Sidebar } from "./components/Sidebar";
import { Home } from "./components/Home";
import { Invoice } from "./components/Invoice/Invoice";
import NotFound from "./components/NotFound";

function App() {
  return (
    <>
      <Grid container spacing={2} justifyContent="center" alignItems="center">
        <Grid size={3}>
          <Sidebar />
        </Grid>
        <Grid size={9}>
          <Router>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/invoice" element={<Invoice />} />
              <Route path="/invoices/:invoiceNumber" element={<Invoice/>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Router>
        </Grid>
      </Grid>
    </>
  );
}

export default App;
