import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import PublicView from "./pages/PublicView";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/club-dashboard/:club_id/" element={<Dashboard />} />
                <Route path="/club-view/:club_id" element={<PublicView />} />
            </Routes>
        </Router>
    );
};

export default App;
