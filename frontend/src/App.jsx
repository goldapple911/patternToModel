import React from 'react';
import { ToastContainer } from 'react-toastify';

import Header from './components/Header';
import Footer from './components/Footer';
import MainVisual from './components/MainVisual';
import FormWindow from './components/FormWindow';
import FileUploadForm from './components/FileUploadForm';

import 'react-toastify/dist/ReactToastify.css';
import './App.css';

const App = () => {
  return (
    <div className="app">
      <Header />
      <main>
        <FileUploadForm />
        <ToastContainer />
        {/* <MainVisual />
        <FormWindow /> */}
      </main>
      <Footer />
    </div>
  );
};

export default App;
