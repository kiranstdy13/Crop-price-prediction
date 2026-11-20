import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useLanguage } from '../context/LanguageContext';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';
import {
  GitCompare,
  TrendingUp,
  Truck,
  CheckCircle2,
  Wheat,
  Building2,
  AlertCircle
} from 'lucide-react';

const MarketComparisonPage = () => {
  const { t, lang } = useLanguage();
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('Tomato');
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCrops = async () => {
      try {
        const res = await api.get('/markets/crops');
        if (res.data?.crops) setCrops(res.data.crops);
      } catch (err) {
        console.error("Crops fetch error:", err);
      }
    };
    fetchCrops();
  }, []);

  useEffect(() => {
    const fetchComparison = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await api.get(`/markets/compare?commodity=${selectedCrop}`);
        setComparisonData(res.data);
      } catch (err) {
        console.error("Comparison error:", err);
        setError("Could not load market comparison for selected crop.");
      } finally {
        setLoading(false);
      }
    };
    if (selectedCrop) {
      fetchComparison();
    }
  }, [selectedCrop]);

  return (
    <div className="content-body">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <GitCompare color="#16a34a" size={26} />
          <span>{t('marketCompareTitle')}</span>
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.92rem', marginTop: '4px' }}>
          Compare current prices, 7-day predicted prices, and net earnings after freight costs across Karnataka APMC mandis.
        </p>
      </div>

      {/* Crop Selector Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Wheat size={18} color="#15803d" />
            <strong style={{ fontSize: '0.92rem' }}>{t('selectCrop')}:</strong>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {(crops.length > 0 ? crops.map(c => c.commodity) : ['Tomato', 'Onion', 'Potato', 'Cabbage', 'Green Chilli', 'Rice', 'Maize', 'Groundnut']).map((cName) => (
              <button
                key={cName}
                onClick={() => setSelectedCrop(cName)}
                className={`btn ${selectedCrop === cName ? 'btn-primary' : 'btn-outline'}`}
                style={{ padding: '7px 16px', fontSize: '0.85rem' }}
              >
                {cName}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '50px', color: '#16a34a' }}>
          Loading Karnataka Mandi comparison data...
        </div>
      ) : error ? (
        <div className="card" style={{ color: '#e11d48', padding: '30px', textAlign: 'center' }}>
          <AlertCircle size={24} style={{ margin: '0 auto 8px auto' }} />
          <div>{error}</div>
        </div>
      ) : comparisonData ? (
        <>
          {/* Key Findings Card */}
          <div className="grid-3" style={{ marginBottom: '24px' }}>
            <div className="card" style={{ borderLeft: '4px solid #16a34a' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>HIGHEST RAW MANDI PRICE</span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {comparisonData.highest_price_mandi?.market} Mandi
              </div>
              <span style={{ fontSize: '0.9rem', color: '#16a34a', fontWeight: 700 }}>
                ₹{comparisonData.highest_price_mandi?.current_modal_price.toLocaleString()} / Q
              </span>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #0284c7' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>BEST NET GAIN (AFTER FREIGHT)</span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {comparisonData.best_net_mandi?.market} Mandi
              </div>
              <span style={{ fontSize: '0.9rem', color: '#0284c7', fontWeight: 700 }}>
                ₹{comparisonData.best_net_mandi?.net_after_transport.toLocaleString()} / Q Net
              </span>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #f59e0b' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>LOWEST MANDI PRICE</span>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', margin: '4px 0' }}>
                {comparisonData.lowest_price_mandi?.market} Mandi
              </div>
              <span style={{ fontSize: '0.9rem', color: '#f59e0b', fontWeight: 700 }}>
                ₹{comparisonData.lowest_price_mandi?.current_modal_price.toLocaleString()} / Q
              </span>
            </div>
          </div>

          {/* Analysis Note */}
          <div className="card" style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
              <CheckCircle2 size={20} color="#15803d" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong style={{ fontSize: '0.92rem', color: '#166534' }}>Decision Support Analysis:</strong>
                <p style={{ fontSize: '0.9rem', color: '#14532d', marginTop: '4px', lineHeight: 1.5 }}>
                  {lang === 'kn' ? comparisonData.analysis_kn : comparisonData.analysis_en}
                </p>
              </div>
            </div>
          </div>

          {/* Graphical Comparison Chart */}
          <div className="card" style={{ marginBottom: '24px' }}>
            <div className="card-header">
              <h3 className="card-title">
                <GitCompare size={19} color="#16a34a" />
                <span>Modal Price vs 7-Day Forecast Across Mandis</span>
              </h3>
            </div>
            <div style={{ width: '100%', height: 320 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={comparisonData.markets || []} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="market" stroke="#64748b" />
                  <YAxis domain={['auto', 'auto']} stroke="#64748b" tickFormatter={(v) => `₹${v}`} />
                  <Tooltip formatter={(v) => `₹${v?.toLocaleString()}/quintal`} />
                  <Legend />
                  <Bar dataKey="current_modal_price" name="Current Modal Price (₹/Q)" fill="#16a34a" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="predicted_7d_price" name="Predicted 7-Day Price (₹/Q)" fill="#2563eb" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="net_after_transport" name="Net Proceeds (After Transport)" fill="#0d9488" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Comparison Table */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Detailed Mandi Economics Table</h3>
            </div>
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Market (Mandi)</th>
                    <th>District</th>
                    <th>Current Modal Price</th>
                    <th>Min - Max Range</th>
                    <th>Arrivals (Q)</th>
                    <th>Predicted 7-Day Price</th>
                    <th>Transport Freight</th>
                    <th>Net Return (₹/Q)</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.markets.map((m, idx) => (
                    <tr key={idx}>
                      <td><strong>{m.market}</strong></td>
                      <td>{m.district}</td>
                      <td>
                        <strong style={{ color: '#15803d' }}>₹{m.current_modal_price.toLocaleString()}</strong>
                      </td>
                      <td style={{ color: '#64748b', fontSize: '0.85rem' }}>
                        ₹{m.minimum_price.toLocaleString()} - ₹{m.maximum_price.toLocaleString()}
                      </td>
                      <td>{m.market_arrivals.toFixed(1)} Q</td>
                      <td><strong>₹{m.predicted_7d_price.toLocaleString()}</strong></td>
                      <td style={{ color: '#e11d48' }}>-₹{m.transport_cost_per_quintal}</td>
                      <td>
                        <strong style={{ fontSize: '1rem', color: '#0369a1' }}>
                          ₹{m.net_after_transport.toLocaleString()}
                        </strong>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default MarketComparisonPage;
