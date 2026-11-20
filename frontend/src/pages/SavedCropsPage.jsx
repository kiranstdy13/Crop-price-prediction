import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import {
  BookmarkCheck,
  Plus,
  Trash2,
  Bell,
  CheckCircle2,
  AlertCircle,
  Wheat,
  MapPin
} from 'lucide-react';

const SavedCropsPage = () => {
  const { t, lang } = useLanguage();
  const [savedCrops, setSavedCrops] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  // Form states
  const [commodity, setCommodity] = useState('Tomato');
  const [market, setMarket] = useState('Bengaluru');
  const [targetPrice, setTargetPrice] = useState('2500');
  const [showAddModal, setShowAddModal] = useState(false);

  const fetchItems = async () => {
    try {
      const [cropsRes, notifsRes] = await Promise.all([
        api.get('/farmer/saved-crops'),
        api.get('/farmer/notifications')
      ]);
      if (cropsRes.data?.saved_crops) setSavedCrops(cropsRes.data.saved_crops);
      if (notifsRes.data?.notifications) setNotifications(notifsRes.data.notifications);
    } catch (err) {
      console.error("Fetch saved crops error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await api.post('/farmer/saved-crops', {
        commodity,
        market,
        target_price: parseFloat(targetPrice),
        alert_enabled: true
      });
      setShowAddModal(false);
      fetchItems();
    } catch (err) {
      console.error("Add crop error:", err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/farmer/saved-crops/${id}`);
      fetchItems();
    } catch (err) {
      console.error("Delete crop error:", err);
    }
  };

  const handleMarkRead = async (id) => {
    try {
      await api.put(`/farmer/notifications/${id}/read`);
      fetchItems();
    } catch (err) {
      console.error("Mark read error:", err);
    }
  };

  return (
    <div className="content-body">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BookmarkCheck color="#16a34a" size={26} />
            <span>{t('savedCrops')}</span>
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.92rem', marginTop: '4px' }}>
            Set target price benchmarks for your preferred Karnataka APMC mandis and receive verified alerts.
          </p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn btn-primary">
          <Plus size={18} />
          <span>Track New Crop</span>
        </button>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '20px'
        }}>
          <div className="card" style={{ width: '100%', maxWidth: '480px', padding: '28px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '18px' }}>
              Track Crop & Target Alert
            </h3>
            <form onSubmit={handleAdd}>
              <div className="form-group">
                <label className="form-label">Crop Name</label>
                <select className="form-select" value={commodity} onChange={(e) => setCommodity(e.target.value)}>
                  {['Tomato', 'Onion', 'Potato', 'Cabbage', 'Green Chilli', 'Rice', 'Maize', 'Groundnut'].map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Karnataka Mandi Market</label>
                <select className="form-select" value={market} onChange={(e) => setMarket(e.target.value)}>
                  {['Bengaluru', 'Mysuru', 'Hubballi', 'Mandya'].map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Target Alert Price (₹ / Quintal)</label>
                <input
                  type="number"
                  className="form-input"
                  required
                  value={targetPrice}
                  onChange={(e) => setTargetPrice(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowAddModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Alert
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Saved Crops Grid */}
      <div className="grid-3" style={{ marginBottom: '32px' }}>
        {savedCrops.map((item, idx) => (
          <div key={idx} className="card" style={{ position: 'relative' }}>
            <button
              onClick={() => handleDelete(item.id)}
              style={{
                position: 'absolute',
                top: '18px',
                right: '18px',
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer'
              }}
              title="Remove"
            >
              <Trash2 size={16} />
            </button>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="badge badge-green">
                <Wheat size={14} /> {item.commodity}
              </span>
              <span className="badge badge-blue">
                <MapPin size={14} /> {item.market}
              </span>
            </div>

            <div style={{ marginTop: '12px' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>CURRENT MANDI PRICE</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a' }}>
                ₹{item.current_price?.toLocaleString() || '1,833'} / Q
              </div>
            </div>

            <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Target Alert:</span>
                <strong style={{ fontSize: '0.9rem', color: '#16a34a', marginLeft: '6px' }}>₹{item.target_price?.toLocaleString()}</strong>
              </div>
              <span className={`badge ${item.target_met ? 'badge-green' : 'badge-amber'}`} style={{ fontSize: '0.72rem' }}>
                {item.target_met ? 'Target Met!' : 'Monitoring'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Notifications Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">
            <Bell size={20} color="#16a34a" />
            <span>Farmer Notifications & Mandi Alerts</span>
          </h3>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {notifications.map((notif, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                borderRadius: '8px',
                background: notif.read ? '#f8fafc' : '#f0fdf4',
                border: notif.read ? '1px solid #e2e8f0' : '1px solid #bbf7d0'
              }}
            >
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#0f172a' }}>
                  {lang === 'kn' && notif.title_kn ? notif.title_kn : notif.title}
                </div>
                <div style={{ fontSize: '0.84rem', color: '#475569', marginTop: '2px' }}>
                  {lang === 'kn' && notif.message_kn ? notif.message_kn : notif.message}
                </div>
              </div>
              {!notif.read && (
                <button
                  onClick={() => handleMarkRead(notif.id)}
                  className="btn btn-secondary"
                  style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                >
                  Mark Read
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SavedCropsPage;
