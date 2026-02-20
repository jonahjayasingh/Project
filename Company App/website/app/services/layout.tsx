import React from "react";
import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Our Services",
    description: "Explore the services we offer",
};

export default function ServicesLayout({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
}
