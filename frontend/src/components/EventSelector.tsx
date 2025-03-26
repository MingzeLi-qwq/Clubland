// 在 EventSelector.tsx 中，确保通过 onEventSelect 回调将选中的事件传递到父组件
const EventSelector = ({ clubId, onEventSelect }: EventSelectorProps) => {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);

  useEffect(() => {
    if (clubId) {
      axios
        .get(`http://51.21.191.188:8000/api/clubs/${clubId}/events/`)
        .then((response) => {
          setEvents(response.data);
        })
        .catch((error) => {
          console.error("There was an error fetching the events!", error);
        });
    }
  }, [clubId]);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const eventId = event.target.value;
    setSelectedEventId(eventId);

    const selectedEvent = events.find((e: any) => e.id === eventId);
    if (selectedEvent) {
      onEventSelect(selectedEvent); // 将选中的活动数据传递给父组件
    }
  };

  return (
    <div>
      <label>Select an Event:</label>
      <select value={selectedEventId || ""} onChange={handleChange}>
        <option value="">Select an event</option>
        {events.map((event: any) => (
          <option key={event.id} value={event.id}>
            {event.name} - {new Date(event.start_time).toLocaleString()}
          </option>
        ))}
      </select>
    </div>
  );
};
