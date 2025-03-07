import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";
import { Link } from "react-router-dom";

const Dashboard = () => {
    const { club_id } = useParams();
    const [widgets, setWidgets] = useState<{ id: number, name: string, x: number, y: number, width: number, height: number }[]>([]);
    const [layout, setLayout] = useState<{ i: string, x: number, y: number, w: number, h: number }[]>([]);

    useEffect(() => {
        axios.get(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, { withCredentials: true })
            .then((res) => {
                setWidgets(res.data);
                setLayout(res.data.map(c => ({
                    i: String(c.id), x: c.x, y: c.y, w: c.width, h: c.height
                })));
            });
    }, [club_id]);

    const getCsrfToken = async () => {
        const response = await axios.get("http://127.0.0.1:8000/api/csrf/");
        return response.data.csrfToken;
    };

    const addWidget = async () => {
        const csrfToken = await getCsrfToken();
        const newY = widgets.length > 0 ? Math.max(...widgets.map(w => w.y)) + 1 : 0;

        axios.post(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, 
            { name: `组件 ${widgets.length + 1}`, x: 0, y: newY, width: 2, height: 2, club: club_id }, 
            { withCredentials: true, headers: { "X-CSRFToken": csrfToken } }
        ).then(res => {
            setWidgets([...widgets, res.data]);
            setLayout([...layout, { i: String(res.data.id), x: 0, y: newY, w: res.data.width, h: res.data.height }]);
        });
    };

    const removeWidget = async (id: number) => {
        const csrfToken = await getCsrfToken();
        await axios.delete(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/${id}/`, {
            headers: { "X-CSRFToken": csrfToken },
            withCredentials: true
        });

        setWidgets(widgets.filter(c => c.id !== id));
        setLayout(layout.filter(l => l.i !== String(id)));
    };

    const saveLayout = async () => {
        const csrfToken = await getCsrfToken();
        await axios.post(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/update_layout/`, 
            { layout }, { withCredentials: true, headers: { "X-CSRFToken": csrfToken } }
        );
    };

    return (
        <div style={{ padding: "0px", maxWidth: "1200px", margin: "auto" }}>
            <h2 style={{ textAlign: "center" }}>组件管理面板</h2>

            <div style={{ display: "flex", justifyContent: "center", marginBottom: "10px" }}>
                <button onClick={addWidget} style={{ marginRight: "10px", padding: "8px 16px", fontSize: "14px" }}>➕ 添加组件</button>
                <button onClick={saveLayout} style={{ marginRight: "10px", padding: "8px 16px", fontSize: "14px" }}>💾 保存布局</button>
                <Link to={`/club-view/${club_id}`}>
                    <button style={{ padding: "8px 16px", fontSize: "14px", background: "#4CAF50", color: "white", border: "none", borderRadius: "5px" }}>
                        👁️ 预览页面
                    </button>
                </Link>
            </div>

            <GridLayout
                className="layout"
                layout={layout}
                cols={8}
                rowHeight={100}
                width={1200}
                onLayoutChange={(newLayout) => setLayout(newLayout)}
                isDraggable={true}
                isResizable={true}
            >
                {widgets.map((widget) => (
                    <div key={widget.id} data-grid={layout.find(l => l.i === String(widget.id))}
                         style={{ 
                             padding: "0px", 
                             background: "#ffffff", 
                             borderRadius: "12px", 
                             border: "1px solid #ddd",
                             boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
                             position: "relative"
                         }}>
                        <div style={{ 
                            fontWeight: "bold", 
                            fontSize: "14px", 
                            padding: "5px", 
                            background: "#f5f5f5", 
                            borderTopLeftRadius: "12px", 
                            borderTopRightRadius: "12px",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center"
                        }}>
                            📌 {widget.name}
                            <button 
                                onClick={() => removeWidget(widget.id)}
                                style={{
                                    background: "red",
                                    color: "#fff",
                                    border: "none",
                                    borderRadius: "50%",
                                    width: "24px",
                                    height: "24px",
                                    fontSize: "14px",
                                    fontWeight: "bold",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    cursor: "pointer",
                                    position: "absolute",
                                    top: "5px",
                                    right: "5px"
                                }}
                            >
                                ×
                            </button>
                        </div>
                        
                        <div style={{ padding: "10px" }}>
                            <p>组件内容...</p>
                        </div>
                    </div>
                ))}
            </GridLayout>
        </div>
    );
};

export default Dashboard;
