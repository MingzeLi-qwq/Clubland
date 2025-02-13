import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";  // 获取 club_id
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";

const Dashboard = () => {
    const { club_id } = useParams();  // 从 URL 获取社团 ID
    const [widgets, setWidgets] = useState([]);
    const [layout, setLayout] = useState([]);

    useEffect(() => {
        axios.get(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, { withCredentials: true })
            .then((res) => {
                setWidgets(res.data);
                setLayout(res.data.map(c => ({
                    i: String(c.id),
                    x: c.x,
                    y: c.y,
                    w: c.width,
                    h: c.height
                })));
            });
    }, [club_id]);

    // ✅ 添加组件
    const addWidget = () => {
        axios.post(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, 
            { name: `组件 ${widgets.length + 1}`, x: 0, y: 0, width: 1, height: 1 }, 
            { withCredentials: true }
        ).then(res => {
            setWidgets([...widgets, res.data]);
            setLayout([...layout, { 
                i: String(res.data.id), 
                x: res.data.x, 
                y: res.data.y, 
                w: res.data.width, 
                h: res.data.height 
            }]);
        });
    };

    // ✅ 删除组件
    const removeWidget = (id) => {
        axios.delete(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/${id}/`, { withCredentials: true })
            .then(() => {
                setWidgets(widgets.filter(c => c.id !== id));
                setLayout(layout.filter(l => l.i !== String(id)));
            });
    };

    return (
        <div className="container mx-auto p-4">
            <h2 className="text-2xl font-bold mb-4">📌 可编辑组件面板</h2>
            
            {/* ✅ 添加组件按钮 */}
            <button 
                onClick={addWidget} 
                className="p-2 bg-blue-500 text-white rounded mb-4"
            >
                ➕ 添加组件
            </button>

            <GridLayout
                className="layout"
                layout={layout}
                cols={4}
                rowHeight={100}
                width={1200}
                onLayoutChange={(newLayout) => setLayout(newLayout)}
            >
                {widgets.map((widget) => (
                    <div 
                        key={widget.id} 
                        data-grid={layout.find(l => l.i === String(widget.id))}
                        className="rounded-lg shadow-lg p-4 bg-white flex justify-between items-center"
                    >
                        {widget.name}
                        {/* ✅ 删除组件按钮 */}
                        <button 
                            onClick={() => removeWidget(widget.id)} 
                            className="text-red-500 p-1"
                        >
                            ❌
                        </button>
                    </div>
                ))}
            </GridLayout>
        </div>
    );
};

export default Dashboard;
