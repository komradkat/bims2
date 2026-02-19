// BIMS Prototype Layout Injector

const topbarContent = `
<div class="flex flex-col min-h-screen">
  <!-- Topbar -->
  <div class="navbar bg-[#1e3a8a] text-white shadow-md z-30 h-16 shrink-0 px-4 justify-between">
      <!-- Left: Branding -->
      <div class="flex items-center gap-3">
          <!-- Mobile Toggle (visible only on small screens) -->
          <label for="my-drawer-2" class="btn btn-square btn-ghost btn-sm lg:hidden text-white mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
          </label>

          <!-- Logo Placeholder -->
          <div class="avatar placeholder">
              <div class="bg-[#6366f1] text-white rounded-lg w-10">
                  <span class="text-xl font-bold">B</span>
              </div>
          </div>
          
          <!-- Text -->
          <div class="leading-tight">
              <div class="font-bold text-lg">Barangay 53</div>
              <div class="text-xs opacity-80 font-light hidden sm:block">Barangay Information Management System</div>
          </div>
      </div>

      <!-- Right: User Profile -->
      <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-2 text-white">
              <div class="avatar placeholder">
                  <div class="bg-[#334155] text-white rounded-full w-8">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                          <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
                      </svg>
                  </div>
              </div>
              <span class="hidden sm:inline">admin</span>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4 opacity-70">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
          </div>
          <ul tabindex="0" class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52 text-base-content">
              <li><a>Profile</a></li>
              <li><a>Settings</a></li>
              <li><a class="text-error">Logout</a></li>
          </ul>
      </div>
  </div>

  <!-- Main Content Areas -->
  <div class="drawer lg:drawer-open flex-1 overflow-hidden">
    <input id="my-drawer-2" type="checkbox" class="drawer-toggle" />
    
    <div class="drawer-content flex flex-col bg-base-200 overflow-y-auto">
      <!-- Page Content -->
      <main class="flex-1 p-6" id="main-content">
          <!-- Content injected here or existing in DOM -->
      </main>
    </div> 
    
    <div class="drawer-side z-20">
      <label for="my-drawer-2" aria-label="close sidebar" class="drawer-overlay"></label> 
      <ul class="menu p-4 w-80 min-h-full bg-base-100 text-base-content border-r border-base-300">
        <!-- Sidebar Content -->
        <!-- Note: Branding moved to Topbar -->
        
        <li class="menu-title mt-2">Tier 1: Community</li>
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

        <li class="menu-title mt-4">Tier 2: Pro</li>
        <li><a href="business.html" class="${window.location.pathname.includes('business.html') ? 'active' : ''}">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
          Business Permits
        </a></li>
        <li><a href="blotter.html" class="${window.location.pathname.includes('blotter.html') ? 'active' : ''}">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" /></svg>
          Justice (Blotter)
        </a></li>
        <li><a href="finance.html" class="${window.location.pathname.includes('finance.html') ? 'active' : ''}">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
           Finance
        </a></li>

        <li class="menu-title mt-4">Tier 3: Ultra</li>
        <li><a href="audit_logs.html" class="${window.location.pathname.includes('audit_logs.html') ? 'active' : ''}">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
           Audit Logs
        </a></li>
        <li><a href="gis_map.html" class="${window.location.pathname.includes('gis_map.html') ? 'active' : ''}">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /></svg>
           GIS Map
        </a></li>
        
        <li class="mt-auto"></li>
        <li><a class="text-error">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          Logout
        </a></li>
      </ul>
    
    </div>
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
    appElement.innerHTML = topbarContent;

    // Inject original content into main area
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      mainContent.innerHTML = originalContent;
    }
  }
});
