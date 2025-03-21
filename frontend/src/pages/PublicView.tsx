import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";
// 定义组件类型接口
interface WidgetType {
    id: number;
    name: string;
    widget_type: 'text' | 'image' | 'notice' | 'countdown';
    x: number;
    y: number;
    width?: number;
    height?: number;
    data?: {
        content?: string;
        url?: string;
        date?: string;
    };
}

const PublicView = () => {
    const { club_id } = useParams();
    const [widgets, setWidgets] = useState<WidgetType[]>([]);
    const [layout, setLayout] = useState<{ i: string; x: number; y: number; w: number; h: number }[]>([]);
    const [dashboardBg, setDashboardBg] = useState<string | null>(null);
    const [clubName, setClubName] = useState<string | null>(null);

    useEffect(() => {
        if (!club_id || isNaN(Number(club_id))) return;

        const fetchClubData = async () => {
            try {
                const [widgetsRes, clubRes] = await Promise.all([
                    axios.get(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, {
                        withCredentials: true
                    }),
                    axios.get(`http://127.0.0.1:8000/api/clubs/${club_id}/info/`, {
                        withCredentials: true
                    })
                ]);

                const validData = widgetsRes.data.filter((w: any) =>
                    w?.id && Number.isInteger(w.x) && Number.isInteger(w.y)
                );

                setWidgets(validData);
                setLayout(validData.map(w => ({
                    i: String(w.id),
                    x: w.x,
                    y: w.y,
                    w: w.width || 2,
                    h: w.height || 2
                })));
                setClubName(clubRes.data.name);
                setDashboardBg(clubRes.data.background_image);
            } catch (error) {
                console.error("加载组件或背景失败：", error);
            }
        };

        fetchClubData();
    }, [club_id]);

    const renderWidgetContent = (widget: WidgetType) => {
        switch (widget.widget_type) {
            case 'text':
                return <div style={{ padding: 10 }}>{widget.data?.content || '文本内容'}</div>;

                case 'image':
                    return widget.data?.url ? (
                        <div
                            style={{
                                width: '100%',
                                height: '100%',
                                overflow: 'hidden',
                            }}
                        >
                            <img
                                src={widget.data.url}
                                alt="社团图片"
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    display: 'block',
                                    borderRadius: 12,
                                }}
                            />
                        </div>
                    ) : <div style={{ padding: 10 }}>暂无图片</div>;

            case 'notice':
                return <div style={{ padding: 10 }}>
                    <div style={{ color: '#666', fontSize: 18 }}>最新公告：</div>
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
        <div
            style={{
                padding: "20px",
                margin: "auto",
                backgroundImage: dashboardBg ? `url(${dashboardBg})` : 'none',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                minHeight: '100vh'
            }}
        >
            <h2 
                style={{
                    textAlign: "center",
                    fontSize: "32px",
                    fontWeight: "bold",
                    color: "#FFFFFF",
                    textShadow: "2px 2px 8px rgba(0, 0, 0, 0.6)",
                    backgroundColor: "rgba(0, 0, 0, 0.4)",
                    padding: "10px",
                    borderRadius: "8px",
                    marginBottom: "20px"
                }}
            >
                {clubName ? `Welcome to ${clubName}` : "Loading..."}
            </h2>

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
                    <div key={widget.id}
                        data-grid={layout.find(l => l.i === String(widget.id))}
                        style={{
                            background: "#fff",
                            borderRadius: 12,
                            border: "1px solid #eee",
                            boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                            overflow: 'hidden'
                        }}
                    >
                        <div style={{
                            height: 'calc(100%)',
                            padding: 1
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