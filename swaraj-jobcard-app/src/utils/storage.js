import { INITIAL_JOB_CARDS } from '../data/initialJobCards';
import { INITIAL_SWARAJ_CATALOG } from '../data/swarajCatalog';

const STORAGE_KEYS = {
  JOB_CARDS: 'swaraj_job_cards_v1',
  PARTS_CATALOG: 'swaraj_parts_catalog_v1'
};

export const loadJobCardsFromStorage = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.JOB_CARDS);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (e) {
    console.error('Failed to load job cards from localStorage', e);
  }
  return INITIAL_JOB_CARDS;
};

export const saveJobCardsToStorage = (jobCards) => {
  try {
    localStorage.setItem(STORAGE_KEYS.JOB_CARDS, JSON.stringify(jobCards));
  } catch (e) {
    console.error('Failed to save job cards to localStorage', e);
  }
};

export const loadPartsCatalogFromStorage = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEYS.PARTS_CATALOG);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (e) {
    console.error('Failed to load catalog from localStorage', e);
  }
  return INITIAL_SWARAJ_CATALOG;
};

export const savePartsCatalogToStorage = (catalog) => {
  try {
    localStorage.setItem(STORAGE_KEYS.PARTS_CATALOG, JSON.stringify(catalog));
  } catch (e) {
    console.error('Failed to save catalog to localStorage', e);
  }
};

export const resetToDemoData = () => {
  localStorage.setItem(STORAGE_KEYS.JOB_CARDS, JSON.stringify(INITIAL_JOB_CARDS));
  localStorage.setItem(STORAGE_KEYS.PARTS_CATALOG, JSON.stringify(INITIAL_SWARAJ_CATALOG));
  return { jobCards: INITIAL_JOB_CARDS, catalog: INITIAL_SWARAJ_CATALOG };
};
