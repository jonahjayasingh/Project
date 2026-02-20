import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ message: "Logged out" });

  response.cookies.set({
    name: "token",
    value: "",
    maxAge: 0,
    path: "/",
    httpOnly: true,
  });
  response.cookies.set({
    name: "role",
    value: "",
    maxAge: 0,
    path: "/",
    httpOnly: true,
  });

  return response;
}
