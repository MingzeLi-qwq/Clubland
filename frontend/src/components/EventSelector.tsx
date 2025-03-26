import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface EventSelectorProps {
  clubId: string;
  onEventSelect: (event: any) => void;
}

const EventSelector = ({ clubId, onEventSelect }: EventSelectorProps) => {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);

  useEffect(() => {
    if (clubId) {
      axios
        .get(`http://51.21.191.188:8000/api/clubs/${clubId}/events/`)
        .then((response) => {
          if (Array.isArray(response.data)) {
            setEvents(response.data);  // Only set if it's an array
          } else {
            console.error('Expected an array of events but got:', response.data);
          }
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
    onEventSelect(selected); // Pass the selected event to parent component
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
