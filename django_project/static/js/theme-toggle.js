/**
 * Theme Toggle - Light/Dark Theme Switcher
 * Uses jQuery for DOM manipulation and localStorage for persistence
 */

(function($) {
    'use strict';

    // Theme configuration
    var STORAGE_KEY = 'theme';
    var THEME_LIGHT = 'light';
    var THEME_DARK = 'dark';

    /**
     * Get the current theme preference
     * Priority: localStorage > system preference > default (light)
     */
    function getTheme() {
        var stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            return stored;
        }
        
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return THEME_DARK;
        }
        
        return THEME_LIGHT;
    }

    /**
     * Apply theme to the document
     */
    function applyTheme(theme) {
        if (theme === THEME_DARK) {
            $('html').attr('data-theme', THEME_DARK);
        } else {
            $('html').attr('data-theme', THEME_LIGHT);
        }
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        var currentTheme = getTheme();
        var newTheme = (currentTheme === THEME_LIGHT) ? THEME_DARK : THEME_LIGHT;
        
        localStorage.setItem(STORAGE_KEY, newTheme);
        applyTheme(newTheme);
        updateToggleButton(newTheme);
        
        return newTheme;
    }

    /**
     * Update the toggle button icon and text
     */
    function updateToggleButton(theme) {
        var $btn = $('.theme-toggle');
        var $icon = $btn.find('.icon');
        
        if (theme === THEME_DARK) {
            $icon.text('☀️'); // Sun for dark mode (switch to light)
            $btn.attr('title', 'Switch to light mode');
        } else {
            $icon.text('🌙'); // Moon for light mode (switch to dark)
            $btn.attr('title', 'Switch to dark mode');
        }
    }

    /**
     * Initialize the theme toggle
     */
    function init() {
        var currentTheme = getTheme();
        applyTheme(currentTheme);
        
        // Create and append toggle button if it doesn't exist
        if (!$('.theme-toggle').length) {
            var $toggleBtn = $('<button type="button" class="theme-toggle">' +
                '<span class="icon"></span>' +
                '</button>');
            
            // Insert into nav-right
            $('.nav-right').prepend($toggleBtn);
        }
        
        updateToggleButton(currentTheme);
        
        // Bind click event
        $(document).on('click', '.theme-toggle', function(e) {
            e.preventDefault();
            toggleTheme();
        });

        // Listen for system theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
                // Only auto-switch if user hasn't set a preference
                if (!localStorage.getItem(STORAGE_KEY)) {
                    applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
                    updateToggleButton(e.matches ? THEME_DARK : THEME_LIGHT);
                }
            });
        }
    }

    // Initialize on DOM ready
    $(document).ready(function() {
        init();
    });

})(jQuery);