import React, { useState, ChangeEvent } from 'react';
import axios from 'axios';

// Define the shape of our nutrition data
interface NutritionItem {
  f: string;  // Food name
  c: number;  // Calories
  ft: number; // Fat
  gi: string; // Glycemic Index (Low/Med/High)
}

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [results, setResults] = useState<NutritionItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Handle image selection and create a preview
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResults([]); // Clear previous results
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Sila pilih gambar menu terlebih dahulu.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // On Vercel, /api/predict automatically points to your index.py
      const response = await axios.post('/api/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      // Handle the response data from Cerebras/Groq
      const data = response.data;
      setResults(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error("Upload error:", err);
      setError("Gagal memproses menu. Sila pastikan gambar jelas dan cuba lagi.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-8 font-sans">
      <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md overflow-hidden p-6">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-600">MANIS</h1>
          <p className="text-gray-500 text-lg">Health & Nutrition Tracker for Seniors</p>
        </header>

        {/* Upload Section */}
        <div className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-6 mb-6">
          {preview ? (
            <img src={preview} alt="Preview" className="max-h-64 rounded mb-4" />
          ) : (
            <div className="text-gray-400 mb-4 text-center">
              <p>Ambil gambar menu atau muat naik fail</p>
            </div>
          )}
          
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <button 
          onClick={handleUpload}
          disabled={loading || !file}
          className={`w-full py-4 rounded-lg text-xl font-bold transition ${
            loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {loading ? "Sedang Mengimbas..." : "Imbas Menu"}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded text-center">
            {error}
          </div>
        )}

        {/* Results Section */}
        <div className="mt-10">
          {results.length > 0 && (
            <h2 className="text-2xl font-bold mb-4 border-b pb-2">Hasil Analisis</h2>
          )}
          
          <div className="space-y-4">
            {results.map((item, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg shadow-sm border-l-4 border-blue-500">
                <div className="flex justify-between items-center">
                  <span className="text-xl font-semibold text-gray-800">{item.f}</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    item.gi === 'Low' ? 'bg-green-100 text-green-700' : 
                    item.gi === 'Medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                  }`}>
                    GI: {item.gi}
                  </span>
                </div>
                <div className="mt-2 text-gray-600 flex gap-4">
                  <span>🔥 {item.c} kcal</span>
                  <span>⚖️ {item.ft}g Lemak</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;