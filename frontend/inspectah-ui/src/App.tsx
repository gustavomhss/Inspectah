import { BrowserRouter, Route, Routes } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import ConsultationRoute from './routes/ConsultationRoute';

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<ConsultationRoute />} />
          <Route path="*" element={<ConsultationRoute />} />
        </Routes>
      </AppShell>
    </BrowserRouter>
  );
}

export default App;
