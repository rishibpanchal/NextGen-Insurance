"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Activity, Database, Settings, HelpCircle, FileStack, Search } from "lucide-react";
import clsx from "clsx";

const navItems = [
  { name: "Executive Overview", href: "/", icon: LayoutDashboard },
  { name: "Individual Claim Analyzer", href: "/analyzer", icon: Search },
  { name: "Live API Simulator", href: "/simulator", icon: Activity },
  { name: "Batch Adjudication", href: "/batch", icon: FileStack },
  { name: "Full Database Ledger", href: "/database", icon: Database },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 min-h-screen p-6 flex flex-col gap-8 fixed border-r border-gray-300 border-opacity-30">
      <div className="flex items-center gap-3 px-2">
        <div className="w-8 h-8 rounded-lg neu-flat flex items-center justify-center text-primary font-bold">
          N
        </div>
        <div>
          <h1 className="font-bold text-lg text-gray-700 tracking-tight leading-tight">NexGen Risk</h1>
          <p className="text-[10px] text-gray-500 font-bold tracking-widest">ANALYTICS ENGINE</p>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <p className="text-xs font-bold text-gray-500 tracking-wider mb-2 ml-2">DASHBOARD</p>
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-medium text-sm",
                isActive ? "neu-pressed text-primary" : "text-gray-600 hover:text-gray-800"
              )}
            >
              <item.icon size={18} className={isActive ? "text-primary" : "text-gray-500"} />
              {item.name}
            </Link>
          );
        })}
      </div>

      <div className="mt-auto flex flex-col gap-2">
        <p className="text-xs font-bold text-gray-500 tracking-wider mb-2 ml-2">PREFERENCES</p>
        <button className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 hover:text-gray-800 font-medium text-sm transition-all text-left">
          <Settings size={18} className="text-gray-500" /> Organization
        </button>
        <button className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 hover:text-gray-800 font-medium text-sm transition-all text-left">
          <HelpCircle size={18} className="text-gray-500" /> Docs & Help
        </button>
      </div>
    </aside>
  );
}
