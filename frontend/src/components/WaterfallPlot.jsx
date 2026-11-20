import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { ArrowUpRight, ArrowDownRight, CheckCircle2 } from 'lucide-react';

const WaterfallPlot = ({ waterfallData, baseValue, predictedPrice, reconciliationDiff }) => {
  const { lang } = useLanguage();

  if (!waterfallData || waterfallData.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>
        No SHAP waterfall data available.
      </div>
    );
  }

  // Calculate dynamic scale for visualization
  const allValues = waterfallData.map(d => d.total).concat([baseValue, predictedPrice]);
  const minVal = Math.min(...allValues) * 0.92;
  const maxVal = Math.max(...allValues) * 1.05;
  const range = maxVal - minVal || 1;

  const getWidthPercent = (val) => {
    return Math.max(2, Math.min(100, ((val - minVal) / range) * 100));
  };

  return (
    <div style={{ background: '#ffffff', borderRadius: '12px', padding: '16px 8px' }}>
      {/* Reconciliation Alert Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '10px 16px',
        background: '#f0fdf4',
        border: '1px solid #bbf7d0',
        borderRadius: '8px',
        marginBottom: '20px',
        fontSize: '0.85rem',
        color: '#166534'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={18} color="#15803d" />
          <span>
            <strong>SHAP Mathematical Additivity:</strong> Base Value (₹{baseValue.toLocaleString()}) + Σ SHAP = Predicted Price (₹{predictedPrice.toLocaleString()})
          </span>
        </div>
        <span style={{ fontSize: '0.78rem', color: '#15803d', fontWeight: 600 }}>
          Diff: ±₹{reconciliationDiff || 0}
        </span>
      </div>

      {/* Waterfall steps list */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {waterfallData.map((item, idx) => {
          const isBase = item.type === 'baseline';
          const isFinal = item.type === 'final';
          const isPositive = item.amount >= 0 && !isBase && !isFinal;
          const isNegative = item.amount < 0 && !isBase && !isFinal;

          const barColor = isBase
            ? '#64748b'
            : isFinal
            ? '#2563eb'
            : isPositive
            ? '#16a34a'
            : '#e11d48';

          const label = (lang === 'kn' && item.name_kn) ? item.name_kn : item.name;

          return (
            <div
              key={idx}
              style={{
                display: 'grid',
                gridTemplateColumns: '260px 1fr 140px',
                alignItems: 'center',
                gap: '16px',
                padding: '8px 12px',
                borderRadius: '8px',
                background: isFinal ? '#f8fafc' : 'transparent',
                border: isFinal ? '1px dashed #cbd5e1' : 'none'
              }}
            >
              {/* Feature Name */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {isPositive && <ArrowUpRight size={16} color="#16a34a" />}
                {isNegative && <ArrowDownRight size={16} color="#e11d48" />}
                <span style={{
                  fontSize: '0.88rem',
                  fontWeight: (isBase || isFinal) ? 700 : 500,
                  color: isFinal ? '#1e3a8a' : (isBase ? '#334155' : '#0f172a'),
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {label}
                </span>
              </div>

              {/* Graphical Bar */}
              <div style={{ position: 'relative', height: '26px', background: '#f1f5f9', borderRadius: '6px', overflow: 'hidden' }}>
                <div
                  style={{
                    position: 'absolute',
                    left: `${getWidthPercent(Math.min(item.start, item.total))}%`,
                    width: `${Math.max(1.5, Math.abs(getWidthPercent(item.total) - getWidthPercent(item.start)))}%`,
                    height: '100%',
                    background: barColor,
                    borderRadius: '4px',
                    transition: 'all 0.3s ease'
                  }}
                />
              </div>

              {/* Amount and Subtotal */}
              <div style={{ textAlign: 'right', fontSize: '0.86rem' }}>
                {!isBase && !isFinal && (
                  <span style={{
                    fontWeight: 700,
                    color: isPositive ? '#16a34a' : '#e11d48',
                    marginRight: '6px'
                  }}>
                    {isPositive ? `+₹${item.amount.toLocaleString()}` : `-₹${Math.abs(item.amount).toLocaleString()}`}
                  </span>
                )}
                <span style={{ color: '#475569', fontWeight: (isBase || isFinal) ? 800 : 500 }}>
                  (₹{item.total.toLocaleString()})
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default WaterfallPlot;
