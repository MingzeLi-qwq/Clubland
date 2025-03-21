import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";
import { Link } from "react-router-dom";


const Dashboard = () => {
    const { club_id } = useParams();
    const [dashboardBg, setDashboardBg] = useState<string | null>(null);
    const [clubName, setClubName] = useState<string | null>(null);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [time, setTime] = useState({
        hours: 0,
        minutes: 0,
        seconds: 0
    });
    useEffect(() => {
        const updateClock = () => {
            const now = new Date();
            setTime({
                hours: now.getHours() % 12,
                minutes: now.getMinutes(),
                seconds: now.getSeconds()
            });
        };
        const timer = setInterval(updateClock, 1000);
        return () => clearInterval(timer);
    }, []);
    
    useEffect(() => {
        if (!club_id || isNaN(Number(club_id))) return;
        const timer = setInterval(() => {
            setCurrentTime(new Date());
        }, 1000);
        
        const loadData = async () => {
            try {
                const response = await axios.get(
                    `http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`,
                    { 
                        withCredentials: true,
                        headers: { "Content-Type": "application/json" }
                    }
                );

                // 添加数据格式验证
                const validData = response.data.filter((w: any) => 
                    w?.id && 
                    Number.isInteger(w.x) && 
                    Number.isInteger(w.y)
                );

                setWidgets(validData);
                // 在布局数据设置处保持尺寸固定
                setLayout(validData.map((w: any) => ({
                    i: String(w.id),
                    x: w.x,
                    y: w.y,
                    w: w.width,
                    h: w.height
                })));

                const clubRes = await axios.get(
                    `http://127.0.0.1:8000/api/clubs/${club_id}/info/`,
                    { withCredentials: true }
                );
        
                if (clubRes.data.background_image) {
                    setDashboardBg(clubRes.data.background_image);
                }
                if (clubRes.data.name) {
                    setClubName(clubRes.data.name); // 设置club名称
                }

            } catch (error) {
                console.error("加载失败:", error);
            }
        };

        loadData();
    }, [club_id]); // 确保依赖项正确

    // State declarations should be at the top
    const [widgets, setWidgets] = useState<{ 
        id: number, 
        name: string, 
        widget_type: string,
        x: number, 
        y: number, 
        width: number, 
        height: number,
        data: any
    }[]>([]);

    const [layout, setLayout] = useState<{ 
        i: string, 
        x: number, 
        y: number, 
        w: number, 
        h: number 
    }[]>([]);

    const getCsrfToken = async () => {
        const cookieToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieToken) return cookieToken;
        
        const response = await axios.get("http://127.0.0.1:8000/api/csrf/");
        return response.data.csrfToken;
    };
    
    const addWidget = async () => {
        const widgetType = prompt('Choose your widget type:\n1. text\n2. chart\n3. notice\n4. image\n5. countdown\n6. clock');
        if (!widgetType) return;
        
        const typeMap: {[key: string]: string} = {
        '1': 'text',
        '2': 'chart',
        '3': 'notice',
        '4': 'image',
        '5': 'countdown',
        '6': 'clock'
        };
        
        const csrfToken = await getCsrfToken();
        const newY = widgets.length > 0 ? Math.max(...widgets.map(w => w.y)) + 1 : 0;
        
        axios.post(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, {
        name: `${widgets.length + 1}`,
        widget_type: typeMap[widgetType],
        x: 0, 
        y: newY, 
        width: 2, 
        height: 2, 
        club: club_id,
        data: {}
        }, 
        { withCredentials: true, headers: { "X-CSRFToken": csrfToken } }
        ).then(res => {
            setWidgets([...widgets, res.data]);
            setLayout([...layout, { 
                i: String(res.data.id), 
                x: 0, 
                y: newY, 
                w: res.data.width, 
                h: res.data.height 
            }]);
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
        
        const payload = {
            layout: layout.map(item => ({
                i: parseInt(item.i),
                x: item.x,
                y: item.y,
                w: item.w,
                h: item.h
            }))
        };
    
        try {
            await axios.post(
                `http://127.0.0.1:8000/api/clubs/${club_id}/widgets/update_layout/`,
                payload, 
                { 
                    withCredentials: true, 
                    headers: { 
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/json"
                    } 
                }
            );
            alert('Saved Layout');
        } catch (error) {
            console.error('Save failed:', error.response?.data || error.message);
            alert(`Save failed: ${error.response?.data?.error || error.message}`);
        }
    };

    const uploadBackground = async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
    
        try {
            const csrfToken = await getCsrfToken();
            const response = await axios.post(
                'http://127.0.0.1:8000/api/upload-image/',
                formData,
                {
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'multipart/form-data'
                    },
                    withCredentials: true
                }
            );
    
            const imageUrl = response.data.file_url;
            const fullUrl = `/media/${imageUrl}`;
    
            const img = new Image();
            img.src = fullUrl;
            img.onload = async () => {
                setDashboardBg(fullUrl);
    
                await axios.patch(
                    `http://127.0.0.1:8000/api/clubs/${club_id}/background/`,
                    { background_image: imageUrl },
                    {
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken
                        },
                        withCredentials: true
                    }
                );
                alert("背景上传并保存成功！");
            };
    
            img.onerror = () => {
                console.error("图片加载失败");
                alert("上传成功但图片加载失败");
            };
    
        } catch (error) {
            console.error('背景上传失败:', error);
            alert('背景图片上传失败');
        }
    };
    

    const updateWidgetData = async (id: number, key: string, value: any) => {
    const csrfToken = await getCsrfToken();
    const updatedWidgets = widgets.map(w => {
    if (w.id === id) {
    return { ...w, data: { ...w.data, [key]: value } };
    }
    return w;
    });
    setWidgets(updatedWidgets);
    
    await axios.patch(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/${id}/`, {
    data: updatedWidgets.find(w => w.id === id)?.data
    }, {
    headers: { "X-CSRFToken": csrfToken },
    withCredentials: true
    });
    };

    return (
        <div 
            style={{
                padding: "40px",
                minHeight: "100vh",
                backgroundImage: dashboardBg ? `url(${dashboardBg})` : "none",
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat"
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

            <div style={{ display: "flex", justifyContent: "center", marginBottom: "10px" }}>
                <button className="button" onClick={addWidget}>
                    ➕ Add Widget
                </button>
                <button className="button" onClick={saveLayout}>
                    💾 Save Layout
                </button>
                <Link to={`/club-view/${club_id}`}>
                    <button className="button">
                        👁️ Preview Page
                    </button>
                </Link>
                <label className="label-upload">
                    🖼️ Background
                    <input
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={(e) => e.target.files?.[0] && uploadBackground(e.target.files[0])}
                    />
                </label>
            </div>

            <GridLayout
                className="layout"
                layout={layout}
                cols={8}
                rowHeight={100}
                width={1200}
                onLayoutChange={(newLayout) => setLayout(newLayout)}
                isDraggable={true}
                isResizable={widgets.widget_type !== 'clock'}
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
                            {widget.name}
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
                        
                        <div style={{ padding: "10px", height: 'calc(100% - 40px)' }}>
                          {widget.widget_type === 'notice' && (
                            <textarea 
                              style={{ 
                                width: '100%', 
                                height: '90%',
                                border: '0px solid #ddd',
                              }}
                              placeholder="输入公告内容..."
                              value={widget.data.content || ''}
                              onChange={(e) => updateWidgetData(widget.id, 'content', e.target.value)}
                            />
                          )}
                          
                        {widget.widget_type === 'image' && (
                            <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                                {!widget.data?.url ? (
                                <>
                                    <input
                                    type="file"
                                    accept="image/*"
                                    onChange={async (e) => {
                                        const file = e.target.files?.[0];
                                        if (!file) return;

                                        const csrfToken = await getCsrfToken();
                                        const formData = new FormData();
                                        formData.append("file", file);

                                        try {
                                        const res = await axios.post("http://127.0.0.1:8000/api/upload-image/", formData, {
                                            headers: {
                                            "X-CSRFToken": csrfToken,
                                            "Content-Type": "multipart/form-data"
                                            },
                                            withCredentials: true
                                        });

                                        const uploadedUrl = `/media/${res.data.file_url}`;
                                        await updateWidgetData(widget.id, 'url', uploadedUrl);
                                        } catch (err) {
                                        alert("上传失败");
                                        console.error(err);
                                        }
                                    }}
                                    />
                                </>
                                ) : (
                                <img
                                    src={widget.data.url}
                                    alt="上传图片"
                                    style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    borderRadius: '8px'
                                    }}
                                />
                                )}
                            </div>
                            )}


                        {widget.widget_type === 'countdown' && (
                                <div style={{ 
                                    height: '100%',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    padding: '8px'
                                }}>
                                    <input
                                        type="date"
                                        value={widget.data.date?.split('T')[0] || ''}
                                        onChange={(e) => updateWidgetData(widget.id, 'date', e.target.value + 'T00:00:00')}
                                        style={{
                                            marginBottom: '8px',
                                            padding: '4px',
                                            border: '1px solid #ddd',
                                            borderRadius: '4px'
                                        }}
                                    />
                                    <div style={{ 
                                        flex: 1,
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '1.2em',
                                        color: '#666'
                                    }}>
                                        {widget.data.date ? (
                                            `剩余天数: ${Math.ceil(
                                                (new Date(widget.data.date).getTime() - Date.now()) / 
                                                (1000 * 60 * 60 * 24)
                                            )}`
                                        ) : '请设置目标日期'}
                                    </div>
                                </div>
                            )}
                            {widget.widget_type === 'clock' && (
                                <div style={{
                                    height: '100%',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    background: '#1a1a1a',
                                    borderRadius: '50%',
                                    position: 'relative',
                                }}>
                                    {/* 表盘内部代码保持不变 */}
                                    <div style={{
                                        width: '80%',
                                        height: '80%',
                                        position: 'relative',
                                        borderRadius: '50%', 
                                        border: '2px solid #444'
                                    }}>
                                        {/* 时钟刻度 */}
                                        {[...Array(12)].map((_, i) => (
                                            <div key={i} style={{
                                                position: 'absolute',
                                                width: '2px',
                                                height: '10px',
                                                background: '#666',
                                                left: '50%',
                                                top: '5%',
                                                transform: `rotate(${i * 30}deg)`,
                                                transformOrigin: 'bottom'
                                            }} />
                                        ))}
                                        
                                        {/* 时钟指针 */}
                                        <div style={{
                                            position: 'absolute',
                                            left: '50%',
                                            bottom: '50%',
                                            width: '2px',
                                            height: '40%',
                                            background: '#ff5555',
                                            transform: `rotate(${time.seconds * 6}deg)`,
                                            transformOrigin: 'bottom',
                                            transition: 'transform 0.3s cubic-bezier(0.4, 2.3, 0.6, 1)'
                                        }} />
                                        <div style={{
                                            position: 'absolute',
                                            left: '50%',
                                            bottom: '50%',
                                            width: '3px',
                                            height: '35%',
                                            background: '#fff',
                                            transform: `rotate(${time.minutes * 6}deg)`,
                                            transformOrigin: 'bottom',
                                            transition: 'transform 0.3s cubic-bezier(0.4, 2.3, 0.6, 1)'
                                        }} />
                                        <div style={{
                                            position: 'absolute',
                                            left: '50%',
                                            bottom: '50%',
                                            width: '4px',
                                            height: '25%',
                                            background: '#fff',
                                            transform: `rotate(${time.hours * 30 + time.minutes * 0.5}deg)`,
                                            transformOrigin: 'bottom',
                                            transition: 'transform 0.3s cubic-bezier(0.4, 2.3, 0.6, 1)'
                                        }} />
                                        
                                        {/* 中心点 */}
                                        <div style={{
                                            position: 'absolute',
                                            left: '50%',
                                            top: '50%',
                                            width: '8px',
                                            height: '8px',
                                            background: '#ff5555',
                                            borderRadius: '50%',
                                            transform: 'translate(-50%, -50%)'
                                        }} />
                                    </div>
                                </div>
                            )}
                          {/* 其他类型渲染逻辑可继续扩展 */}
                        </div>
                    </div>
                ))}
            </GridLayout>
        </div>
    );
};

export default Dashboard;
