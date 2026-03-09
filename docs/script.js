// Language switching functionality
let currentLang = 'ru';

const translations = {
    ru: {},
    en: {}
};

// Initialize language switcher
document.addEventListener('DOMContentLoaded', function() {
    const langRuBtn = document.getElementById('lang-ru');
    const langEnBtn = document.getElementById('lang-en');
    
    // Load saved language preference
    const savedLang = localStorage.getItem('preferredLanguage') || 'ru';
    switchLanguage(savedLang);
    
    langRuBtn.addEventListener('click', () => switchLanguage('ru'));
    langEnBtn.addEventListener('click', () => switchLanguage('en'));
});

function switchLanguage(lang) {
    currentLang = lang;
    
    // Update button states
    const langRuBtn = document.getElementById('lang-ru');
    const langEnBtn = document.getElementById('lang-en');
    
    if (lang === 'ru') {
        langRuBtn.classList.add('active');
        langEnBtn.classList.remove('active');
        document.documentElement.lang = 'ru';
    } else {
        langEnBtn.classList.add('active');
        langRuBtn.classList.remove('active');
        document.documentElement.lang = 'en';
    }
    
    // Update all translatable elements
    const elements = document.querySelectorAll('[data-ru][data-en]');
    elements.forEach(element => {
        const text = element.getAttribute(`data-${lang}`);
        if (text) {
            // Check if element contains only text or has child elements
            if (element.children.length === 0) {
                element.textContent = text;
            } else {
                // For elements with children (like links), update only text nodes
                updateTextContent(element, text);
            }
        }
    });
    
    // Save language preference
    localStorage.setItem('preferredLanguage', lang);
    
    // Add smooth transition effect
    document.body.style.opacity = '0.95';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 150);
}

function updateTextContent(element, newText) {
    // Get all child nodes
    const childNodes = Array.from(element.childNodes);
    
    // Find text nodes and update them
    let textUpdated = false;
    childNodes.forEach(node => {
        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
            node.textContent = newText;
            textUpdated = true;
        }
    });
    
    // If no text node found, just set textContent (will preserve some child elements)
    if (!textUpdated && element.children.length === 0) {
        element.textContent = newText;
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add scroll animation for elements
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all cards and sections
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.feature-card, .command-card, .step, .warning-box, .license-box');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Add parallax effect to header
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const header = document.querySelector('header');
    if (header) {
        header.style.transform = `translateY(${scrolled * 0.5}px)`;
        header.style.opacity = 1 - (scrolled / 500);
    }
});

// Copy code on click
document.addEventListener('DOMContentLoaded', () => {
    const codeBlocks = document.querySelectorAll('.step-content code');
    codeBlocks.forEach(code => {
        code.style.cursor = 'pointer';
        code.title = currentLang === 'ru' ? 'Нажмите, чтобы скопировать' : 'Click to copy';
        
        code.addEventListener('click', () => {
            const text = code.textContent;
            navigator.clipboard.writeText(text).then(() => {
                // Show feedback
                const originalBg = code.style.background;
                code.style.background = 'rgba(76, 175, 80, 0.3)';
                setTimeout(() => {
                    code.style.background = originalBg;
                }, 300);
            });
        });
    });
});

// Add hover effect to feature cards
document.addEventListener('DOMContentLoaded', () => {
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});

// Keyboard navigation for language switcher
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        switchLanguage(currentLang === 'ru' ? 'en' : 'ru');
    }
});
