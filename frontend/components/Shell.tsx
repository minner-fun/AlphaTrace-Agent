import Link from "next/link";
import { Bot, FilePlus2, UserRoundCheck } from "lucide-react";

import { WalletButton } from "@/components/WalletButton";

const navItems = [
  { href: "/", label: "Console", icon: Bot },
  { href: "/create-job", label: "Create", icon: FilePlus2 },
  { href: "/agent", label: "Agent", icon: UserRoundCheck },
];

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-paper text-ink">
      <header className="border-b border-ink/10 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-ink text-paper">
              <Bot size={22} />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-moss">AlphaTrace</p>
              <p className="text-xs text-ink/60">ERC-8004 market intelligence agent</p>
            </div>
          </Link>
          <nav className="hidden items-center gap-2 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-ink/70 hover:bg-mint hover:text-ink"
              >
                <item.icon size={16} />
                {item.label}
              </Link>
            ))}
          </nav>
          <WalletButton />
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
    </div>
  );
}

