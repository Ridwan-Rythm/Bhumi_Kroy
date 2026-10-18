import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import Form from "./pages/Form";
import Checking from "./pages/Checking";
import Result from "./pages/Result";
import Verify from "./pages/Verify";
import PrintReport from "./pages/PrintReport";
import Demo from "./pages/Demo";
import NotFound from "./pages/NotFound";

// Routes from workflow B0.1 item 6. The QR and demo routes get lazy-loaded in B4.
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/check" element={<Form />} />
        <Route path="/checking" element={<Checking />} />
        <Route path="/result/:reportId" element={<Result />} />
        <Route path="/verify" element={<Verify />} />
        <Route path="/report/:reportId/print" element={<PrintReport />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
