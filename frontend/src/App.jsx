import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Send, Inbox, AlertCircle, Sparkles, Tag, Clock, RefreshCw } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://127.0.0.1:8000';

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  // Retrieve the tickets from the backend.
  const fetchTickets = async () => {
    setFetching(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/tickets/`);
      setTickets(response.data);
    } catch (error) {
      console.error('Error retrieving tickets:', error);
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  // Submitting a new ticket
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!subject.trim() || !body.trim()) return;

    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/tickets/`, { subject, body });
      setSubject('');
      setBody('');
      await fetchTickets(); // Reload the ticket list
    } catch (error) {
      console.error('Error sending the ticket:', error);
      alert("Si è verificato un errore durante l'invio del ticket.");
    } finally {
      setLoading(false);
    }
  };

  // Helper function for the urgency badge color
  const getUrgencyBadge = (urgency) => {
    const level = urgency ? urgency.toUpperCase() : 'BASSA';
    switch (level) {
      case 'ALTA':
        return <span className="badge badge-high"><AlertCircle size={14} /> ALTA</span>;
      case 'MEDIA':
        return <span className="badge badge-medium">MEDIA</span>;
      default:
        return <span className="badge badge-low">BASSA</span>;
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="logo-section">
          <Inbox size={28} className="icon-main" />
          <h1>Smart Support Inbox</h1>
        </div>
        <span className="ai-status">
          <Sparkles size={16} /> AI Engine (Gemini)
        </span>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Left Column: Input Form */}
        <section className="card form-section">
          <h2>Nuovo Ticket di Assistenza</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="subject">Oggetto</label>
              <input
                id="subject"
                type="text"
                placeholder="Es. Impossibile accedere all'account"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="body">Messaggio del cliente</label>
              <textarea
                id="body"
                rows="6"
                placeholder="Descrivi il problema riscontrato..."
                value={body}
                onChange={(e) => setBody(e.target.value)}
                required
              ></textarea>
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? (
                <>
                  <Sparkles size={18} className="spin" /> Analisi IA in corso...
                </>
              ) : (
                <>
                  <Send size={18} /> Invia & Analizza con IA
                </>
              )}
            </button>
          </form>
        </section>

        {/* Right Column: Ticket List */}
        <section className="card inbox-section">
          <div className="inbox-header">
            <h2>Inbox Ticket ({tickets.length})</h2>
            <button onClick={fetchTickets} className="btn-refresh" title="Aggiorna lista">
              <RefreshCw size={16} className={fetching ? 'spin' : ''} />
            </button>
          </div>

          {fetching && tickets.length === 0 ? (
            <p className="empty-message">Caricamento ticket in corso...</p>
          ) : tickets.length === 0 ? (
            <p className="empty-message">Nessun ticket presente. Inviane uno dal modulo a sinistra!</p>
          ) : (
            <div className="ticket-list">
              {tickets.map((ticket) => (
                <div key={ticket.id} className="ticket-card">
                  <div className="ticket-header">
                    <h3 className="ticket-title">{ticket.subject}</h3>
                    {getUrgencyBadge(ticket.urgency)}
                  </div>

                  <p className="ticket-body">{ticket.body}</p>

                  <div className="ticket-meta">
                    <span className="meta-tag">
                      <Tag size={14} /> {ticket.category}
                    </span>
                    <span className="meta-date">
                      <Clock size={14} /> {new Date(ticket.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  {ticket.suggested_reply && (
                    <div className="ai-suggestion-box">
                      <div className="ai-suggestion-header">
                        <Sparkles size={14} /> Risposta suggerita dall'IA
                      </div>
                      <p className="ai-suggestion-text">{ticket.suggested_reply}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}