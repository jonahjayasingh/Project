"use client";
import { createContext, useContext } from "react";

export const RefreshContext = createContext<number>(0);
export const useRefresh = () => useContext(RefreshContext);
