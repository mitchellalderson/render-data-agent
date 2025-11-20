"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type AccordionContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
};

const AccordionContext = React.createContext<AccordionContextValue | null>(null);

export function Accordion({
  children
}: {
  type?: "single";
  collapsible?: boolean;
  className?: string;
  children: React.ReactNode;
}) {
  const [open, setOpen] = React.useState(true);
  return (
    <AccordionContext.Provider value={{ open, setOpen }}>
      <div>{children}</div>
    </AccordionContext.Provider>
  );
}

export function AccordionItem({
  className,
  children
}: {
  value: string;
  className?: string;
  children: React.ReactNode;
}) {
  return <div className={cn("rounded-md border", className)}>{children}</div>;
}

export function AccordionTrigger({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  const ctx = React.useContext(AccordionContext);
  if (!ctx) return null;
  return (
    <button
      type="button"
      className={cn("flex w-full items-center justify-between", className)}
      onClick={() => ctx.setOpen(!ctx.open)}
    >
      {children}
    </button>
  );
}

export function AccordionContent({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  const ctx = React.useContext(AccordionContext);
  if (!ctx) return null;
  if (!ctx.open) return null;
  return <div className={cn(className)}>{children}</div>;
}
