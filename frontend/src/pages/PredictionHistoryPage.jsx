import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import { History, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

const PredictionHistoryPage = () => {
  const { t } = useLanguage();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/predictions/history');
        if (res.data?.predictions) setPredictions(res.data.predictions);
      } catch (err) {
        console.error("Fetch history error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  return (
    <div className="content-body">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <History color="#16a34a" size={26} />
          <span>{t('history')}</span>
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.92rem', marginTop: '4px' }}>
          Historical record of all machine learning forecasts and SHAP feature contributions generated for your account.
        </p>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#16a34a' }}>Loading prediction history...</div>
        ) : predictions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            <p style={{ marginBottom: '16px' }}>No predictions generated yet.</p>
            <Link to="/predict" className="btn btn-primary">Make First Prediction</Link>
          </div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Date Generated</th>
                  <th>Crop</th>
                  <th>Market</th>
                  <th>Horizon</th>
                  <th>Current Price</th>
                  <th>Forecast Price</th>
                  <th>Expected Change</th>
                  <th>Recommendation</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {predictions.map((p, idx) => (
                  <tr key={idx}>
                    <td style={{ fontSize: '0.82rem', color: '#64748b' }}>
                      {new Date(p.created_at).toLocaleDateString()}
                    </td>
                    <td><strong>{p.commodity}</strong></td>
                    <td>{p.market}</td>
                    <td>{p.horizon_days} Days</td>
                    <td>₹{p.current_modal_price?.toLocaleString()}</td>
                    <td><strong style={{ color: '#15803d' }}>₹{p.predicted_price?.toLocaleString()}</strong></td>
                    <td>
                      <span className={`badge ${p.pct_change >= 0 ? 'badge-green' : 'badge-red'}`}>
                        {p.pct_change >= 0 ? `+${p.pct_change}%` : `${p.pct_change}%`}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-amber">{p.recommendation?.action || 'Monitor'}</span>
                    </td>
                    <td>
                      <Link to={`/result/${p.id}`} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.78rem' }}>
                        View SHAP
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default PredictionHistoryPage;
