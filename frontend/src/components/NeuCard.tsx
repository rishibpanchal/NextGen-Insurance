import clsx from "clsx";
import React from "react";

interface NeuCardProps {
  children: React.ReactNode;
  className?: string;
  type?: "flat" | "pressed" | "convex" | "concave";
}

export default function NeuCard({ children, className, type = "flat" }: NeuCardProps) {
  const typeClass = {
    flat: "neu-flat",
    pressed: "neu-pressed",
    convex: "neu-convex",
    concave: "neu-concave",
  }[type];

  return (
    <div className={clsx(typeClass, "p-6", className)}>
      {children}
    </div>
  );
}
