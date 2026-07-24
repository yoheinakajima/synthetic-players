import { Link, useLocation } from 'wouter';
import { 
  Sidebar, 
  SidebarContent, 
  SidebarFooter, 
  SidebarGroup, 
  SidebarGroupContent, 
  SidebarGroupLabel, 
  SidebarHeader, 
  SidebarMenu, 
  SidebarMenuButton, 
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger
} from '@/components/ui/sidebar';
import { 
  Network, 
  BookOpen, 
  Dna, 
  Microscope,
  FileText,
  Menu
} from 'lucide-react';
import React from 'react';

const mainNavigation = [
  { name: 'Dashboard', path: '/', icon: Network },
  { name: 'Game Catalog', path: '/games', icon: BookOpen },
  { name: 'Experiments', path: '/experiments', icon: Microscope },
  { name: 'Research Claims', path: '/claims', icon: Dna },
  { name: 'Papers', path: '/papers', icon: FileText },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full font-sans bg-background">
        <Sidebar className="border-r border-border">
          <SidebarHeader className="border-b border-border py-4 px-4 bg-card">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-primary flex items-center justify-center shadow-sm">
                <Network className="w-4 h-4 text-primary-foreground" />
              </div>
              <div>
                <h1 className="font-serif font-semibold text-base leading-tight tracking-tight text-foreground">
                  Game Theory
                </h1>
                <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-mono">
                  Research Lab
                </p>
              </div>
            </Link>
          </SidebarHeader>

          <SidebarContent className="bg-card">
            <SidebarGroup>
              <SidebarGroupLabel className="font-mono text-xs uppercase text-muted-foreground tracking-wider mb-2">
                Core
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {mainNavigation.map((item) => (
                    <SidebarMenuItem key={item.name}>
                      <SidebarMenuButton 
                        asChild
                        isActive={location === item.path || (item.path !== '/' && location.startsWith(item.path))}
                      >
                        <Link href={item.path} className="flex items-center gap-3">
                          <item.icon className="w-4 h-4 opacity-75" />
                          <span className="font-medium text-sm">{item.name}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <SidebarFooter className="border-t border-border p-4 bg-card">
            <div className="text-[10px] text-muted-foreground font-mono">
              SYSTEM STATUS: ONLINE
              <br/>
              DB: CONNECTED
            </div>
          </SidebarFooter>
        </Sidebar>

        <main className="flex-1 flex flex-col min-w-0">
          <header className="h-14 border-b border-border bg-card flex items-center px-4 md:px-6 sticky top-0 z-10">
            <SidebarTrigger className="mr-4 md:hidden" />
            <div className="flex-1" />
            {/* Optional Top Right actions */}
          </header>
          <div className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
