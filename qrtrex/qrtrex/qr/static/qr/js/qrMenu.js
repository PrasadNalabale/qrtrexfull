

// Store original nodes and their corresponding texts
let originalNodes = { translate: [], transliterate: [] };
let originalTexts = { translate: [], transliterate: [] };

// Recursive function to find all text nodes in a given element
// Recursive function to find all text nodes in a given element
function getTextNodesIn(el) {
  let nodes = [];
  
  // Only collect text nodes from elements that are not excluded
  if (el.nodeType === Node.TEXT_NODE && el.nodeValue.trim()) {
    // Check if the parent element of this text node has the `.no-translate` class
    const parentElement = el.parentElement;
    if (parentElement && !parentElement.closest('.no-translate')) {
      nodes.push(el);
    }
  } else {
    for (let child of el.childNodes) {
      nodes = nodes.concat(getTextNodesIn(child));
    }
  }
  return nodes;
}


// Collect initial text nodes and their original content
function collectTextNodes() {
  const translateNodes = [];
  const translateTexts = [];

  const translateElements = document.querySelectorAll('.translate');
  translateElements.forEach(el => {
    const nodes = getTextNodesIn(el);
    nodes.forEach(n => {
      translateNodes.push(n);
      translateTexts.push(n.nodeValue.trim());
    });
  });

  // Get transliterate nodes excluding those in '.no-translate' class
  const allNodes = getTextNodesIn(document.body);
  const translateSet = new Set(translateNodes);
  const transliterateNodes = allNodes.filter(n => !translateSet.has(n));
  const transliterateTexts = transliterateNodes.map(n => n.nodeValue.trim());

  // Save original nodes and texts
  originalNodes.translate = translateNodes;
  originalNodes.transliterate = transliterateNodes;
  originalTexts.translate = translateTexts;
  originalTexts.transliterate = transliterateTexts;
}

// Fetch translated or transliterated data from the server
async function fetchLanguageData(texts, lang, mode) {
  const formData = new FormData();
  texts.forEach(text => formData.append('texts[]', text));
  formData.append('language', lang);

  const url = mode === 'translate' ? '/api/translate/' : '/api/transliterate/';
//   const response = await fetch(url, { method: 'POST', body: formData });
//   const result = await response.json();

//   // Use `translated` or `transliterated` fields; fallback to original
//   return result.translated || result.transliterated || texts;
// }
  try {
    const response = await fetch(url, { method: 'POST', body: formData });
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const result = await response.json();
    return result.translated || result.transliterated || texts;
  } catch (error) {
    console.error(`Failed to fetch ${mode} data:`, error);
    return texts;  // fallback to original texts on error
  }
}

// Apply selected language
// async function applyLanguage(lang) {
//   localStorage.setItem('lang', lang);


//   const [translated, transliterated] = await Promise.all([ 
//     fetchLanguageData(originalTexts.translate, lang, 'translate'),
//     fetchLanguageData(originalTexts.transliterate, lang, 'transliterate')
//   ]);

//   // Update the text content for translation
//   originalNodes.translate.forEach((node, i) => {
//     node.nodeValue = translated[i];
//   });
async function applyLanguage(lang) {
  localStorage.setItem('lang', lang);

  const [translated, transliterated] = await Promise.all([
    fetchLanguageData(originalTexts.translate, lang, 'translate'),
    fetchLanguageData(originalTexts.transliterate, lang, 'transliterate')
  ]);

  // Safely update nodes if data length matches
  originalNodes.translate.forEach((node, i) => {
    if (translated[i] !== undefined) node.nodeValue = translated[i];
  });

  originalNodes.transliterate.forEach((node, i) => {
    if (transliterated[i] !== undefined) node.nodeValue = transliterated[i];
  });
}
//   // Update the text content for transliteration
//   originalNodes.transliterate.forEach((node, i) => {
//     node.nodeValue = transliterated[i];
//   });
// }

// Restore original English content
function restoreEnglish() {
  localStorage.setItem('lang', 'en');

  // Restore text for translation
  originalNodes.translate.forEach((node, i) => {
    node.nodeValue = originalTexts.translate[i];
  });

  // Restore text for transliteration
  originalNodes.transliterate.forEach((node, i) => {
    node.nodeValue = originalTexts.transliterate[i];
  });
}

// Setup language buttons and apply saved language on load
function setupLanguageSwitcher() {
  collectTextNodes();

  // Set up language switcher buttons
  document.getElementById('lang-en')?.addEventListener('click', restoreEnglish);
  document.getElementById('lang-mr')?.addEventListener('click', () => applyLanguage('mr'));
  document.getElementById('lang-hi')?.addEventListener('click', () => applyLanguage('hi'));

  const savedLang = localStorage.getItem('lang');
  if (savedLang && savedLang !== 'en') {
    applyLanguage(savedLang);
  }
}

