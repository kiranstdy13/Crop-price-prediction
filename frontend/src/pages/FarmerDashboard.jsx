import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import {
  TrendingUp,
  TrendingDown,
  Building2,
  Wheat,
  BookmarkCheck,
  BellRing,
  ArrowRight,
  ShieldAlert,
  Sprout
} from 'lucide-react';

const FarmerDashboard = () => {
  const { user } = useAuth();
  const { t, lang } = useLanguage();

  const [metrics, setMetrics] = useState(null);
  const [marketTickers, setMarketTickers] = useState([]);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [allPrices, setAllPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dashRes, pricesRes] = await Promise.all([
          api.get('/farmer/dashboard').catch(() => null),
          api.get('/markets/latest-prices').catch(() => null),
        ]);

        if (dashRes && dashRes.data) {
          setMetrics(dashRes.data.metrics);
          setMarketTickers(dashRes.data.market_tickers || []);
          setRecentPredictions(dashRes.data.recent_predictions || []);
        }

        if (pricesRes && pricesRes.data) {
          setAllPrices(pricesRes.data.prices || []);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="content-body">
      {/* Welcome & Status Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #166534 0%, #15803d 100%)',
        color: 'white',
        borderRadius: '16px',
        padding: '30px',
        marginBottom: '28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.18)', padding: '4px 12px', borderRadius: '9999px', fontSize: '0.78rem', marginBottom: '12px' }}>
            <span style={{ width: '8px', height: '8px', background: '#4ade80', borderRadius: '50%' }}></span>
            {t('mandiStatus')}
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '8px' }}>
            {t('welcomeFarmer')}, {user?.name || 'Ramesh Gowda'}!
          </h2>
          <p style={{ opacity: 0.9, fontSize: '0.92rem', maxWidth: '600px' }}>
            Real-time Karnataka APMC mandi trends powered by verified AGMARKNET records, XGBoost regression, and SHAP explainability.
          </p>
        </div>
        <Link to="/predict" className="btn btn-outline" style={{ background: 'white', color: '#166534', border: 'none', padding: '12px 24px', fontWeight: 700 }}>
          <TrendingUp size={18} />
          <span>{t('predictPrices')}</span>
        </Link>
      </div>

      {/* KPI Stat Cards */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>Supported Crops</span>
            <div style={{ background: '#dcfce7', color: '#15803d', padding: '8px', borderRadius: '8px' }}>
              <Wheat size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>8</div>
          <span style={{ fontSize: '0.78rem', color: '#15803d', fontWeight: 600 }}>Tomato, Onion, Potato, Rice...</span>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>Karnataka Mandis</span>
            <div style={{ background: '#e0f2fe', color: '#0369a1', padding: '8px', borderRadius: '8px' }}>
              <Building2 size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>4 APMCs</div>
          <span style={{ fontSize: '0.78rem', color: '#0369a1', fontWeight: 600 }}>Bengaluru, Mysuru, Hubballi, Mandya</span>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>Saved Crops</span>
            <div style={{ background: '#fef3c7', color: '#b45309', padding: '8px', borderRadius: '8px' }}>
              <BookmarkCheck size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>
            {metrics?.saved_crops_count ?? 3}
          </div>
          <span style={{ fontSize: '0.78rem', color: '#b45309', fontWeight: 600 }}>Active Price Alerts</span>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600 }}>Total Forecasts</span>
            <div style={{ background: '#ede9fe', color: '#6d28d9', padding: '8px', borderRadius: '8px' }}>
              <TrendingUp size={18} />
            </div>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>
            {metrics?.farmer_predictions_count ?? 12}
          </div>
          <span style={{ fontSize: '0.78rem', color: '#6d28d9', fontWeight: 600 }}>Generated by ML models</span>
        </div>
      </div>

      {/* Live Karnataka Mandi Prices Table */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Sprout size={20} color="#16a34a" />
              <span>{t('todayMandiRates')}</span>
            </h3>
            <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px' }}>
              Standardized modal prices in ₹ per quintal (100 kg) across Karnataka agricultural markets.
            </p>
          </div>
          <Link to="/compare" className="btn btn-outline" style={{ fontSize: '0.82rem', padding: '6px 14px' }}>
            <span>Compare Markets</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Crop (Commodity)</th>
                <th>Category</th>
                <th>Market (Mandi)</th>
                <th>Modal Price (₹/Q)</th>
                <th>Min - Max Range (₹/Q)</th>
                <th>Arrivals (Q)</th>
                <th>7-Day Trend</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {allPrices.map((item, idx) => {
                const isUp = item.change_7d_pct > 0;
                const isDown = item.change_7d_pct < 0;
                return (
                  <tr key={idx}>
                    <td>
                      <strong style={{ color: '#0f172a' }}>{item.commodity}</strong>
                    </td>
                    <td>
                      <span className="badge badge-blue">{item.category}</span>
                    </td>
                    <td>{item.market} ({item.district})</td>
                    <td>
                      <strong style={{ fontSize: '1rem', color: '#15803d' }}>
                        ₹{item.modal_price.toLocaleString()}
                      </strong>
                    </td>
                    <td style={{ color: '#64748b', fontSize: '0.85rem' }}>
                      ₹{item.minimum_price.toLocaleString()} - ₹{item.maximum_price.toLocaleString()}
                    </td>
                    <td>{item.market_arrivals.toFixed(1)} Q</td>
                    <td>
                      <span className={`badge ${isUp ? 'badge-green' : isDown ? 'badge-red' : 'badge-amber'}`}>
                        {isUp ? <TrendingUp size={12} /> : isDown ? <TrendingDown size={12} /> : null}
                        {item.change_7d_pct > 0 ? `+${item.change_7d_pct}%` : `${item.change_7d_pct}%`}
                      </span>
                    </td>
                    <td>
                      <Link
                        to={`/predict?crop=${item.commodity}&market=${item.market}`}
                        className="btn btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '0.78rem' }}
                      >
                        Predict
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Predictions Overview */}
      {recentPredictions.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <TrendingUp size={20} color="#16a34a" />
              <span>Recent Price Forecasts</span>
            </h3>
            <Link to="/history" style={{ fontSize: '0.85rem', color: '#16a34a', textDecoration: 'none', fontWeight: 600 }}>
              View all history →
            </Link>
          </div>
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Market</th>
                  <th>Horizon</th>
                  <th>Current Price</th>
                  <th>Predicted Price</th>
                  <th>Expected Change</th>
                  <th>Selling Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {recentPredictions.map((pred, i) => (
                  <tr key={i}>
                    <td><strong>{pred.commodity}</strong></td>
                    <td>{pred.market}</td>
                    <td>{pred.horizon_days} Days</td>
                    <td>₹{pred.current_modal_price?.toLocaleString()}</td>
                    <td><strong>₹{pred.predicted_price?.toLocaleString()}</strong></td>
                    <td>
                      <span className={`badge ${pred.pct_change >= 0 ? 'badge-green' : 'badge-red'}`}>
                        {pred.pct_change >= 0 ? `+${pred.pct_change}%` : `${pred.pct_change}%`}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-amber">
                        {pred.recommendation?.action || 'Monitor'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default FarmerDashboard;
