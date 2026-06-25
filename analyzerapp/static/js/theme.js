(function () {
    const STORAGE_KEY = 'resumeAnalyzerTheme';

    function getInitialTheme() {
        const savedTheme = localStorage.getItem(STORAGE_KEY);
        if (savedTheme === 'dark' || savedTheme === 'light') {
            return savedTheme;
        }
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (document.body) {
            document.body.setAttribute('data-theme', theme);
        }

        document.querySelectorAll('.theme-toggle').forEach(function (toggle) {
            toggle.textContent = '';
            toggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
            toggle.setAttribute('title', theme === 'dark' ? 'Light theme' : 'Dark theme');
        });
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, nextTheme);
        applyTheme(nextTheme);
    }

    function initThemeToggle() {
        if (!document.querySelector('.theme-toggle')) {
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'theme-toggle';
            document.body.appendChild(toggle);
        }

        document.querySelectorAll('.theme-toggle').forEach(function (toggle) {
            if (!toggle.dataset.themeBound) {
                toggle.dataset.themeBound = 'true';
                toggle.addEventListener('click', toggleTheme);
            }
        });

        applyTheme(getInitialTheme());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initThemeToggle);
    } else {
        initThemeToggle();
    }
})();

