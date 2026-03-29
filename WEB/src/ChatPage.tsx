import { useState, useRef, useEffect } from 'react';
import { sendMessage, generateId, getCurrentTimestamp } from './api/elysiumApi';
import type { ChatMessage } from './api/elysiumApi';
import { useNavigation } from './context/NavigationContext';

function ChatPage() {
  const { navigateTo } = useNavigation();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'initial',
      role: 'assistant',
      content: 'SYSTEM_INITIALIZED. WELCOME BACK OPERATOR_01. HOW CAN I ASSIST YOU TODAY?',
      timestamp: getCurrentTimestamp()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      const tagName = target.tagName.toLowerCase();
      
      if (tagName === 'textarea' || tagName === 'input' || tagName === 'button' || tagName === 'a') {
        return;
      }
      
      if (e.key === 'Enter' || e.key === 'Shift' || e.key === 'Control' || e.key === 'Alt' || e.key === 'Meta') {
        return;
      }
      
      inputRef.current?.focus();
    };

    document.addEventListener('keydown', handleGlobalKeyDown);
    return () => document.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: getCurrentTimestamp()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await sendMessage(userMessage.content);
      
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: response,
        timestamp: getCurrentTimestamp()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `ERROR: CONNECTION_FAILED. UNABLE TO REACH ELYSIUM CORE. ${error instanceof Error ? error.message : 'UNKNOWN_ERROR'}`,
        timestamp: getCurrentTimestamp()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
      setHistoryIndex(-1);
      return;
    }

    const userMessages = messages.filter(m => m.role === 'user');

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (userMessages.length === 0) return;

      const newIndex = historyIndex === -1 ? 0 : Math.min(historyIndex + 1, userMessages.length - 1);
      setHistoryIndex(newIndex);
      setInputValue(userMessages[userMessages.length - 1 - newIndex].content);
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (historyIndex === -1) return;

      const newIndex = historyIndex - 1;
      if (newIndex < 0) {
        setHistoryIndex(-1);
        setInputValue('');
      } else {
        setHistoryIndex(newIndex);
        setInputValue(userMessages[userMessages.length - 1 - newIndex].content);
      }
    }
  };

  return (
    <div className="min-h-screen bg-surface-container-lowest text-on-surface overflow-hidden">
      {/* TopNavBar */}
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-6 h-20 bg-[#131313] backdrop-blur-xl bg-opacity-80">
        <div className="flex items-center gap-4">
          <span className="text-[#D97757] text-2xl font-['VT323'] tracking-widest uppercase">ELYSIUM</span>
        </div>
        <div className="flex items-center gap-6">
          <button className="hover:bg-[#2a2a2a] transition-colors duration-200 p-2 active:scale-95">
            <span className="material-symbols-outlined text-[#B1B6B4]">settings</span>
          </button>
          <button className="hover:bg-[#2a2a2a] transition-colors duration-200 p-2 active:scale-95">
            <span className="material-symbols-outlined text-[#B1B6B4]">help_outline</span>
          </button>
          <div className="w-10 h-10 bg-surface-container-highest flex items-center justify-center">
            <img alt="User" className="w-full h-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuC8oim8kFbtlSOmAhe-HTqUqo87rK_RL42GEIfCb-qTVxP1FmSAY2dvUauqpvz6t4Y56PQJTkNOCyC_CH4CQt9FHQdP-wB4YXnYvr8btWuTPIFigMo7kxvgctmjEyML9XOsPQzDY7bEZElyETa4k1J4xY5-p2b6xZG1pCUOzjsgZuD_2BG2C7UIa6b8rUoWzDo9ZEdABqgsmSdYfANlQI8vwEoSpDB4hqdD3cRVa6es7o9BvJqbwnWehzPYJaVPAcZSzyo2s-l9KKQ" />
          </div>
        </div>
      </header>

      {/* SideNavBar */}
      <aside className="h-screen w-64 fixed left-0 top-0 bg-[#0e0e0e] flex flex-col py-6 z-40">
        <div className="px-6 mb-8 pt-16">
          <div className="text-xl font-['VT323'] text-[#D97757]">ELYSIUM</div>
          <div className="text-xs font-['VT323'] text-[#B1B6B4] tracking-wider uppercase">VER_1.0.4</div>
        </div>
        <nav className="flex flex-col flex-grow">
          <a className="flex items-center gap-3 bg-[#2a2a2a] text-[#ffb59e] px-4 py-3 border-l-4 border-[#D97757] font-['VT323'] text-sm tracking-wider uppercase active:scale-95 transition-transform" href="#">
            <span className="material-symbols-outlined">chat</span>
            <span>CHATS</span>
          </a>
          <button 
            onClick={() => navigateTo('models')}
            className="flex items-center gap-3 text-[#353534] px-4 py-3 hover:bg-[#131313] hover:text-[#e5e2e1] font-['VT323'] text-sm tracking-wider uppercase active:scale-95 transition-transform text-left w-full"
          >
            <span className="material-symbols-outlined">model_training</span>
            <span>MODELS</span>
          </button>
          <a className="flex items-center gap-3 text-[#353534] px-4 py-3 hover:bg-[#131313] hover:text-[#e5e2e1] font-['VT323'] text-sm tracking-wider uppercase active:scale-95 transition-transform" href="#">
            <span className="material-symbols-outlined">layers</span>
            <span>VOXELS</span>
          </a>
          <a className="flex items-center gap-3 text-[#353534] px-4 py-3 hover:bg-[#131313] hover:text-[#e5e2e1] font-['VT323'] text-sm tracking-wider uppercase active:scale-95 transition-transform" href="#">
            <span className="material-symbols-outlined">inventory_2</span>
            <span>ARCHIVE</span>
          </a>
        </nav>
        <div className="px-4 mt-auto">
          <button 
            onClick={() => setMessages([{
              id: 'initial',
              role: 'assistant',
              content: 'NEW_SESSION_INITIALIZED. AWAITING YOUR INSTRUCTIONS.',
              timestamp: getCurrentTimestamp()
            }])}
            className="w-full bg-primary-container text-on-primary py-4 pixel-font text-xl font-bold border-b-4 border-on-primary-fixed-variant hover:bg-primary transition-colors active:translate-y-1"
          >
            NEW SESSION
          </button>
        </div>
      </aside>

      {/* Main Content Canvas */}
      <main className="ml-64 pt-20 h-screen relative bg-surface overflow-hidden">
        {/* Chat Area */}
        <div ref={chatContainerRef} className="h-full overflow-y-auto px-8 py-10 pb-40 flex flex-col gap-8">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`flex gap-6 max-w-4xl ${message.role === 'user' ? 'self-end flex-row-reverse' : ''}`}
            >
              <div className={`flex-shrink-0 w-12 h-12 flex items-center justify-center ${
                message.role === 'user' ? 'bg-surface-container-highest' : 'bg-primary-container'
              }`}>
                <span 
                  className={`material-symbols-outlined ${message.role === 'user' ? 'text-primary' : 'text-on-primary'}`}
                  style={message.role === 'assistant' ? { fontVariationSettings: "'FILL' 1" } : undefined}
                >
                  {message.role === 'user' ? 'person' : 'smart_toy'}
                </span>
              </div>
              <div className={`flex flex-col gap-2 ${message.role === 'user' ? 'items-end' : ''}`}>
                <div className={`p-6 ${
                  message.role === 'user' 
                    ? 'bg-surface-container-highest shadow-[-4px_4px_0px_0px_rgba(255,181,158,0.1)]' 
                    : 'bg-surface-container-low shadow-[4px_4px_0px_0px_rgba(217,119,87,0.1)]'
                }`}>
                  <p className={`pixel-font text-xl leading-relaxed ${
                    message.role === 'user' ? 'text-primary' : 'text-on-surface'
                  }`}>
                    {message.content}
                  </p>
                </div>
                <span className="pixel-font text-xs text-on-surface-variant">
                  {message.role === 'user' ? 'SENT' : 'RECEIVED'} {message.timestamp}
                </span>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-6 max-w-4xl">
              <div className="flex-shrink-0 w-12 h-12 bg-primary-container flex items-center justify-center">
                <span className="material-symbols-outlined text-on-primary animate-pulse" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
              </div>
              <div className="bg-surface-container-low p-6 shadow-[4px_4px_0px_0px_rgba(217,119,87,0.1)]">
                <p className="pixel-font text-xl leading-relaxed text-on-surface-variant animate-pulse">
                  PROCESSING...
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Input Section - Merged with Chat */}
        <div className="absolute bottom-0 left-0 right-0">
          <div className="h-40 bg-gradient-to-t from-surface via-surface to-transparent"></div>
          <div className="absolute bottom-0 left-0 right-0 px-8 pb-6">
            <div className="max-w-5xl mx-auto flex gap-4 items-start">
              <div className="flex-grow relative">
                <textarea 
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value);
                    setHistoryIndex(-1);
                  }}
                  onKeyDown={handleKeyDown}
                  className="w-full bg-surface-container-low text-primary pixel-font text-xl p-6 border-0 focus:ring-0 resize-none h-20 placeholder:text-outline-variant focus:border-primary transition-all" 
                  placeholder="TERMINAL_INPUT://_"
                  disabled={isLoading}
                ></textarea>
                <div className="absolute bottom-4 right-4 flex gap-4">
                  <button className="text-on-surface-variant hover:text-primary">
                    <span className="material-symbols-outlined">attach_file</span>
                  </button>
                  <button className="text-on-surface-variant hover:text-primary">
                    <span className="material-symbols-outlined">mic</span>
                  </button>
                </div>
              </div>
              <button 
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                className="bg-primary-container text-on-primary h-14 w-20 flex items-center justify-center hover:bg-primary transition-colors group active:translate-y-1 mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="material-symbols-outlined text-3xl group-hover:scale-110 transition-transform" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default ChatPage;
