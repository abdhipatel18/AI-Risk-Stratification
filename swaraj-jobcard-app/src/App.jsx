import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardOverview } from './components/DashboardOverview';
import { JobCardFormModal } from './components/JobCardFormModal';
import { JobCardDetailModal } from './components/JobCardDetailModal';
import { PartsCatalogModal } from './components/PartsCatalogModal';
import { PrintableInvoice } from './components/PrintableInvoice';

import { 
  loadJobCardsFromStorage, 
  saveJobCardsToStorage, 
  loadPartsCatalogFromStorage, 
  savePartsCatalogToStorage, 
  resetToDemoData 
} from './utils/storage';

export function App() {
  const [jobCards, setJobCards] = useState([]);
  const [catalog, setCatalog] = useState([]);

  // Modal States
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingJobCard, setEditingJobCard] = useState(null);

  const [selectedDetailCard, setSelectedDetailCard] = useState(null);
  const [selectedPrintCard, setSelectedPrintCard] = useState(null);
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);

  // Initial Load from LocalStorage
  useEffect(() => {
    const loadedCards = loadJobCardsFromStorage();
    const loadedCatalog = loadPartsCatalogFromStorage();
    setJobCards(loadedCards);
    setCatalog(loadedCatalog);
  }, []);

  // Save to LocalStorage whenever state changes
  const handleSaveJobCards = (newCards) => {
    setJobCards(newCards);
    saveJobCardsToStorage(newCards);
  };

  const handleSaveCatalog = (newCatalog) => {
    setCatalog(newCatalog);
    savePartsCatalogToStorage(newCatalog);
  };

  // Create or Update Job Card
  const handleSaveJobCardForm = (cardData) => {
    let updatedCards;
    const exists = jobCards.some(c => c.id === cardData.id);

    if (exists) {
      updatedCards = jobCards.map(c => c.id === cardData.id ? cardData : c);
    } else {
      updatedCards = [cardData, ...jobCards];
    }

    // Adjust catalog stock for used parts installed in this card!
    if (cardData.usedParts && cardData.usedParts.length > 0) {
      const updatedCatalog = catalog.map(catItem => {
        const usedInCard = cardData.usedParts.find(p => p.partNumber === catItem.partNumber);
        if (usedInCard) {
          const newQty = Math.max(0, catItem.stockQty - Number(usedInCard.quantity));
          return { ...catItem, stockQty: newQty };
        }
        return catItem;
      });
      handleSaveCatalog(updatedCatalog);
    }

    handleSaveJobCards(updatedCards);
    setIsFormOpen(false);
    setEditingJobCard(null);
  };

  // Delete Job Card
  const handleDeleteJobCard = (id) => {
    if (window.confirm('Are you sure you want to delete this job card?')) {
      const updated = jobCards.filter(c => c.id !== id);
      handleSaveJobCards(updated);
    }
  };

  // Handlers for Modals
  const handleOpenCreateForm = () => {
    setEditingJobCard(null);
    setIsFormOpen(true);
  };

  const handleOpenEditForm = (card) => {
    setEditingJobCard(card);
    setIsFormOpen(true);
  };

  const handleResetDemoData = () => {
    if (window.confirm('Reset all job cards and catalog stock to initial demo data?')) {
      const reset = resetToDemoData();
      setJobCards(reset.jobCards);
      setCatalog(reset.catalog);
    }
  };

  const handleExportData = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ jobCards, catalog }, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Swaraj_JobCards_Backup_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const activeCount = jobCards.filter(c => c.status === 'In Service' || c.status === 'Open').length;
  const lowStockCount = catalog.filter(c => c.stockQty < 10).length;

  return (
    <div className="app-layout">
      <Navbar 
        onOpenCreate={handleOpenCreateForm}
        onOpenCatalog={() => setIsCatalogOpen(true)}
        onResetDemo={handleResetDemoData}
        onExportData={handleExportData}
        activeCount={activeCount}
        lowStockCount={lowStockCount}
      />

      <main className="main-content">
        <DashboardOverview 
          jobCards={jobCards}
          onSelectJobCard={(card) => setSelectedDetailCard(card)}
          onEditJobCard={(card) => handleOpenEditForm(card)}
          onDeleteJobCard={handleDeleteJobCard}
          onPrintInvoice={(card) => setSelectedPrintCard(card)}
          onNewJobCard={handleOpenCreateForm}
        />
      </main>

      {/* Form Modal */}
      <JobCardFormModal 
        isOpen={isFormOpen}
        onClose={() => { setIsFormOpen(false); setEditingJobCard(null); }}
        onSave={handleSaveJobCardForm}
        editingJobCard={editingJobCard}
        catalog={catalog}
      />

      {/* Detail Inspector Modal */}
      <JobCardDetailModal 
        jobCard={selectedDetailCard}
        onClose={() => setSelectedDetailCard(null)}
        onEdit={(card) => { setSelectedDetailCard(null); handleOpenEditForm(card); }}
        onPrint={(card) => { setSelectedDetailCard(null); setSelectedPrintCard(card); }}
      />

      {/* Spare Parts Inventory Catalog Modal */}
      <PartsCatalogModal 
        isOpen={isCatalogOpen}
        onClose={() => setIsCatalogOpen(false)}
        catalog={catalog}
        onSaveCatalog={handleSaveCatalog}
      />

      {/* Printable Invoice Modal */}
      {selectedPrintCard && (
        <PrintableInvoice 
          jobCard={selectedPrintCard}
          onClose={() => setSelectedPrintCard(null)}
        />
      )}
    </div>
  );
}

export default App;
