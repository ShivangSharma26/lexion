import React from 'react';
import { Cpu } from 'lucide-react';

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full bg-black/40 backdrop-blur-md border-b border-white/10 animate-in fade-in slide-in-from-top-4 duration-700">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20">
            <Cpu className="w-6 h-6 text-primary" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            Lexion <span className="text-xs px-2 py-1 rounded-full bg-white/10 text-gray-300 font-medium">Doc AI</span>
          </h1>
        </div>
        <nav>
          <a href="#" className="text-sm font-medium text-gray-400 hover:text-white transition-colors">
            Documentation
          </a>
        </nav>
      </div>
    </header>
  );
}
