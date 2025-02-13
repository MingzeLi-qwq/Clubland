import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/club-dashboard/:club_id/" element={<Dashboard />} />
            </Routes>
        </Router>
    );
};

export default App;
