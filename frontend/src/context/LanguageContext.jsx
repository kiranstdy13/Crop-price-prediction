import React, { createContext, useContext, useState } from 'react';

const translations = {
  en: {
    appTitle: "KrishiMulya AI",
    subTitle: "Explainable Agricultural Price Forecast & Decision Support",
    dashboard: "Dashboard",
    predictPrices: "Predict Prices",
    marketComparison: "Market Comparison",
    savedCrops: "Saved Crops & Alerts",
    history: "Prediction History",
    adminPortal: "Admin Portal",
    login: "Sign In",
    logout: "Sign Out",
    welcomeFarmer: "Welcome back, Farmer",
    mandiStatus: "Live Karnataka APMC Data Synchronized",
    stateAverage: "Karnataka State Baseline",
    todayMandiRates: "Today's Karnataka APMC Rates",
    selectCrop: "Select Crop",
    selectMarket: "Select Mandi Market",
    selectHorizon: "Forecast Horizon",
    predictButton: "Generate Price Forecast & SHAP Analysis",
    predicting: "Calculating XGBoost Model & SHAP Explanations...",
    currentPrice: "Current Modal Price",
    predictedPrice: "Predicted Future Price",
    expectedChange: "Expected Change",
    priceDirection: "Price Direction",
    modelName: "Model Architecture",
    shapTitle: "Why did the model predict this price? (SHAP Explainability)",
    shapSubtitle: "Feature attribution calculated using TreeExplainer. Explains positive and negative price factors.",
    baseValue: "State Baseline Value",
    reconciliation: "Exact SHAP Additivity Reconciliation",
    recommendationTitle: "Smart Selling Recommendation (Decision Support)",
    marketCompareTitle: "Karnataka Mandi Cross-Market Comparison",
    bestNetMandi: "Best Mandi by Net Proceeds (After Freight)",
    adminTitle: "Agricultural ML Administration & Operations",
    uploadDataset: "Upload AGMARKNET Dataset (CSV)",
    triggerRetraining: "Retrain Machine Learning Pipeline",
    modelMetrics: "Chronological Evaluation Metrics (Test Set)",
    days: "Days"
  },
  kn: {
    appTitle: "ಕೃಷಿಮೌಲ್ಯ AI",
    subTitle: "ಕರ್ನಾಟಕ ಕೃಷಿ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮುನ್ಸೂಚನೆ ಮತ್ತು ನಿರ್ಧಾರ ಬೆಂಬಲ ವ್ಯವಸ್ಥೆ",
    dashboard: "ಮುಖಪುಟ",
    predictPrices: "ಬೆಲೆ ಮುನ್ಸೂಚನೆ",
    marketComparison: "ಮಾರುಕಟ್ಟೆ ಹೋಲಿಕೆ",
    savedCrops: "ಉಳಿಸಿದ ಬೆಳೆಗಳು ಮತ್ತು ಎಚ್ಚರಿಕೆಗಳು",
    history: "ಹಿಂದಿನ ಮುನ್ಸೂಚನೆಗಳು",
    adminPortal: "ನಿರ್ವಾಹಕ ಪೋರ್ಟಲ್",
    login: "ಪ್ರವೇಶಿಸಿ",
    logout: "ನಿರ್ಗಮಿಸಿ",
    welcomeFarmer: "ರೈತ ಬಾಂಧವರಿಗೆ ಸುಸ್ವಾಗತ",
    mandiStatus: "ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ದತ್ತಾಂಶ ನವೀಕೃತಗೊಂಡಿದೆ",
    stateAverage: "ರಾಜ್ಯ ಸರಾಸರಿ ದರ",
    todayMandiRates: "ಇಂದಿನ ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ದರಗಳು",
    selectCrop: "ಬೆಳೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    selectMarket: "ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ಆಯ್ಕೆಮಾಡಿ",
    selectHorizon: "ಮುನ್ಸೂಚನಾ ಅವಧಿ",
    predictButton: "ಬೆಲೆ ಮುನ್ಸೂಚನೆ ಮತ್ತು SHAP ವಿಶ್ಲೇಷಣೆ ಪಡೆಯಿರಿ",
    predicting: "ಯಂತ್ರ ಕಲಿಕೆ ಮತ್ತು SHAP ಲೆಕ್ಕಾಚಾರ ಮಾಡಲಾಗುತ್ತಿದೆ...",
    currentPrice: "ಪ್ರಸ್ತುತ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ",
    predictedPrice: "ಅಂದಾಜು ಭವಿಷ್ಯದ ಬೆಲೆ",
    expectedChange: "ನಿರೀಕ್ಷಿತ ಬದಲಾವಣೆ",
    priceDirection: "ಬೆಲೆಯ ದಿಕ್ಕು",
    modelName: "ಮಾದರಿ ತಂತ್ರಜ್ಞಾನ",
    shapTitle: "ಮಾದರಿಯು ಈ ಬೆಲೆಯನ್ನು ಏಕೆ ಅಂದಾಜಿಸಿದೆ? (SHAP ವಿವರಣೆ)",
    shapSubtitle: "ಯಂತ್ರ ಕಲಿಕೆ ಆಧಾರಿತ ಧನಾತ್ಮಕ ಮತ್ತು ಋಣಾತ್ಮಕ ಅಂಶಗಳ ವಿಶ್ಲೇಷಣೆ.",
    baseValue: "ರಾಜ್ಯ ಸರಾಸರಿ ಮೂಲ ಬೆಲೆ",
    reconciliation: "ನಿಖರ ಗಣಿತೀಯ ಹೊಂದಾಣಿಕೆ",
    recommendationTitle: "ಬುದ್ಧಿವಂತ ಮಾರಾಟ ಶಿಫಾರಸು (ನಿರ್ಧಾರ ಬೆಂಬಲ)",
    marketCompareTitle: "ಕರ್ನಾಟಕ ಮಂಡಿ ಮಾರುಕಟ್ಟೆಗಳ ಹೋಲಿಕೆ",
    bestNetMandi: "ಹೆಚ್ಚು ನಿವ್ವಳ ಲಾಭ ನೀಡುವ ಮಾರುಕಟ್ಟೆ (ಸಾರಿಗೆ ವೆಚ್ಚ ಕಳೆದು)",
    adminTitle: "ಕೃಷಿ ಯಂತ್ರ ಕಲಿಕೆ ನಿರ್ವಹಣೆ ಮತ್ತು ಅಂಕಿಅಂಶಗಳು",
    uploadDataset: "ಹೊಸ ಎಪಿಎಂಸಿ ದತ್ತಾಂಶ ಅಪ್‌ಲೋಡ್ (CSV)",
    triggerRetraining: "ಮಾದರಿಗಳನ್ನು ಮರು ತರಬೇತಿಗೊಳಿಸಿ",
    modelMetrics: "ಮಾದರಿ ನಿಖರತೆಯ ಮೌಲ್ಯಮಾಪನ ವರದಿ",
    days: "ದಿನಗಳು"
  }
};

const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState('en');

  const t = (key) => {
    return translations[lang]?.[key] || translations['en']?.[key] || key;
  };

  const toggleLanguage = () => {
    setLang((prev) => (prev === 'en' ? 'kn' : 'en'));
  };

  return (
    <LanguageContext.Provider value={{ lang, setLang, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
