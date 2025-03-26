import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import axios from "axios";

interface WidgetType {
    id: number;
    name: string;
    widget_type: 'text' | 'image' | 'notice' | 'countdown' | 'clock' | 'calendar' | 'event_selector';
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
    const { event_id } = useParams();
    const [event, setEvent] = useState<any>(null);
    const [isManager, setIsManager] = useState<boolean | null>(null);
    const [widgets, setWidgets] = useState<WidgetType[]>([]);
    const [layout, setLayout] = useState<{ i: string; x: number; y: number; w: number; h: number }[]>([]);
    const [dashboardBg, setDashboardBg] = useState<string | null>(null);
    const [clubName, setClubName] = useState<string | null>(null);
    const [time, setTime] = useState({
        hours: 0,
        minutes: 0,
        seconds: 0
    });
    const widgetConfig = {
        clock: { w: 2, h: 3, resizable: false },
        calendar: { w: 3, h: 3, resizable: false },
        default: { w: 2, h: 2, resizable: true }
    };
    
    useEffect(() => {
        const checkIfManager = async () => {
            try {
                console.log("Checking admin status...");
                const response = await axios.get(`http://51.21.191.188:8000/api/clubs/api/clubs/${club_id}/is_manager/`);
                setIsManager(response.data.is_manager);  // Set the manager status based on the response
            } catch (error) {
                console.error("Error checking admin status", error);
            }
        };

        checkIfManager();
    }, [club_id]);

    useEffect(() => {
        const timer = setInterval(() => {
            const now = new Date();
            setTime({
                hours: now.getHours() % 12,
                minutes: now.getMinutes(),
                seconds: now.getSeconds()
            });
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        if (!club_id || isNaN(Number(club_id))) return;

        const fetchClubData = async () => {
            try {
                const [widgetsRes, clubRes] = await Promise.all([
                    axios.get(`http://51.21.191.188:8000/api/clubs/${club_id}/widgets/`, {
                        withCredentials: true
                    }),
                    axios.get(`http://51.21.191.188:8000/api/clubs/${club_id}/info/`, {
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
                    w: widgetConfig[w.widget_type as keyof typeof widgetConfig]?.w || w.width,
                    h: widgetConfig[w.widget_type as keyof typeof widgetConfig]?.h || w.height,
                })));
                setClubName(clubRes.data.name);
                if (clubRes.data.background_image) {
                    const fullUrl = `http://51.21.191.188:8000${clubRes.data.background_image}`;
                    setDashboardBg(fullUrl);
                }
            } catch (error) {
                console.error("Loading Error", error);
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
                                src={`http://51.21.191.188:8000${widget.data.url}`}
                                alt="Photo"
                                style={{
                                    width: '100%',
                                    height: '100%',
                                    objectFit: 'cover',
                                    display: 'block',
                                    borderRadius: 12,
                                }}
                            />
                        </div>
                    ) : <div style={{ padding: 10 }}>No Photo</div>;

            case 'notice':
                return <div style={{ padding: 10 }}>
                    <div style={{ color: '#666', fontSize: 18 }}>Lastest Notice</div>
                    <div>{widget.data?.content || 'No Notice'}</div>
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

            case 'clock':
                return <div style={{
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative'
                }}>
                    <div style={{
                        width: '100%',
                        height: '100%',
                        background: '#1a1a1a',
                        borderRadius: '50%',
                        margin: '0 auto',
                        position: 'relative'
                    }}>
                        <div style={{
                            width: '80%',
                            height: '80%',
                            position: 'absolute',
                            left: '10%',
                            top: '10%',
                            borderRadius: '50%',
                            border: '2px solid #444'
                        }}>
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
                        </div>
                        
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
                            top: '50%',
                            width: '8px',
                            height: '8px',
                            background: '#fff',
                            borderRadius: '50%',
                            transform: 'translate(-50%, -50%)'
                        }} />
                    </div>
                </div>;
            case 'event_selector':
                if (!widget.data?.event_id) {
                    return <div>No Event Info</div>;
                }
                
                return (
                    <div style={{ padding: 10 }}>
                        <h3>Event Detail</h3>
                        {widget.data ? (
                            <>
                                <p><strong>Event Name:</strong> {widget.data.name}</p>
                                <p><strong>TIme:</strong> {new Date(widget.data.start_time).toLocaleString()} - {new Date(widget.data.end_time).toLocaleString()}</p>
                                <p><strong>Location:</strong> {widget.data.location}</p>
                                <p><strong>Descriptioon:</strong> {widget.data.description}</p>
                            </>
                        ) : (
                            <div>Loading...</div>
                        )}
                    </div>
                );
          
                
            default:
                return <div>Undefined Widget</div>;
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
            {isManager && (
            <button 
                onClick={() => window.location.href = `/club-dashboard/${club_id}`}
                style={{
                    background: '#1890ff',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    height: '40px',
                    transition: 'background 0.3s',
                    ':hover': {
                        background: '#40a9ff'
                    }
                }}
            >
                Edit
            </button>
            )}
        </div>
        
    );
};

export default PublicView;