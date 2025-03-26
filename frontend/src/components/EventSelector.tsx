// EventSelector.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface EventSelectorProps {
  clubId: string;
  onEventSelect: (event: any) => void;
}

const EventSelector = ({ clubId, onEventSelect }: EventSelectorProps) => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  console.log(clubId);
  console.log(selectedEvent);
  useEffect(() => {
    if (clubId) {
      axios
        .get(`/api/clubs/${clubId}/events/`)
        .then((response) => {
          setEvents(response.data);
        })
        .catch((error) => {
          console.error('There was an error fetching the events!', error);
        });
    }
  }, [clubId]);

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const eventId = event.target.value;
    setSelectedEvent(eventId);
    const selected = events.find((e: any) => e.id === eventId);
    onEventSelect(selected); // 将选中的活动数据传递给父组件
  };

  return (
    <div>
      <label>Select an Event:</label>
      <select value={selectedEvent || ''} onChange={handleChange}>
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

export default EventSelector;
