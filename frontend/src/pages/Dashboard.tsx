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
    // 在现有状态声明下方添加useEffect
    useEffect(() => {
        if (!club_id || isNaN(Number(club_id))) return;
        const savedBg = localStorage.getItem(`dashboardBg-${club_id}`);
        if (savedBg) setDashboardBg(savedBg);

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
                setLayout(validData.map((w: any) => ({
                    i: String(w.id),
                    x: w.x,
                    y: w.y,
                    w: w.width || 2,
                    h: w.height || 2
                })));
            } catch (error) {
                console.error("加载失败:", error);
                alert("组件加载失败，请检查控制台");
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

    // 添加统一的 CSRF Token 获取方法
    const getCsrfToken = async () => {
        // 同时支持两种获取方式确保可靠性
        const cookieToken = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        
        if (cookieToken) return cookieToken;
        
        // 如果 cookie 不存在则从 API 获取
        const response = await axios.get("http://127.0.0.1:8000/api/csrf/");
        return response.data.csrfToken;
    };
    
    // 修改所有使用 CSRF Token 的方法（示例修改 addWidget）
    const addWidget = async () => {
        const widgetType = prompt('选择组件类型：\n1. 文本\n2. 图表\n3. 公告\n4. 图片\n5. 倒计时');
        if (!widgetType) return;
        
        const typeMap: {[key: string]: string} = {
        '1': 'text',
        '2': 'chart',
        '3': 'notice',
        '4': 'image',
        '5': 'countdown'
        };
        
        // 删除重复的 csrfToken 声明（第63行）
        const csrfToken = await getCsrfToken(); // 统一使用封装方法
        const newY = widgets.length > 0 ? Math.max(...widgets.map(w => w.y)) + 1 : 0;
        
        axios.post(`http://127.0.0.1:8000/api/clubs/${club_id}/widgets/`, {
        name: `组件 ${widgets.length + 1}`,
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
    
    // 同样修改其他方法中的 CSRF Token 获取方式（saveLayout, removeWidget, updateWidgetData）
    const saveLayout = async () => {
        const csrfToken = await getCsrfToken();
        
        // 修改字段名从 widget_id 改为 i 以匹配后端要求
        const payload = {
            layout: layout.map(item => ({
                i: parseInt(item.i),  // 字段名改为后端需要的i
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
            alert('布局保存成功!');
        } catch (error) {
            console.error('保存失败:', error.response?.data || error.message);
            alert(`保存失败: ${error.response?.data?.error || error.message}`);
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
            setDashboardBg(response.data.url);
        } catch (error) {
            console.error('背景上传失败:', error);
            alert('背景图片上传失败');
        }
    };

    // 新增数据更新方法
    const updateWidgetData = async (id: number, key: string, value: any) => {
    const csrfToken = await getCsrfToken();
    const updatedWidgets = widgets.map(w => {
    if (w.id === id) {
    return { ...w, data: { ...w.data, [key]: value } };
    }
    return w;
    });
    setWidgets(updatedWidgets);
    
    // 保存到后端
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
            <h2 style={{ textAlign: "center" }}>组件管理面板</h2>
            
            <div style={{ display: "flex", justifyContent: "center", marginBottom: "10px" }}>
                <button onClick={addWidget} style={{ marginRight: "10px", padding: "8px 16px", fontSize: "14px" }}>➕ 添加组件</button>
                <button onClick={saveLayout} style={{ marginRight: "10px", padding: "8px 16px", fontSize: "14px" }}>💾 保存布局</button>
                <Link to={`/club-view/${club_id}`}>
                    <button style={{ padding: "8px 16px", fontSize: "14px", background: "#4CAF50", color: "white", border: "none", borderRadius: "5px" }}>
                        👁️ 预览页面
                    </button>
                </Link>
                <label style={{
                    marginLeft: '10px',
                    padding: '8px 16px',
                    background: '#2196F3',
                    color: 'white',
                    borderRadius: '5px',
                    cursor: 'pointer'
                }}>
                    🖼️ 上传背景
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
                              <input
                                type="text"
                                placeholder="图片URL"
                                value={widget.data.url || ''}
                                onChange={(e) => updateWidgetData(widget.id, 'url', e.target.value)}
                                style={{ marginBottom: '8px' }}
                              />
                              {widget.data.url && (
                                <img 
                                  src={widget.data.url} 
                                  alt="自定义图片" 
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
                          {/* 其他类型渲染逻辑可继续扩展 */}
                        </div>
                    </div>
                ))}
            </GridLayout>
        </div>
    );
};

export default Dashboard;
