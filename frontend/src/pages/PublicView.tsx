import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";

const PublicView = () => {
    const { club_id } = useParams();
    const [widgets, setWidgets] = useState<{ id: number; name: string; x: number; y: number; width: number; height: number }[]>([]);
    const [layout, setLayout] = useState<{ i: string; x: number; y: number; w: number; h: number }[]>([]);

    useEffect(() => {
        axios.get(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, { withCredentials: true })
            .then((res) => {
                setWidgets(res.data);
                setLayout(res.data.map((widget) => ({
                    i: String(widget.id),
                    x: widget.x,
                    y: widget.y,
                    w: widget.width,
                    h: widget.height,
                })));
            });
    }, [club_id]);

    return (
        <div style={{ padding: "20px", maxWidth: "1200px", margin: "auto" }}>
            <h2 style={{ textAlign: "center", marginBottom: "20px" }}>📌 组件展示页面</h2>

            <GridLayout
                className="layout"
                layout={layout}
                cols={8}
                rowHeight={100}
                width={1200}
                isDraggable={false}
                isResizable={false}
            >
                {widgets.map((widget) => (
                    <div key={widget.id} data-grid={layout.find(l => l.i === String(widget.id))}
                        style={{
                            background: "#ffffff",
                            borderRadius: "12px",
                            border: "1px solid #ddd",
                            boxShadow: "0 2px 5px rgba(0, 0, 0, 0.1)",
                            textAlign: "left",
                        }}>
                        <h3 style={{ fontSize: "16px", fontWeight: "bold", margin: "0 0 10px" }}>
                            📌 {widget.name}
                        </h3>
                        <p>组件内容展示...</p>
                    </div>
                ))}
            </GridLayout>
        </div>
    );
};

export default PublicView;
