import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";
import { WidgetType } from "../types"; // 假设已有类型定义

const PublicView = () => {
    const { club_id } = useParams();
    const [widgets, setWidgets] = useState<{ id: number; name: string; x: number; y: number; width: number; height: number }[]>([]);
    const [layout, setLayout] = useState<{ i: string; x: number; y: number; w: number; h: number }[]>([]);

    // 修改数据获取逻辑
    useEffect(() => {
        if (!club_id || isNaN(Number(club_id))) return;

        axios.get(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, { 
            withCredentials: true 
        }).then((res) => {
            const validData = res.data.filter((w: any) => 
                w?.id && 
                Number.isInteger(w.x) && 
                Number.isInteger(w.y)
            );
            
            setWidgets(validData);
            setLayout(validData.map(w => ({
                i: String(w.id),
                x: w.x,
                y: w.y,
                w: w.width || 2,
                h: w.height || 2
            })));
        });
    }, [club_id]);

    // 新增组件渲染逻辑
    const renderWidgetContent = (widget: WidgetType) => {
        switch(widget.widget_type) {
            case 'text':
                return <div style={{ padding: 10 }}>{widget.data?.content || '文本内容'}</div>;
                
            case 'image':
                return widget.data?.url ? (
                    <img 
                        src={widget.data.url} 
                        alt="社团图片" 
                        style={{ 
                            width: '100%', 
                            height: '100%',
                            objectFit: 'cover',
                            borderRadius: 8
                        }}
                    />
                ) : <div style={{ padding: 10 }}>暂无图片</div>;

            case 'notice':
                return <div style={{ padding: 10 }}>
                    <div style={{ color: '#666', fontSize: 12 }}>最新公告：</div>
                    <div>{widget.data?.content || '暂无公告'}</div>
                </div>;

            case 'countdown':
                const targetDate = widget.data?.date ? new Date(widget.data.date) : null;
                return <div style={{ 
                    textAlign: 'center', 
                    padding: 10,
                    fontSize: 18,
                    fontWeight: 'bold'
                }}>
                    {targetDate ? `${Math.ceil((targetDate.getTime() - Date.now()) / 86400000)} 天` : '未设置时间'}
                </div>;

            default:
                return <div>未知组件类型</div>;
        }
    };

    return (
        <div style={{ padding: "20px", maxWidth: "1200px", margin: "auto" }}>
            <h2 style={{ textAlign: "center", marginBottom: "20px" }}>📌 组件展示页面</h2>

            <GridLayout
                className="layout"
                layout={layout}
                cols={8}
                rowHeight={100}
                width={1200}
                isDraggable={false}  // 预览页面禁用拖拽
                isResizable={false}  // 预览页面禁用调整大小
            >
                {widgets.map((widget) => (
                    <div key={widget.id} 
                        data-grid={layout.find(l => l.i === String(widget.id))}
                        style={{ 
                            background: "#fff",
                            borderRadius: 12,
                            border: "1px solid #eee",
                            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                            overflow: 'hidden'
                        }}>
                        <div style={{ 
                            padding: 8,
                            background: "#f8f9fa",
                            borderBottom: "1px solid #eee",
                            fontSize: 14,
                            fontWeight: 500
                        }}>
                            {widget.name}
                        </div>
                        <div style={{ 
                            height: 'calc(100% - 40px)',
                            padding: 8
                        }}>
                            {renderWidgetContent(widget)}
                        </div>
                    </div>
                ))}
            </GridLayout>
        </div>
    );
};

export default PublicView;
