import ChatPage from './ChatPage';
import { NavigationProvider, useNavigation } from './context/NavigationContext';

function ModelsPage() {
  const { navigateTo } = useNavigation();
  const models = [
    {
      name: "G-VOXEL 4.0",
      description: "High-fidelity geometric reasoning unit. Optimized for structural analysis and voxel-based world generation.",
      version: "V.4.0.2-STABLE",
      latency: "12ms",
      status: "READY",
      statusColor: "text-primary",
      icon: "deployed_code",
      dots: [true, true, true, false],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuA7Cbow8w9o6EFEH0J9ZCWRfHP4ChCx3l_8IWBlo0CS7p9ehra87Mk8WQoJAwcHmDg8vpykBR3JRj4O_1CmRubhvHpEs5hasRCXd43Pkqtw6wYnHE2MFVroGT6MROMYPCAaDXRJPGE9iJ9N9_sTGez8WWc-TmuAe295SClHddFjnjaNk6VwNa4Ca0zqc9tWRbCytNXvKbdbSI2bCBbglASk4MPrzOU5WXSlA1JU9N0apT4AJo8-5vmV4idPr_s8nqtzGicHktCFHb4",
    },
    {
      name: "OBSIDIAN CORE",
      description: "Raw processing power for complex logic chains. The standard in encrypted neural computation and data mining.",
      version: "ULTRA-FAST",
      latency: "4ms",
      status: "READY",
      statusColor: "text-primary",
      icon: "terminal",
      dots: [true, true, true, true],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuAUQTPMhNheqrCCywFIrsXZuhtC0tnhHTbmz5DfSl7BxUBGeRf09JqeKgfEbwW3gmgoVdShg6A24ZQl2HhUi4qpgZVvHksRbfhV-xVrXw8wG15sRRO7-yLNVfcTq6W7UQxcUKk-sytYCwXyHQ1g7xHqLZiwwhMKtXfyR3TdKT7ANzsLpypaxA9agBg-ZxTKefTStAy2VirXhm-s2vi2cle75i2Jm1o-ml01bJFgVrZ0UwbV92nSJe5grxNzMsTkJ7hRhmNc-jGhxmI",
    },
    {
      name: "PIXEL BRAIN",
      description: "Creative-first architecture for narrative generation and stylistic translation. High entropy, low predictability.",
      version: "EXPERIMENTAL",
      latency: "45ms",
      status: "BOOTING",
      statusColor: "text-secondary",
      icon: "memory",
      dots: [true, true, false, false],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDs_mZKuiCvQNwQwTMAkbRNxjpQJW3eT5qWA1xZ8I7cGDt7oGDpHrnN0TINZpC6ndEWgsykrjeTYoACrlPxy2fs467q84VyXmIs0aspQQ0rfHtgjsLl0lstiWi8CFeJF84T4EoFqNogHY-mwI-KfVrK0az5Wc6rv45_ah1-mw_i2HRg8bRzB9Brdg-g7N1Ri1bpTpaqUZmER51VfDSxq1hwzzjFOEF3utQXbzP3WGE07V02Gn9tQqrZnd0MmiShkhRqe4YurcrGzU0",
    },
    {
      name: "VOID RUNNER",
      description: "Optimized for low-bandwidth environments. Reliable execution of basic directive sets without the bloat.",
      version: "LEGACY",
      latency: "8ms",
      status: "READY",
      statusColor: "text-primary",
      icon: "settings_input_component",
      dots: [true, false, false, false],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuCA-vAhor5RAvo0hUPPP_UFF7YIBIBRmYS6qcD-6fbY0ylciIaBtPCgLaYbQ601gK5AfSOVYKhj7DcH4Yy4YqfZICjRA1XpJPXlTfv-pgYS48u8KxTciZJqZcuf5oEGbAJ3ZktFT5NjB4FV077K6LEt-v45X_jHrTh9QiQFCQ6f4KpdrpIAfrNFQYrbPGd2of8Od4oUBQv37x8W82jVnttUn__yRtqRfmSualqYQGNwCfHLCoXXbzr4Wi7aAo1xhSFor3Xz-z3pc8I",
    },
    {
      name: "SPECTER v9",
      description: "Anonymized query processing unit. Ensures zero-knowledge retention for sensitive architectural sessions.",
      version: "SECURE",
      latency: "18ms",
      status: "READY",
      statusColor: "text-primary",
      icon: "security",
      dots: [true, true, true, false],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuB9Q17p5Cnfr7wEzSnpveCOx0Vyl9H-fapqcdLGc4wtoG0I-2Tx7yLB5cYMc03AF3OTHeIbOK1gM0blm51JFdjQ7CjrDEWi7EN_1bknVpueDdD3J-VgkpmWw2sEOJhxJMH4ZfP_P5AhJ07eGxju9bf4hyNKUgb4HlRmLDcLHmCykzVpB4zrHiIW8hduZbXER5awOgPQ6qcaIO3wmtIhNt75NdbZJpgpr5RlQfCh6NqTsgoz9ARZer7a9gHb97wgxjV0WQp0FWlArhM",
    },
    {
      name: "DATA SWARM",
      description: "Distributed intelligence network. Excels at multi-variable simulations and real-time environmental monitoring.",
      version: "PARALLEL",
      latency: "32ms",
      status: "OVERLOAD",
      statusColor: "text-error",
      icon: "hub",
      dots: [true, true, true, true],
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuB1OqNj-IanLPNuSViDTT9LYTD6DU_SHprKN858OO4ulmnyhPIW3VzYiarEcTlvbZyK1YNWF2pt2SMp3vXHzKn0h1qPB_UoyawIAKGWILVgi5hprGzPCYWj301ioiIB-0YG52rOLRXixj8PsEXsTeJtAOl7qi_bwcZQEKUaAMVPSbTb3u1qeRNhrua9Pv-MzGqMZ1TObxm2BlQmuZ0Byir1NaR5KinXipgoezN6jK-vic-ulyJJAYKZmZgL_YeNB2xIa2D1RJOxxPs",
    },
  ];

  return (
    <div className="min-h-screen bg-surface text-on-surface">
      {/* TopAppBar Shell */}
      <header className="fixed top-0 w-full z-50 h-16 bg-[#131313] shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)] flex justify-between items-center px-6">
        <div className="flex items-center gap-4">
          <span className="text-2xl font-black text-[#D97757] tracking-widest pixel-font uppercase">ELYSIUM</span>
        </div>
        <div className="flex items-center gap-6 h-full">
          <nav className="hidden md:flex h-full items-center gap-8">
            <button 
              onClick={() => navigateTo('chat')}
              className="pixel-font uppercase text-base tracking-tight text-[#353535] hover:bg-[#353535] transition-colors duration-75 px-2 py-1 active:translate-y-1"
            >
              CHATS
            </button>
            <button 
              onClick={() => navigateTo('models')}
              className="pixel-font uppercase text-base tracking-tight text-[#FFB59E] border-b-4 border-[#D97757] h-full flex items-center px-2 active:translate-y-1"
            >
              MODELS
            </button>
            <a className="pixel-font uppercase text-base tracking-tight text-[#353535] hover:bg-[#353535] transition-colors duration-75 px-2 py-1 active:translate-y-1" href="#">VOXELS</a>
            <a className="pixel-font uppercase text-base tracking-tight text-[#353535] hover:bg-[#353535] transition-colors duration-75 px-2 py-1 active:translate-y-1" href="#">ARCHIVE</a>
          </nav>
          <div className="flex items-center gap-2">
            <button className="p-2 text-[#D97757] hover:bg-[#353535] transition-colors duration-75 active:translate-y-1">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <button className="p-2 text-[#D97757] hover:bg-[#353535] transition-colors duration-75 active:translate-y-1">
              <span className="material-symbols-outlined">help</span>
            </button>
          </div>
        </div>
      </header>

      {/* SideNavBar Shell */}
      <aside className="h-screen w-64 fixed left-0 top-0 pt-16 bg-[#0E0E0E] flex flex-col hidden md:flex border-r-0 z-40">
        <div className="p-6 flex flex-col gap-1">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-surface-container-highest flex items-center justify-center border-2 border-primary-container">
              <span className="material-symbols-outlined text-primary">person</span>
            </div>
            <div>
              <div className="pixel-font text-base text-[#D97757] font-bold tracking-tight">OPERATOR_01</div>
              <div className="pixel-font text-xs text-on-surface-variant opacity-60">LEVEL 42</div>
            </div>
          </div>
          <button className="w-full bg-primary-container text-on-primary font-bold pixel-font py-3 px-4 flex items-center justify-center gap-2 active:scale-95 transition-transform mb-8">
            <span className="material-symbols-outlined text-sm">add</span>
            NEW_SESSION
          </button>
        </div>
        <nav className="flex flex-col flex-grow">
          <button 
            onClick={() => navigateTo('chat')}
            className="text-[#FFB59E]/60 flex items-center gap-3 p-4 pixel-font uppercase text-base tracking-tight hover:bg-[#353535] hover:text-[#FFB59E] transition-colors active:scale-95 text-left w-full"
          >
            <span className="material-symbols-outlined">chat</span>
            CHATS
          </button>
          <a className="bg-[#D97757] text-[#131313] font-bold flex items-center gap-3 p-4 pixel-font uppercase text-base tracking-tight active:scale-95" href="#">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>layers</span>
            MODELS
          </a>
          <a className="text-[#FFB59E]/60 flex items-center gap-3 p-4 pixel-font uppercase text-base tracking-tight hover:bg-[#353535] hover:text-[#FFB59E] transition-colors active:scale-95" href="#">
            <span className="material-symbols-outlined">grid_view</span>
            VOXELS
          </a>
          <a className="text-[#FFB59E]/60 flex items-center gap-3 p-4 pixel-font uppercase text-base tracking-tight hover:bg-[#353535] hover:text-[#FFB59E] transition-colors active:scale-95" href="#">
            <span className="material-symbols-outlined">inventory_2</span>
            ARCHIVE
          </a>
        </nav>
        <div className="mt-auto p-6 bg-surface-container-low">
          <div className="h-2 w-full bg-surface-container-highest mb-2">
            <div className="h-full bg-gradient-to-r from-primary-container to-primary w-3/4"></div>
          </div>
          <div className="flex justify-between pixel-font text-[10px] text-on-surface-variant">
            <span>SYSTEM STABILITY</span>
            <span>75%</span>
          </div>
        </div>
      </aside>

      {/* Main Content Canvas */}
      <main className="md:pl-64 pt-16 min-h-screen bg-[#131313]">
        <div className="max-w-7xl mx-auto p-8 lg:p-12">
          {/* Header Section */}
          <div className="mb-12">
            <h1 className="pixel-font text-5xl md:text-7xl font-bold uppercase tracking-tighter text-on-surface mb-4">
              Neural <span className="text-primary-container">Architectures</span>
            </h1>
            <p className="text-on-surface-variant max-w-2xl text-lg leading-relaxed opacity-80">
              Select a core processing unit for your current session. Each model features unique voxel-weighting algorithms and ethical constraints.
            </p>
          </div>

          {/* Search and Filter Bar */}
          <div className="mb-12 flex flex-col md:flex-row gap-4">
            <div className="flex-grow relative">
              <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-primary opacity-50">search</span>
              <input 
                className="w-full bg-surface-container-lowest border-none focus:ring-2 focus:ring-primary pixel-font py-4 pl-12 pr-4 text-primary uppercase placeholder:text-outline-variant/50" 
                placeholder="FILTER_MODELS_BY_IDENTIFIER..." 
                type="text"
              />
            </div>
            <div className="flex gap-2">
              <button className="bg-surface-container-highest px-6 py-4 pixel-font text-on-surface uppercase flex items-center gap-2 hover:bg-primary-container hover:text-on-primary transition-colors">
                <span className="material-symbols-outlined text-sm">tune</span>
                PARAMETERS
              </button>
              <button className="bg-surface-container-highest px-4 py-4 flex items-center justify-center hover:bg-primary-container hover:text-on-primary transition-colors">
                <span className="material-symbols-outlined">sort</span>
              </button>
            </div>
          </div>

          {/* Models Bento Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {models.map((model, index) => (
              <div 
                key={index}
                className="group bg-surface-container-low flex flex-col h-full border-b-4 border-transparent hover:border-primary-container transition-all cursor-pointer"
              >
                <div className="h-48 bg-surface-container-highest relative overflow-hidden">
                  <img 
                    alt={`${model.name} Interface`} 
                    className="w-full h-full object-cover grayscale opacity-40 group-hover:grayscale-0 group-hover:opacity-60 transition-all duration-500" 
                    src={model.image}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-surface-container-low to-transparent"></div>
                  <div className="absolute bottom-4 left-4">
                    <span className={`${model.version === "EXPERIMENTAL" || model.version === "SECURE" ? "bg-surface-container-highest text-on-surface" : "bg-primary-container text-on-primary"} pixel-font px-2 py-1 text-xs`}>
                      {model.version}
                    </span>
                  </div>
                </div>
                <div className="p-6 flex flex-col flex-grow">
                  <div className="flex justify-between items-start mb-4">
                    <span className="material-symbols-outlined text-primary text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>{model.icon}</span>
                    <div className="flex gap-1">
                      {model.dots.map((filled, i) => (
                        <span 
                          key={i} 
                          className={`w-2 h-2 ${filled ? "bg-primary" : "bg-surface-container-highest"}`}
                        ></span>
                      ))}
                    </div>
                  </div>
                  <h3 className="pixel-font text-2xl font-bold uppercase text-on-surface mb-2">{model.name}</h3>
                  <p className="text-on-surface-variant pixel-font text-sm leading-snug mb-6 flex-grow">
                    {model.description}
                  </p>
                  <div className="flex items-center justify-between mt-auto pt-4 border-t border-outline-variant/20">
                    <span className="pixel-font text-xs text-outline">LATENCY: {model.latency}</span>
                    <span className={`pixel-font text-xs font-bold ${model.statusColor}`}>{model.status}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Contextual FAB (Only for main screens) */}
      <button className="fixed bottom-8 right-8 w-16 h-16 bg-[#D97757] text-[#131313] shadow-[4px_4px_0px_0px_rgba(0,0,0,0.3)] flex items-center justify-center active:scale-95 transition-transform z-50 hover:opacity-90">
        <span className="material-symbols-outlined text-4xl">add</span>
      </button>
    </div>
  );
}

function AppContent() {
  const { currentPage } = useNavigation();

  return (
    <>
      {currentPage === 'chat' ? (
        <ChatPage />
      ) : (
        <ModelsPage />
      )}
    </>
  );
}

function App() {
  return (
    <NavigationProvider>
      <AppContent />
    </NavigationProvider>
  );
}

export default App;
