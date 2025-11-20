"use client";

import * as React from "react";

export function Dialog({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

export function DialogTrigger({ asChild, children }: { asChild?: boolean; children: React.ReactNode }) {
  return <>{children}</>;
}

export function DialogContent({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={className}>
      {children}
    </div>
  );
}

export function DialogHeader({
  children
}: {
  children: React.ReactNode;
}) {
  return <div>{children}</div>;
}

export function DialogTitle({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <h2 className={className}>{children}</h2>;
}

export function DialogDescription({
  className,
  children
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <p className={className}>{children}</p>;
}
