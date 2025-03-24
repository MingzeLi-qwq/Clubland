import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EventSelector = ({ clubId }) => {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState("");

  useEffect(() => {
    if (clubId) {
      axios.get(`/api/clubs/${clubId}/events/`)
        .then(response => {
          setEvents(response.data);
        })
        .catch(error => {
          console.error("There was an error fetching the events!", error);
        });
    }
  }, [clubId]);

  const handleChange = (event) => {
    setSelectedEvent(event.target.value);
  };

  return (
    <div>
      <label>Select an Event:</label>
      <select value={selectedEvent} onChange={handleChange}>
        <option value="">Select an event</option>
        {events.map((event) => (
          <option key={event.id} value={event.id}>
            {event.name} - {new Date(event.start_time).toLocaleString()}
          </option>
        ))}
      </select>
    </div>
  );
};

export default EventSelector;
