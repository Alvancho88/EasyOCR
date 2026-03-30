import React, { useState } from 'react';
import axios from 'axios';

interface MenuItem {
  f: string;  // Food Name
  c: string;  // Calories
  ft: string; // Fat
  gi: string; // Glycemic Index
}

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [menu, setMenu] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return alert("Pilih gambar menu!");
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', formData);
      const data = typeof response.data.structuredData === 'string' 
        ? JSON.parse(response.data.structuredData) 
        : response.data.structuredData;
      
      setMenu(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      setError("Gagal memproses menu. Cuba lagi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h1 style={{ fontSize: '2.5rem' }}>SIDIA Health Scan</h1>
      
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={handleUpload} disabled={loading} style={{ padding: '10px 20px', margin: '10px 0', fontSize: '1.2rem' }}>
        {loading ? 'Scanning...' : 'Imbas Menu'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <div style={{ marginTop: '20px' }}>
        {menu.map((item, i) => (
          <div key={i} style={{ border: '2px solid #eee', borderRadius: '12px', padding: '15px', marginBottom: '10px' }}>
            <h3 style={{ fontSize: '1.8rem', margin: '0 0 10px 0' }}>{item.f}</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px', fontSize: '1.1rem' }}>
              <span>🔥 {item.c} kcal</span>
              <span>🥑 {item.ft}g Fat</span>
              <div style={{ 
                gridColumn: 'span 2', padding: '8px', borderRadius: '5px', textAlign: 'center', fontWeight: 'bold', marginTop: '10px',
                backgroundColor: item.gi === 'High' ? '#ffd7d7' : item.gi === 'Medium' ? '#fff4d7' : '#d7ffd9',
                color: item.gi === 'High' ? '#c0392b' : item.gi === 'Medium' ? '#d35400' : '#27ae60'
              }}>
                GI Level: {item.gi}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;