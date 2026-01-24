// BIMS Prototype Layout Injector

const appName = "BIMS Pro";

const sidebarContent = `
<div class="drawer lg:drawer-open">
  <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col bg-base-200 min-h-screen">
    <!-- Navbar -->
    <div class="w-full navbar bg-base-100 lg:hidden shadow-sm">
      <div class="flex-none">
        <label for="my-drawer-2" class="btn btn-square btn-ghost">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </label>
      </div>
      <div class="flex-1 px-2 mx-2 text-xl font-bold tracking-tighter">${appName}</div>
    </div>
    
    <!-- Page Content -->
    <main class="flex-1 p-6" id="main-content">
        <!-- Content injected here or existing in DOM -->
    </main>
  </div> 
  
  <div class="drawer-side z-20">
    <label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label> 
    <ul class="menu p-4 w-80 min-h-full bg-base-100 text-base-content border-r border-base-300">
      <!-- Sidebar Content -->
      <li class="mb-4">
        <div class="flex items-center gap-3 px-2">
            <div class="avatar placeholder">
              <div class="bg-primary text-primary-content rounded-full w-10">
                <span class="text-xl">B</span>
              </div>
            </div>
            <div>
                <h2 class="font-bold text-lg leading-tight">Barangay 143</h2>
                <p class="text-xs text-base-content/60 uppercase tracking-wider font-semibold">System v2.0</p>
            </div>
        </div>
      </li>
      
      <li class="menu-title mt-2">Core</li>
      <li><a href="index.html" class="${window.location.pathname.includes('index.html') ? 'active' : ''}">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
        Dashboard
      </a></li>
      <li><a href="residents.html" class="${window.location.pathname.includes('residents.html') ? 'active' : ''}">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
        Residents
      </a></li>
      <li><a href="certificates.html" class="${window.location.pathname.includes('certificates.html') ? 'active' : ''}">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
        Certificates
      </a></li>

      <li class="menu-title mt-4">Pro & Ultra</li>
      <li><a href="business.html" class="${window.location.pathname.includes('business.html') ? 'active' : ''}">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
        Business Permits
      </a></li>
      <li><a href="blotter.html" class="${window.location.pathname.includes('blotter.html') ? 'active' : ''}">
         <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>
        Justice (Blotter)
      </a></li>
      
      <li class="mt-auto"></li>
      <li><a class="text-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
        Logout
      </a></li>
    </ul>
  
  </div>
</div>
`;

// Inject layout
document.addEventListener('DOMContentLoaded', () => {
    const appElement = document.getElementById('app');
    if (appElement) {
        // Save original content
        const originalContent = appElement.innerHTML;
        
        // Overwrite with sidebar structure
        appElement.innerHTML = sidebarContent;
        
        // Inject original content into main area
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = originalContent;
        }
    }
});
