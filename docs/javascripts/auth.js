// auth.js - Client-side authentication script for Supabase
(function() {
  // Wait for DOM to be loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the login page
    if (!document.getElementById('loginForm')) {
      return;
    }

    // Import Supabase client dynamically
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.x/dist/browser/supabase.js';
    script.onload = function() {
      initializeAuth();
    };
    document.head.appendChild(script);
  });

  function initializeAuth() {
    // Get Supabase configuration from environment variables injected by Vercel
    const supabaseUrl = window.SUPABASE_URL || '%%SUPABASE_URL%%';
    const supabaseKey = window.SUPABASE_ANON_KEY || '%%SUPABASE_ANON_KEY%%';

    // Validate configuration
    if (!supabaseUrl || !supabaseKey || supabaseUrl === '%%SUPABASE_URL%%' || supabaseKey === '%%SUPABASE_ANON_KEY%%') {
      console.error('Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables in Vercel.');
      return;
    }

    // Initialize Supabase client
    const supabase = supabaseJs.createClient(supabaseUrl, supabaseKey);

    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('error-message');

    // Handle form submission
    if (loginForm) {
      loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        // Basic validation
        if (!email || !password) {
          showError('Por favor completa todos los campos.');
          return;
        }

        try {
          // Show loading state
          const submitButton = loginForm.querySelector('button[type="submit"]');
          const originalText = submitButton.textContent;
          submitButton.textContent = 'Iniciando sesión...';
          submitButton.disabled = true;

          // Attempt to sign in
          const { data, error } = await supabase.auth.signInWithPassword({
            email: email,
            password: password
          });

          // Reset button state
          submitButton.textContent = originalText;
          submitButton.disabled = false;

          if (error) {
            throw new Error(error.message);
          }

          // Extract access token and store in cookie
          const accessToken = data.session.access_token;

          // Create secure cookie with access token
          document.cookie = `sb-access-token=${accessToken}; path=/; max-age=3600; SameSite=Lax; Secure`;

          // Redirect to home page
          window.location.href = '/';

        } catch (err) {
          console.error('Authentication error:', err);
          showError('Credenciales inválidas. Por favor verifica tu correo y contraseña.');
        }
      });
    }

    function showError(message) {
      if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        // Clear error after 5 seconds
        setTimeout(() => {
          errorMessage.style.display = 'none';
        }, 5000);
      }
    }
  }

  // Check authentication status on page load (for protected pages)
  document.addEventListener('DOMContentLoaded', function() {
    // Skip check on login page
    if (window.location.pathname.includes('/login')) {
      return;
    }

    // Check for access token cookie
    const cookies = document.cookie.split(';').map(cookie => cookie.trim());
    const hasAccessToken = cookies.some(cookie => cookie.startsWith('sb-access-token='));

    // If no access token and not on home page, redirect to login
    if (!hasAccessToken && window.location.pathname !== '/') {
      // Only redirect if we're trying to access protected content
      const protectedPaths = ['/notebook_', '/chapter', '/capitulo'];
      const isProtected = protectedPaths.some(path => window.location.pathname.startsWith(path));

      if (isProtected) {
        window.location.href = '/login';
      }
    }
  });
})();