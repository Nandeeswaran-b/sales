// Supabase Configuration
// Replace with your actual Supabase URL and Anon Key
const SUPABASE_URL = 'https://ngarllhydgplgyqttkwp.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5nYXJsbGh5ZGdwbGd5cXR0a3dwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4NzY3NTUsImV4cCI6MjA5MTQ1Mjc1NX0.d9bXKhweT6GSiX8mui2FZ6JQyPUaQsNDa5TuF0HZCfY';

// Initialize Supabase Client
const _supabase = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Export for use in other scripts
window.supabaseClient = _supabase;