// Listen for DOMContentLoaded event to initialize the language switcher
document.addEventListener('DOMContentLoaded', setupLanguageSwitcher);








// let originalNodes = { translate: [], transliterate: [] };
// let originalTexts = { translate: [], transliterate: [] };

// // Recursive function to find all text nodes in a given element
// function getTextNodesIn(el) {
//   let nodes = [];
//   if (el.nodeType === Node.TEXT_NODE && el.nodeValue.trim()) {
//     nodes.push(el);
//   } else {
//     for (let child of el.childNodes) {
//       nodes = nodes.concat(getTextNodesIn(child));
//     }
//   }
//   return nodes;
// }

// // Collect initial text nodes and their original content
// function collectTextNodes() {
//   const translateNodes = [];
//   const translateTexts = [];

//   const translateElements = document.querySelectorAll('.translate');
//   translateElements.forEach(el => {
//     const nodes = getTextNodesIn(el);
//     nodes.forEach(n => {
//       translateNodes.push(n);
//       translateTexts.push(n.nodeValue.trim());
//     });
//   });

//   const allNodes = getTextNodesIn(document.body);
//   const translateSet = new Set(translateNodes);
//   const transliterateNodes = allNodes.filter(n => !translateSet.has(n));
//   const transliterateTexts = transliterateNodes.map(n => n.nodeValue.trim());

//   originalNodes.translate = translateNodes;
//   originalNodes.transliterate = transliterateNodes;
//   originalTexts.translate = translateTexts;
//   originalTexts.transliterate = transliterateTexts;
// }

// // Fetch translated or transliterated data from the server
// async function fetchLanguageData(texts, lang, mode) {
//   const formData = new FormData();
//   texts.forEach(text => formData.append('texts[]', text));
//   formData.append('language', lang);

//   const url = mode === 'translate' ? '/api/translate/' : '/api/transliterate/';
//   const response = await fetch(url, { method: 'POST', body: formData });
//   const result = await response.json();

//   // Use `translated` or `transliterated` fields; fallback to original
//   return result.translated || result.transliterated || texts;
// }

// // Apply selected language
// async function applyLanguage(lang) {
//   localStorage.setItem('lang', lang);

//   const [translated, transliterated] = await Promise.all([
//     fetchLanguageData(originalTexts.translate, lang, 'translate'),
//     fetchLanguageData(originalTexts.transliterate, lang, 'transliterate')
//   ]);

//   originalNodes.translate.forEach((node, i) => {
//     node.nodeValue = translated[i];
//   });
//   originalNodes.transliterate.forEach((node, i) => {
//     node.nodeValue = transliterated[i];
//   });
// }

// // Restore original English content
// function restoreEnglish() {
//   localStorage.setItem('lang', 'en');

//   originalNodes.translate.forEach((node, i) => {
//     node.nodeValue = originalTexts.translate[i];
//   });
//   originalNodes.transliterate.forEach((node, i) => {
//     node.nodeValue = originalTexts.transliterate[i];
//   });
// }

// // Setup language buttons and apply saved language on load
// function setupLanguageSwitcher() {
//   collectTextNodes();

//   document.getElementById('lang-en')?.addEventListener('click', restoreEnglish);
//   document.getElementById('lang-mr')?.addEventListener('click', () => applyLanguage('mr'));
//   document.getElementById('lang-hi')?.addEventListener('click', () => applyLanguage('hi'));

//   const savedLang = localStorage.getItem('lang');
//   if (savedLang && savedLang !== 'en') {
//     applyLanguage(savedLang);
//   }
// }

// document.addEventListener('DOMContentLoaded', setupLanguageSwitcher);

// document.getElementById('menuSearch').addEventListener('input', function () {
//   const filter = this.value.toLowerCase();
//   const items = document.querySelectorAll('#menuList li');

//   items.forEach(item => {
//     const text = item.textContent.toLowerCase();
//     if (filter === '') {
//       // Reset if empty
//       item.innerHTML = item.textContent;
//       item.style.display = '';
//     } else if (text.includes(filter)) {
//       // Highlight match
//       const regex = new RegExp(`(${filter})`, 'gi');
//       const highlighted = item.textContent.replace(regex, '<mark>$1</mark>');
//       item.innerHTML = highlighted;
//       item.style.display = '';
//     } else {
//       item.style.display = 'none';
//     }
//   });
// });


window.applyLanguage = applyLanguage;
window.collectTextNodes = collectTextNodes;
